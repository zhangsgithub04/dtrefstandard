from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
from supabase import create_client, Client
from datetime import date, datetime, timezone
from typing import Optional
import os

app = FastAPI(title="Standard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://dtrefstandard-ui.onrender.com",
        "https://zhangsgithub04.github.io",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MY_API_KEY = os.getenv("MY_API_KEY")

if not SUPABASE_URL:
    raise RuntimeError("Missing SUPABASE_URL")

if not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_KEY")

if not MY_API_KEY:
    raise RuntimeError("Missing MY_API_KEY")

if not SUPABASE_URL.startswith("https://") or "supabase.co" not in SUPABASE_URL:
    raise RuntimeError(f"Invalid SUPABASE_URL: {SUPABASE_URL}")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != MY_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key


class StandardCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=50)
    standardname: str = Field(..., min_length=1, max_length=200)
    version: str = Field(..., min_length=1, max_length=50)
    standard_date: Optional[date] = None
    description: Optional[str] = None
    longdescription: Optional[str] = None
    url: Optional[HttpUrl] = None
    organization: Optional[str] = Field(None, max_length=200)


class StandardUpdate(BaseModel):
    symbol: Optional[str] = Field(None, min_length=1, max_length=50)
    standardname: Optional[str] = Field(None, min_length=1, max_length=200)
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    standard_date: Optional[date] = None
    description: Optional[str] = None
    longdescription: Optional[str] = None
    url: Optional[HttpUrl] = None
    organization: Optional[str] = Field(None, max_length=200)


@app.get("/")
async def root():
    response = supabase.table("standard").select("*", count="exact").execute()
    return {
        "message": "Standard API is running",
        "standard_count": response.count,
    }


@app.get("/standards")
#async def list_standards(api_key: str = Depends(require_api_key)):
async def list_standards():
    response = (
        supabase
        .table("standard")
        .select("*")
        .order("symbol")
        .order("version")
        .execute()
    )
    return response.data


@app.get("/standards/count")
#async def count_standards(api_key: str = Depends(require_api_key)):
async def count_standards():
    response = supabase.table("standard").select("*", count="exact").execute()
    return {"count": response.count}


@app.get("/standards/{standard_id}")
#async def get_standard(standard_id: int, api_key: str = Depends(require_api_key)):
async def get_standard(standard_id: int):
    response = (
        supabase
        .table("standard")
        .select("*")
        .eq("id", standard_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Standard not found")

    return response.data[0]


@app.get("/standards/by-symbol/{symbol}")
#async def list_standards_by_symbol(symbol: str, api_key: str = Depends(require_api_key)):
async def list_standards_by_symbol(symbol: str):
    response = (
        supabase
        .table("standard")
        .select("*")
        .eq("symbol", symbol)
        .order("version")
        .execute()
    )

    return response.data

@app.get("/standards/latest/{symbol}")
#async def get_latest_standard_by_symbol(symbol: str,api_key: str = Depends(require_api_key),):
async def get_latest_standard_by_symbol(symbol: str):
    response = (
        supabase
        .table("standard")
        .select("*")
        .eq("symbol", symbol)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Standard not found")

    return response.data[0]
    

@app.get("/standards/by-symbol/{symbol}/{version}")
#async def get_standard_by_symbol_version(symbol: str,version: str,api_key: str = Depends(require_api_key)):
async def get_standard_by_symbol_version(symbol: str,version: str):
    response = (
        supabase
        .table("standard")
        .select("*")
        .eq("symbol", symbol)
        .eq("version", version)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Standard not found")

    return response.data[0]


@app.post("/standards", status_code=201)
async def create_standard(
    standard: StandardCreate,
    api_key: str = Depends(require_api_key),
):
    payload = {
        "symbol": standard.symbol.strip(),
        "standardname": standard.standardname.strip(),
        "version": standard.version,
        "standard_date": standard.standard_date.isoformat() if standard.standard_date else None,
        "description": standard.description.strip() if standard.description else None,
        "longdescription": standard.longdescription.strip() if standard.longdescription else None,
        "url": str(standard.url) if standard.url else None,
        "organization": standard.organization.strip() if standard.organization else None,
        "updated_at": utc_now_iso(),
    }

    response = supabase.table("standard").insert(payload).execute()

    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create standard")

    return response.data[0]


@app.patch("/standards/{standard_id}")
async def update_standard(
    standard_id: int,
    standard: StandardUpdate,
    api_key: str = Depends(require_api_key),
):
    update_data = standard.model_dump(exclude_none=True)

    if "symbol" in update_data:
        update_data["symbol"] = update_data["symbol"].strip()

    if "standardname" in update_data:
        update_data["standardname"] = update_data["standardname"].strip()

    if "standard_date" in update_data and update_data["standard_date"] is not None:
        update_data["standard_date"] = update_data["standard_date"].isoformat()

    if "description" in update_data and update_data["description"] is not None:
        update_data["description"] = update_data["description"].strip()

    if "longdescription" in update_data and update_data["longdescription"] is not None:
        update_data["longdescription"] = update_data["longdescription"].strip()

    if "url" in update_data and update_data["url"] is not None:
        update_data["url"] = str(update_data["url"])

    if "organization" in update_data and update_data["organization"] is not None:
        update_data["organization"] = update_data["organization"].strip()

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    update_data["updated_at"] = utc_now_iso()

    response = (
        supabase
        .table("standard")
        .update(update_data)
        .eq("id", standard_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Standard not found")

    return response.data[0]


@app.put("/standards/{standard_id}")
async def replace_standard(
    standard_id: int,
    standard: StandardCreate,
    api_key: str = Depends(require_api_key),
):
    payload = {
        "symbol": standard.symbol.strip(),
        "standardname": standard.standardname.strip(),
        "version": standard.version,
        "standard_date": standard.standard_date.isoformat() if standard.standard_date else None,
        "description": standard.description.strip() if standard.description else None,
        "longdescription": standard.longdescription.strip() if standard.longdescription else None,
        "url": str(standard.url) if standard.url else None,
        "organization": standard.organization.strip() if standard.organization else None,
        "updated_at": utc_now_iso(),
    }

    response = (
        supabase
        .table("standard")
        .update(payload)
        .eq("id", standard_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Standard not found")

    return response.data[0]


@app.delete("/standards/{standard_id}")
async def delete_standard(
    standard_id: int,
    api_key: str = Depends(require_api_key),
):
    response = (
        supabase
        .table("standard")
        .delete()
        .eq("id", standard_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Standard not found")

    return {"message": "Standard deleted successfully"}
