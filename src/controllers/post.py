from http import HTTPStatus

from flask import Blueprint, request
from sqlalchemy import inspect
from src.app import Post, db
from src.utils import requires_roles

app = Blueprint("post", __name__, url_prefix="/posts")


def _create_post():
    data = request.json

    post = Post(
        title=data["title"],
        body=data["body"],
        author_id=data["author_id"],
    )

    db.session.add(post)
    db.session.commit()


def _list_posts():
    query = db.select(Post)
    posts = db.session.execute(query).scalars()
    return [
        {
            "id": post.id,
            "title": post.title,
            "body": post.body,
            "created": post.created.isoformat() if post.created else None,
            "author_id": post.author_id,
        }
        for post in posts
    ]


@app.route("/", methods=["GET", "POST"])
@requires_roles("normal")
def handle_post():
    if request.method == "POST":
        _create_post()
        return {"message": "Post created!"}, HTTPStatus.CREATED
    else:
        return {"posts": _list_posts()}


@app.route("/<int:post_id>")
@requires_roles("normal")
def get_post(post_id):
    post = db.get_or_404(Post, post_id)
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created.isoformat() if post.created else None,
        "author_id": post.author_id,
    }


@app.route("/<int:post_id>", methods=["DELETE"])
@requires_roles("normal")
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()
    return "", HTTPStatus.NO_CONTENT


@app.route("/<int:post_id>", methods=["PATCH"])
@requires_roles("normal")
def update_post(post_id):
    post = db.get_or_404(Post, post_id)
    data = request.json

    mapper = inspect(Post)
    for column in mapper.attrs:
        # opcional: evitar alteração de campos sensíveis
        if column.key in ("id", "created"):
            continue

        if column.key in data:
            setattr(post, column.key, data[column.key])

    db.session.commit()

    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created.isoformat() if post.created else None,
        "author_id": post.author_id,
    }
