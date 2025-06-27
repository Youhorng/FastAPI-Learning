from typing import Optional, List
from fastapi import Body, FastAPI, HTTPException, Response, status, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()






# Database connection
while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="lolishi",
                            cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection successful")
        break
    except Exception as error:
        print("Database connection failed")
        print(f"Error: {error}")
        time.sleep(2)




@app.get("/")
def root(): 
    return {"message": "Welcome to my API"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status": posts}


@app.get("/posts", response_model=List[schemas.Post])
def get_post(db: Session = Depends(get_db)):
    # posts = cursor.execute("""SELECT * FROM posts""")
    # posts= cursor.fetchall()
    posts = db.query(models.Post).all()

    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(**post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post_data = cursor.fetchone()
    # if not post_data:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
    #                         detail=f"Post with id {id} not found")

    post_data = db.query(models.Post).filter(models.Post.id == id).first()
    if not post_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    
    return post_data


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    # if deleted_post is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"Post with id {id} not found")

    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    # if updated_post is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"Post with id {id} not found")
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    
    return post_query.first()

    