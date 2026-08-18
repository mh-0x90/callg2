from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from dependencies import get_db
from olten3 import is_valid_length
from olten4 import Profile
from repository import fetch_profile, validate_element_2, validate_element_3

from olten2 import process_olten_input

# Global constant for max length threshold
MAX_ELEMENT_LENGTH = 1000000


class OltenRequest(BaseModel):
    user_input: str = Field(min_length=1)
    log_file: str | None = Field(default=None)


class OltenResponse(BaseModel):
    result: str


class DynamicdRequest(BaseModel):
    element1: str = Field(min_length=1)
    element2: str = Field(min_length=1)
    element3: str = Field(min_length=1)
    operation: str | None = Field(default=None, description="Optional dynamic operation for element2")


class DynamicdResponse(BaseModel):
    status: str
    element1_stored: bool
    element2_validated: str
    element3_hash: str


class User(BaseModel):
    user_id: int
    username: str







async def get_current_user() -> User:
    return User(user_id=1, username="alice")


router = APIRouter(prefix="/olten", tags=["olten"])


@router.post("", response_model=OltenResponse, status_code=status.HTTP_200_OK)
def create_olten(payload: OltenRequest) -> OltenResponse:
    result = process_olten_input(payload.user_input, payload.log_file)
    return OltenResponse(result=result)


@router.get("/users/{user_id}/profile", response_model=Profile)
def get_user_profile(
    user_id: int,
    db: sqlite3.Connection = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Profile:
    profile = fetch_profile(db, user_id)
    if profile is None or not is_valid_length(profile.username):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.post("/dynamicd", response_model=DynamicdResponse, status_code=status.HTTP_200_OK)
def dynamicd(payload: DynamicdRequest) -> DynamicdResponse:
    # Process element 1: check length and store to file if > 1000
    element1_stored = False
    if len(payload.element1) > 1000 and len(payload.element1) <= MAX_ELEMENT_LENGTH:
        output_path = Path("dynamicd_elements.txt")
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(f"element1:{payload.element1}\n")
        element1_stored = True
    elif len(payload.element1) > MAX_ELEMENT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Element 1 exceeds max length {MAX_ELEMENT_LENGTH}",
        )

    # Process element 2: validate through repository call chain with optional operation
    element2_result = validate_element_2(payload.element2, payload.operation)

    element3_hash = validate_element_3(payload.element3)

    return DynamicdResponse(
        status="success",
        element1_stored=element1_stored,
        element2_validated=element2_result,
        element3_hash=element3_hash,
    )


@router.post("/cookies/kharid/null", status_code=status.HTTP_200_OK)
def clear_kharid_cookie(response: Response) -> dict[str, str]:
    response.delete_cookie(key="kharid")
    return {"status": "ok", "cookie": "kharid", "state": "null"}


app = FastAPI(title="Olten API")
app.include_router(router)