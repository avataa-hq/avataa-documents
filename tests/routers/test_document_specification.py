# from app.database import db
#
# import pytest
import sys
import os

sys.path.append(os.path.join(sys.path[0], "..", "app"))

prefix = os.environ.get("PREFIX", "/api/documents/v1")


# @pytest.fixture()
# def create_document_spec(rs):
#     payload = {"name": "test post document specification"}
#     r = rs.post(f"{prefix}/documentSpecification/", json=payload)
#     pytest.id = r.json()["id"]
#
#
# def test_can_read_documents_spec(rs, create_document_spec):
#     r = rs.get(f"{prefix}/documentSpecification/")
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 200, (
#         f"Status code should be 200, but got:\n{r.statuse_code}\n{r.text}"
#     )
#     assert isinstance(r.json(), list), "Response body should be list"
#     assert "name" in r.json()[0]
#
#
# def test_can_read_document_spec(rs, create_document_spec):
#     r = rs.get(f"{prefix}/documentSpecification/{pytest.id}")
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 200, (
#         f"Status code should be 200, but got:\n{r.statuse_code}\n{r.text}"
#     )
#
#
# def test_can_delete_document_spec(rs, create_document_spec):
#     r = rs.delete(f"{prefix}/documentSpecification/{pytest.id}")
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 204, (
#         f"Status code should be 200, but got:\n{r.statuse_code}\n{r.text}"
#     )
#     assert db.document_specification.find_one({"id": pytest.id}) is None, (
#         "Should be deleted from database"
#     )
#
#
# def test_can_create_document_spec(rs):
#     payload = {"name": "test post document specification"}
#     r = rs.post(f"{prefix}/documentSpecification/", json=payload)
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 201, (
#         f"Status code should be 201, but got:\n{r.statuse_code}\n{r.text}"
#     )
#
#
# def test_can_patch_document_spec(rs, create_document_spec):
#     name = "patched document spec name"
#     payload = {"name": name}
#     r = rs.patch(f"{prefix}/documentSpecification/{pytest.id}", json=payload)
#     print("\n", r.url, "\n", r.status_code, "\n", r.text)
#     assert r.status_code == 200, (
#         f"Status code should be 200, but got:\n{r.statuse_code}\n{r.text}"
#     )
#
#     assert (
#         db.document_specification.find_one({"id": pytest.id})["name"] == name
#     ), f"Status should be '{name}'"
