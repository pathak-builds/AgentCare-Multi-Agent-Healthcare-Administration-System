"""
Tools for document processing:
- List patient documents
- Extract document text
- Classify documents
- Check duplicate documents
"""

import json

from langchain_core.tools import tool

from app.database.session import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService


ALLOWED_CLASSIFICATIONS = {
    "Blood Report",
    "ECG",
    "MRI",
    "CT Scan",
    "Prescription",
    "Insurance",
    "Other",
}


@tool
def list_patient_documents(patient_id: str) -> str:
    """
    Return all documents belonging to a patient.
    """

    db = SessionLocal()

    try:
        repo = DocumentRepository(db)

        docs = repo.get_by_patient(patient_id)

        if not docs:
            return json.dumps(
                {
                    "documents": [],
                    "message": "No documents found."
                },
                indent=2,
            )

        result = []

        for doc in docs:

            preview = (
                doc.extracted_text[:100] + "..."
                if doc.extracted_text and len(doc.extracted_text) > 100
                else doc.extracted_text or "Not extracted"
            )

            result.append(
                {
                    "id": doc.id,
                    "original_filename": doc.original_filename,
                    "file_type": doc.file_type,
                    "classification": doc.classification or "Unclassified",
                    "checksum": doc.sha256_checksum,
                    "uploaded_at": doc.created_at.isoformat(),
                    "text_preview": preview,
                }
            )

        return json.dumps(
            {
                "documents": result
            },
            indent=2,
        )

    finally:
        db.close()


@tool
def extract_document_text(doc_id: str) -> str:
    """
    Extract text from a document and return a preview.
    """

    db = SessionLocal()

    try:
        service = DocumentService(db)

        text = service.extract_text(doc_id)

        if not text:
            return json.dumps(
                {
                    "status": "success",
                    "preview": "No text could be extracted."
                },
                indent=2,
            )

        preview = text[:500]

        if len(text) > 500:
            preview += "..."

        return json.dumps(
            {
                "status": "success",
                "preview": preview,
            },
            indent=2,
        )

    except Exception as e:

        return json.dumps(
            {
                "status": "error",
                "message": str(e),
            },
            indent=2,
        )

    finally:
        db.close()


@tool
def classify_document(doc_id: str, classification: str) -> str:
    """
    Assign an administrative classification to a document.
    """

    db = SessionLocal()

    try:

        repo = DocumentRepository(db)

        doc = repo.get_by_id(doc_id)

        if not doc:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Document not found.",
                },
                indent=2,
            )

        if classification not in ALLOWED_CLASSIFICATIONS:

            return json.dumps(
                {
                    "status": "error",
                    "message": "Invalid classification.",
                    "allowed": sorted(ALLOWED_CLASSIFICATIONS),
                },
                indent=2,
            )

        doc.classification = classification

        db.commit()
        db.refresh(doc)

        return json.dumps(
            {
                "status": "success",
                "document_id": doc.id,
                "classification": classification,
                "message": f"Document classified as '{classification}'.",
            },
            indent=2,
        )

    except Exception as e:

        db.rollback()

        return json.dumps(
            {
                "status": "error",
                "message": str(e),
            },
            indent=2,
        )

    finally:
        db.close()


@tool
def check_duplicate(checksum: str) -> str:
    """
    Check whether a document with the given checksum already exists.
    """

    db = SessionLocal()

    try:

        repo = DocumentRepository(db)

        existing = repo.get_by_checksum(checksum)

        if existing:

            return json.dumps(
                {
                    "duplicate": True,
                    "document_id": existing.id,
                    "original_filename": existing.original_filename,
                    "classification": existing.classification,
                },
                indent=2,
            )

        return json.dumps(
            {
                "duplicate": False
            },
            indent=2,
        )

    except Exception as e:

        return json.dumps(
            {
                "status": "error",
                "message": str(e),
            },
            indent=2,
        )

    finally:
        db.close()