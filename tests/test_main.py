from http.client import HTTPException
from fastapi.testclient import TestClient


def test_get(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    assert len(response.text) > 0
    assert response.json() != {"Amgen": "Sensing Pipeline API"}


# Products
def test_product(test_client: TestClient):
    credentials = "lasjdlkjsadlksajd"
    response = test_client.get(
        "/api/v1/product?product=123123",
        headers={"Authorization": "Bearer {}".format(credentials)},
    )
    assert response.status_code == 403
    assert len(response.text) > 0


def test_bad_forbidden_product(test_client: TestClient):
    credentials = "lasjdlkjsadlksajd"
    response = test_client.get(
        "/api/v1/product?product=141441",
        headers={"Authorization": "Bearer {}".format(credentials)},
    )
    assert response.status_code == 403
    assert len(response.text) > 0


def test_bad_product(test_client_bad: TestClient):
    mocked_get = test_client_bad.patch("app.products.products")
    mocked_get.side_effect = Exception("Something broke")
    response = test_client_bad.get("/api/v1/product?product=product")
    assert response.status_code == 403


def test_product_tpp(test_client: TestClient):
    credentials = "lasjdlkjsadlksajd"
    response = test_client.get(
        "/api/v1/product/tpp?name=asdasda,asdsadsa",
        headers={"Authorization": "Bearer {}".format(credentials)},
    )
    assert response.status_code == 403
    assert len(response.text) > 0


def test_bad_forbidden_product_tpp(test_client: TestClient):
    credentials = "lasjdlkjsadlksajd"
    response = test_client.get(
        "/api/v1/product/tpp?name=asdasda",
        headers={"Authorization": "Bearer {}".format(credentials)},
    )
    assert response.status_code == 403
    assert len(response.text) > 0


def test_bad_product_tpp(test_client_bad: TestClient):
    mocked_get = test_client_bad.patch("app.products.products_tpp")
    mocked_get.side_effect = Exception("Something broke")
    response = test_client_bad.get("/api/v1/product/tpp?name=asdasda")
    assert response.status_code == 403
