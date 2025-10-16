import os
import pytest
import requests
import sys

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

sys.path.append(os.path.join(sys.path[0], "..", "app"))

from app.main import app_v1


@pytest.fixture(autouse=True)
def db_clear():
    yield db_clear
    # db.document.delete_many({})
    # db.document_specification.delete_many({})


class RequestsSession(requests.Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super(RequestsSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs):
        url = f"{self.prefix_url}{url}"
        return super(RequestsSession, self).request(
            method, url, *args, **kwargs
        )


# @pytest.fixture(name="rs", scope="session")
# def requests_session():
#     with RequestsSession('http://localhost:8000') as rs:
#         yield rs


@pytest.fixture(scope="function", autouse=True)
def mock_database():
    mock_db = MagicMock()
    mock_document = MagicMock()
    mock_db.document = mock_document

    with patch("routers.document_router.db", mock_db):
        yield mock_db


@pytest.fixture(name="rs", scope="function")
def client_session():
    with TestClient(app_v1) as rs:
        yield rs
