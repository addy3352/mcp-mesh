
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

class PostBody(BaseModel):
    message: str
    visibility: str | None = "PUBLIC"

@router.post("/linkedin.create_post")
def create_post(body: PostBody):
    mention = os.getenv("LINKEDIN_MENTION", "Agent IRIS is posting on Aditya's behalf")
    text = f"{mention}\n\n{body.message}"
    # TODO: Integrate real LinkedIn API call with LINKEDIN_TOKEN.
    print("[LinkedIn] Would post:\n", text)
    return {"ok": True, "posted": True, "text": text}
