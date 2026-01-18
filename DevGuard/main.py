from fastapi import FastAPI, Request

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
        pr_number = payload.get("repository", {})
        repo_name = payload.get("repository", {})
        print(f"New PR {pr_number} opened in {repo_name}")
    else:
        print("Event Ignored")
    return {"status": "ok"}
