from http import HTTPStatus

from src.models import Post, Role, User, db


def _create_normal_user(client):
    role = Role(name="normal")
    db.session.add(role)
    db.session.commit()

    user = User(username="john-post", password="test", role_id=role.id)
    db.session.add(user)
    db.session.commit()

    login_response = client.post(
        "/auth/login",
        json={"username": user.username, "password": user.password},
    )

    access_token = login_response.json["access_token"]
    return user, access_token


def test_create_post_success(client):
    user, access_token = _create_normal_user(client)

    payload = {
        "title": "First post",
        "body": "This is my first post",
        "author_id": user.id,
    }

    response = client.post(
        "/posts/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"message": "Post created!"}

    post = db.session.execute(
        db.select(Post).where(Post.title == "First post")
    ).scalar()

    assert post is not None
    assert post.body == "This is my first post"
    assert post.author_id == user.id


def test_create_post_without_token(client):
    payload = {
        "title": "First post",
        "body": "This is my first post",
        "author_id": 1,
    }

    response = client.post("/posts/", json=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_list_posts_without_token(client):
    response = client.get("/posts/")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_list_posts_empty_success(client):
    _, access_token = _create_normal_user(client)

    response = client.get(
        "/posts/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == {"posts": []}


def test_create_post_forbidden(client):
    role = Role(name="admin")
    db.session.add(role)
    db.session.commit()

    user = User(username="admin-user", password="test", role_id=role.id)
    db.session.add(user)
    db.session.commit()

    login_response = client.post(
        "/auth/login",
        json={"username": user.username, "password": user.password},
    )

    access_token = login_response.json["access_token"]

    payload = {
        "title": "First post",
        "body": "This is my first post",
        "author_id": user.id,
    }

    response = client.post(
        "/posts/",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json == {"message": "User dosent have access"}


def test_list_posts_success(client):
    user, access_token = _create_normal_user(client)

    post = Post(title="First post", body="This is my first post", author_id=user.id)
    db.session.add(post)
    db.session.commit()

    response = client.get(
        "/posts/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "body": post.body,
                "created": post.created.isoformat() if post.created else None,
                "author_id": post.author_id,
            }
        ]
    }


def test_get_post_success(client):
    user, access_token = _create_normal_user(client)

    post = Post(title="First post", body="This is my first post", author_id=user.id)
    db.session.add(post)
    db.session.commit()

    response = client.get(
        f"/posts/{post.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created.isoformat() if post.created else None,
        "author_id": post.author_id,
    }


def test_get_post_not_found(client):
    user, access_token = _create_normal_user(client)

    response = client.get(
        "/posts/999",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_post_without_token(client):
    response = client.get("/posts/1")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_post_success(client):
    user, access_token = _create_normal_user(client)

    post = Post(title="First post", body="This is my first post", author_id=user.id)
    db.session.add(post)
    db.session.commit()

    response = client.delete(
        f"/posts/{post.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert db.session.get(Post, post.id) is None


def test_delete_post_not_found(client):
    user, access_token = _create_normal_user(client)

    response = client.delete(
        "/posts/999",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_post_success(client):
    user, access_token = _create_normal_user(client)

    post = Post(title="First post", body="This is my first post", author_id=user.id)
    db.session.add(post)
    db.session.commit()

    payload = {"title": "Updated title", "body": "Updated body"}

    response = client.patch(
        f"/posts/{post.id}",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "id": post.id,
        "title": "Updated title",
        "body": "Updated body",
        "created": post.created.isoformat() if post.created else None,
        "author_id": post.author_id,
    }

    updated_post = db.session.get(Post, post.id)
    assert updated_post.title == "Updated title"
    assert updated_post.body == "Updated body"


def test_update_post_not_found(client):
    user, access_token = _create_normal_user(client)

    payload = {"title": "Updated title"}

    response = client.patch(
        "/posts/999",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
