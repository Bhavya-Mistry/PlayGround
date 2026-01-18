from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
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

        print(f"New PR {pr_number} opened in {repo_name}")

        token = os.getenv("GITHUB_TOKEN")

        headers = {
            "Authorization": f"Bear {token}",
            "Accept": "application/vnd.github.v3.diff",
        }

        diff_url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"

        async with httpx.AsyncClient() as client:
            response = await client.get(diff_url, headers=headers)

            if response.status_code == 200:
                diff_text = response.text
                print("-------------Diff received-------------")
                print(diff_text)
                print("---------------------------------------")
            else:
                print(f"error fetching diff:{response.status_code}")
    return {"status": "ok"}
