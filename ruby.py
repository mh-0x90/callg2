from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, FastAPI, status
from pydantic import BaseModel, Field

from dependencies import CurrentUser, get_db, require_sku_group_member
from service import create_ruby_record


class RubyCreateRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0)
    note: str | None = Field(default=None, max_length=255)


class RubyCreateResponse(BaseModel):
    id: int
    sku: str
    quantity: int
    note: str | None
    created_by: str
    group: str


router = APIRouter(prefix="/ruby", tags=["ruby"])


@router.post("", response_model=RubyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_ruby(
    payload: RubyCreateRequest,
    db: sqlite3.Connection = Depends(get_db),
    current_user: CurrentUser = Depends(require_sku_group_member),
) -> RubyCreateResponse:
    saved_record = create_ruby_record(
        connection=db,
        payload=payload.model_dump(),
        current_user=current_user,
    )
    return RubyCreateResponse(**saved_record)


app = FastAPI(title="Ruby API")
app.include_router(router)