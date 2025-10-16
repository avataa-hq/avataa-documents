# from app.database import db

import pytest
import sys
import os

sys.path.append(os.path.join(sys.path[0], "..", "app"))

prefix = os.environ.get("PREFIX", "/api/documents/v1")


@pytest.fixture()
def create_document(rs, mock_database):
    payload = {"name": "test post document"}
    mock_database.document.find_one.return_value = None
    r = rs.post("/document", json=payload)
    pytest.id = r.json()["id"]


def test_can_read_documents(rs, create_document, mock_database):
    mock_database.document.find.return_value = [{"name": "test post document"}]
    r = rs.get("/document")
    print("\n", r.url, "\n", r.status_code, "\n", r.text)
    assert r.status_code == 200, (
        f"Status code should be 200, but got:\n{r.statuse_code}\n{r.text}"
    )
    assert isinstance(r.json(), list), "Response body should be list"
    assert "name" in r.json()[0]


#
#
# def test_can_read_document(rs, create_document):
#     r = rs.get(f"{prefix}/document/{pytest.id}")
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 200, (
#         f"Status code should be 200, but got:\n{r.statuse_code}\n{r.text}"
#     )
#
#
# def test_can_delete_document(rs, create_document):
#     r = rs.delete(f"{prefix}/document/{pytest.id}")
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 204, (
#         f"Status code should be 200, but got:\n{r.statuse_code}\n{r.text}"
#     )
#     assert db.document.find_one({"id": pytest.id})["status"] == "deleted", (
#         "Status should be 'deleted'"
#     )
#
#
# def test_can_create_document(rs):
#     payload = {"name": "test post document"}
#     r = rs.post(f"{prefix}/document/", json=payload)
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 201, (
#         f"Status code should be 201, but got:\n{r.statuse_code}\n{r.text}"
#     )
#
#
# def test_can_patch_document(rs, create_document):
#     name = "patched document"
#     payload = {"name": name}
#     r = rs.patch(f"{prefix}/document/{pytest.id}", json=payload)
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 200, (
#         f"Status code should be 200, but got:\n{r.statuse_code}\n{r.text}"
#     )
#
#     print(db.document.find_one({"id": pytest.id}))
#     assert db.document.find_one({"id": pytest.id})["name"] == name, (
#         f"Status should be '{name}'"
#     )
#     assert db.document.find_one({"id": pytest.id})["status"] == "created", (
#         "Status should be 'created'"
#     )
