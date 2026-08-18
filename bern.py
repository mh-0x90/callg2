from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from bern_service import build_bern_response
from run_service import run


class BernRequest(BaseModel):
    website: str = Field(min_length=1)
    user_data: str = Field(min_length=1)


class BernResponse(BaseModel):
    result: str


class RunRequest(BaseModel):
    value: str = Field(min_length=1)


class RunResponse(BaseModel):
    result: str


router = APIRouter(prefix="/bern", tags=["bern"])


@router.post("", response_model=BernResponse, status_code=status.HTTP_200_OK)
def create_bern(payload: BernRequest) -> BernResponse:
    try:
        result = build_bern_response(payload.website, payload.user_data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="XML data source file not found on disk.",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return BernResponse(result=result)


@router.post("/run", response_model=RunResponse, status_code=status.HTTP_200_OK)
def create_run(payload: RunRequest) -> RunResponse:
    result = run(payload.value)
    return RunResponse(result=result)


app = FastAPI(title="Bern API")
app.include_router(router)