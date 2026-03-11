from http import HTTPStatus

from src.models import Role, db


def test_admin_to_normal_user_full_portfolio_flow(client, access_token):
    create_role_response = client.post(
        "/roles/",
        json={"name": "normal"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_role_response.status_code == HTTPStatus.CREATED
    assert create_role_response.json == {"message": "Role created!"}

    normal_role_id = db.session.execute(
        db.select(Role.id).where(Role.name == "normal")
    ).scalar()
    assert normal_role_id is not None

    create_user_response = client.post(
        "/users/",
        json={
            "username": "portfolio-user",
            "password": "secret123",
            "role_id": normal_role_id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert create_user_response.status_code == HTTPStatus.CREATED

    admin_list_response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    created_user = next(
        user
        for user in admin_list_response.json["users"]
        if user["username"] == "portfolio-user"
    )

    login_response = client.post(
        "/auth/login",
        json={"username": "portfolio-user", "password": "secret123"},
    )
    assert login_response.status_code == HTTPStatus.OK
    normal_token = login_response.json["access_token"]

    forbidden_admin_response = client.post(
        "/roles/",
        json={"name": "should-fail"},
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert forbidden_admin_response.status_code == HTTPStatus.FORBIDDEN

    empty_posts_response = client.get(
        "/posts/",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert empty_posts_response.status_code == HTTPStatus.OK
    assert empty_posts_response.json == {"posts": []}

    create_post_response = client.post(
        "/posts/",
        json={
            "title": "Portfolio Post",
            "body": "Testing the full project flow",
            "author_id": created_user["id"],
        },
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert create_post_response.status_code == HTTPStatus.CREATED

    list_posts_response = client.get(
        "/posts/",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert list_posts_response.status_code == HTTPStatus.OK
    created_post = list_posts_response.json["posts"][0]
    assert created_post["title"] == "Portfolio Post"

    get_post_response = client.get(
        f"/posts/{created_post['id']}",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert get_post_response.status_code == HTTPStatus.OK
    assert get_post_response.json["title"] == "Portfolio Post"

    patch_post_response = client.patch(
        f"/posts/{created_post['id']}",
        json={"title": "Updated Portfolio Post"},
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert patch_post_response.status_code == HTTPStatus.OK
    assert patch_post_response.json["title"] == "Updated Portfolio Post"

    delete_post_response = client.delete(
        f"/posts/{created_post['id']}",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert delete_post_response.status_code == HTTPStatus.NO_CONTENT

    get_user_response = client.get(
        f"/users/{created_user['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_user_response.status_code == HTTPStatus.OK
    assert get_user_response.json["user"]["username"] == "portfolio-user"

    delete_user_response = client.delete(
        f"/users/{created_user['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_user_response.status_code == HTTPStatus.OK
    assert delete_user_response.json == {"message": "User deleted successfully!"}

    relogin_response = client.post(
        "/auth/login",
        json={"username": "portfolio-user", "password": "secret123"},
    )
    assert relogin_response.status_code == HTTPStatus.UNAUTHORIZED
