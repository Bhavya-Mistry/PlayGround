from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Hello, this is my project, you are not meant to see this but if you end up here then let me know ;)"
    }
