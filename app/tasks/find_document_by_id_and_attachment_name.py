from pydantic import parse_obj_as

from database import Database, db
from schemas.document import Document


def find_document_by_id_and_attachment_name(
    mo_id: int, attachment_name: str, db_client: Database = db
) -> list[Document] | None:
    query = {
        "externalIdentifier": {"$elemMatch": {"id": str(mo_id)}},
        "attachment": {"$elemMatch": {"name": attachment_name}},
    }
    documents = [
        parse_obj_as(Document, i) for i in db_client.document.find(query)
    ]
    if not documents:
        return None
    return documents
