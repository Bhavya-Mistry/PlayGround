from fastapi import FastAPI, Request, HTTPException, Header
from dotenv import load_dotenv
from groq import AsyncGroq
from database import SessionLocal, Review, init_db, ReviewResponse
from icecream import ic
import hmac
import hashlib
import httpx
import os
from typing import List
import base64
import re
# from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

init_db()

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins (for development)
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allows all headers
# )


async def verify_signature(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=403, detail="Missing signature")

    body = await request.body()

    secret = os.getenv("GITHUB_WEBHOOK_SECRET")

    expected_signature = (
        "sha256="
        + hmac.new(key=secret.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()
    )

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    return True


async def create_branch(repo_name, source_sha, new_branch_name, token):
    """
    Creates a new branch in the repo.

    Args:
        repo_name: "owner/repo"
        source_sha: The Commit ID we are copying FROM.
        new_branch_name: The name of the new branch (e.g., "devguard-fix-1").
        token: Your GitHub PAT.
    """

    # 1. The API Endpoint for Git References
    url = f"https://api.github.com/repos/{repo_name}/git/refs"

    # 2. Standard Headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # 3. The Payload (The "Clone" Instruction)
    # GitHub strictly requires the 'ref' to start with 'refs/heads/'
    data = {"ref": f"refs/heads/{new_branch_name}", "sha": source_sha}

    # 4. Send the Request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers)

            # 201 Created means success
            if response.status_code == 201:
                print(f"✅ Branch '{new_branch_name}' created successfully!")
                return True
            else:
                print(f"❌ Failed to create branch: {response.text}")
                return False

        except Exception as e:
            print(f"Error creating branch: {e}")
            return False


async def update_file(repo_name, file_path, new_content, branch_name, token):
    """
    Commits a file update to a specific branch.

    Args:
        repo_name: "owner/repo"
        file_path: "src/login.py"
        new_content: The actual Python code (text).
        branch_name: The branch we are updating (e.g., "devguard-fix-1").
        token: Your GitHub PAT.
    """

    # The API URL for file contents
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        # --- STEP 1: Get the current file's SHA ---
        # We need to tell GitHub *which* branch to look in (?ref=...)
        get_response = await client.get(f"{url}?ref={branch_name}", headers=headers)

        if get_response.status_code != 200:
            print(f"❌ Could not find file '{file_path}' on branch '{branch_name}'")
            return False

        # Extract the SHA (The "Version ID")
        file_data = get_response.json()
        current_sha = file_data["sha"]

        # --- STEP 2: Prepare the Payload ---
        # GitHub requires content to be Base64 encoded (binary safe)
        encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

        data = {
            "message": "refactor: DevGuard auto-fix 🛡️",  # The commit message
            "content": encoded_content,
            "sha": current_sha,  # Proof we saw the latest version
            "branch": branch_name,  # The branch to commit to
        }

        # --- STEP 3: The Commit (PUT Request) ---
        put_response = await client.put(url, json=data, headers=headers)

        if put_response.status_code == 200:
            print(f"✅ File '{file_path}' updated on branch '{branch_name}'!")
            return True
        else:
            print(f"❌ Failed to commit file: {put_response.text}")
            return False


async def create_pull_request(repo_name, title, body, head_branch, base_branch, token):
    """
    Opens a new Pull Request.

    Args:
        repo_name: "owner/repo"
        title: "Fix: Security Vulnerability in login.py"
        body: "I found a SQL injection. Here is the fix."
        head_branch: The branch WITH the fix (e.g., "devguard-fix-1")
        base_branch: The branch WITHOUT the fix (e.g., "feature/login")
        token: Your GitHub PAT.
    """

    url = f"https://api.github.com/repos/{repo_name}/pulls"
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "title": title,
        "body": body,
        "head": head_branch,  # The source of the changes (DevGuard)
        "base": base_branch,  # The destination (User's feature branch)
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

        if response.status_code == 201:
            print(f"✅ PR created successfully! URL: {response.json()['html_url']}")
            return response.json()["html_url"]
        else:
            print(f"❌ Failed to create PR: {response.text}")
            return None


def extract_code_fix(ai_text):
    """
    Scans the AI response for a Python code block and returns just the code.
    """
    pattern = r"```python\n(.*?)```"
    match = re.search(pattern, ai_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


@app.get("/")
def root():
    return {
        "message": "Hello, this is my project, you are not meant to see this but if you end up here then let me know ;)"
    }


@app.get("/reviews", response_model=List[ReviewResponse])
def get_reviews():

    db = SessionLocal()
    try:
        reviews = db.query(Review).order_by(Review.created_at.desc()).limit(10).all()
        return reviews
    finally:
        db.close()


@app.post("/webhook")
async def github_webhook(request: Request):

    await verify_signature(request)

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
            system_prompt = """You are a senior code review engineer and security architect.
            Analyze the following code diff. 
            
            Your goal is two-fold:
            1. IDENTIFY: List any security vulnerabilities, performance issues, or bad practices.
            2. FIX: For every issue identified, provide the CORRECTED code snippet.
            
            Format your response exactly like this:
            
            ### 🚨 Issues Found
            * [Severity: High/Medium/Low] Description of the issue.
            
            ### 🛠️ Proposed Fix
            ```python
            # The corrected code goes here
            ```
            
            ### 💡 Explanation
            Why this fix is better.

            IMPORTANT: If you are providing a corrected code snippet that fixes a security vulnerability, append the text "[AUTO-FIX]" at the very end of your response.
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
                    temperature=0.3,
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
                # test
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
                    if "[AUTO-FIX]" in review_content:
                        print("⚡ Auto-fix trigger detected!")

                        # 1. Extract the fixed code
                        fixed_code = extract_code_fix(review_content)

                        if fixed_code:
                            # 2. Setup Branch Names
                            # Create a unique branch name for this fix
                            fix_branch = f"devguard-fix-{pr_number}"

                            # Get the SHA and Branch of the code we are fixing (from payload)
                            source_sha = pr.get("head", {}).get("sha")
                            original_branch = pr.get("head", {}).get("ref")

                            print(
                                f"Targeting branch: {fix_branch} from {original_branch}"
                            )

                            # 3. Create the Branch
                            if await create_branch(
                                repo_name, source_sha, fix_branch, token
                            ):
                                # 4. Commit the Fix
                                # Note: For this test, we are hardcoding the filename.
                                # In a real app, you'd parse this from the diff.
                                target_file = "bad_sql.py"

                                print(f"Committing fix to {target_file}...")
                                if await update_file(
                                    repo_name,
                                    target_file,
                                    fixed_code,
                                    fix_branch,
                                    token,
                                ):
                                    # 5. Open the Counter-PR
                                    print("Opening Counter-PR...")
                                    pr_url = await create_pull_request(
                                        repo_name=repo_name,
                                        title=f"🛡️ Security Fix for #{pr_number}",
                                        body=f"DevGuard detected a vulnerability. This PR applies the suggested fix.\n\n**Original PR:** #{pr_number}",
                                        head_branch=fix_branch,
                                        base_branch=original_branch,
                                        token=token,
                                    )

                                    if pr_url:
                                        print(f"🚀 Counter-PR created: {pr_url}")

    return {"status": "ok"}
