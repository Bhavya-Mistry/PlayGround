from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Hello, this is my project, you are not meant to see this but if you end up here then let me know ;)"
    }


@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json
    print(payload)
    return {"status": "ok"}
