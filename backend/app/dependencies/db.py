from typing import Annotated
from fastapi import Depends
from google.cloud import firestore
from app.core.config import Settings, get_settings


def get_firestore_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> firestore.Client:
    return firestore.Client(project=settings.gcp_project_id)
