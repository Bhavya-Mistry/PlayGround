from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
import httpx
from groq import AsyncGroq
from database import SessionLocal, Review, init_db
from icecream import ic

load_dotenv()

init_db()

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Hello, this is my project, you are not meant to see this but if you end up here then let me know ;)"
    }


@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    action = payload.get("action")
    if action == "opened":
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})
        pr_number = pr.get("number")
        repo_name = repo.get("full_name")

        # print(f"New PR {pr_number} opened in {repo_name}")
        ic(pr_number, repo_name)

        token = os.getenv("GITHUB_TOKEN")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff",
        }

        diff_url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"

        async with httpx.AsyncClient() as client:
            response = await client.get(diff_url, headers=headers)

            if response.status_code == 200:
                diff_text = response.text
                print("-------------Diff received-------------")
                # print(diff_text)
                ic(diff_text)
                print("---------------------------------------")
            else:
                # print(f"error fetching diff:{response.status_code}")
                ic("Error fetching the difference", response.status_code)

            ai_client = AsyncGroq()
            system_prompt = """You are a senior code review engineer. 
            Analyze the following code diff. 
            Focus on: 
            1. Security vulnerabilities (SQL injection, secrets, etc).
            2. Performance issues (n+1 queries, expensive loops).
            3. Code style and best practices.
            
            Provide your feedback in a concise bullet-point list.
            """

            if response.status_code == 200:
                # print("Analyzing code with AI...")
                ic("Analyzing code with AI...")

                chat_completion = await ai_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": f"Here is the git diff to review:\n\n{diff_text}",
                        },
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.2,
                )

                review_content = chat_completion.choices[0].message.content

                print("----------------------AI review----------------------\n\n")
                # print(review_content)
                ic(review_content)
                print("-----------------------------------------------------")

                comment_url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
                comment_payload = {"body": review_content}
                comment_headers = {"Authorization": f"Bearer {token}"}
                comment_response = await client.post(
                    comment_url, json=comment_payload, headers=comment_headers
                )

                # print(f"Comment posted status: {comment_response.status_code}")
                ic("comment posted status", comment_response.status_code)

                db = SessionLocal()

                try:
                    new_review = Review(
                        repo_name=repo_name,
                        pr_number=pr_number,
                        ai_feedback=review_content,
                    )

                    db.add(new_review)

                    db.commit()
                    ic("Review successfully saved to database!")

                except Exception as e:
                    ic("Failed to save in db", e)
                    db.rollback()

                finally:
                    db.close()

    return {"status": "ok"}
