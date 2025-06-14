from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
from typing import Optional

# Initialize app
app = FastAPI()

class Post(BaseModel):
    title : str
    content : str
    published : bool = True
    rating : Optional[int] = None

my_posts = [
    {"title" : "title of post1", "content" : "content of post 1", "id":1},
    {"title" : "title of post2", "content" : "content of post 2", "id":2}
]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
@app.get("/")
def root():
    return {
        "message" : "Hello World"
    }

@app.post("/posts")
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0,1000000)
    my_posts.append(post_dict)
    return {"data":post_dict}

@app.get("/post/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id : {id} was not found")
    return{
        "post_detail" : post
    }
