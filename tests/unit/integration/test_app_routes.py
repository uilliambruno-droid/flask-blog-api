from http import HTTPStatus


def test_docs_route_returns_openapi_payload(client):
    response = client.get("/docs")

    assert response.status_code == HTTPStatus.OK
    assert "paths" in response.json


def test_not_found_returns_json_payload(client):
    response = client.get("/route-that-does-not-exist")

    expected_description = (
        "The requested URL was not found on the server. "
        "If you entered the URL manually please check your spelling and try again."
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {
        "code": HTTPStatus.NOT_FOUND,
        "name": "Not Found",
        "description": expected_description,
    }
