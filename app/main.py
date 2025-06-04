from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
import json

SMTP_HOST = "ann.naruto-u.ac.jp"
SMTP_PORT = 25

with open("apikeys.json", "r") as f:
    API_KEYS = {entry["key"]: entry["label"] for entry in json.load(f)}
APY_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=APY_KEY_NAME, auto_error=False)


async def evaluate_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header in API_KEYS:
        return True
    raise HTTPException(status_code=401, detail="Invalid API key")


app = FastAPI(title="NUE Mailing API")


class EmailPayload(BaseModel):
    to: EmailStr
    subject: str
    body: str
    from_address: EmailStr
    from_name: str
    date: str
    cc: list[EmailStr] = []
    bcc: list[EmailStr] = []


@app.post("/send")
def send_email(payload: EmailPayload, _: bool = Depends(evaluate_api_key)):
    msg = MIMEText(payload.body)
    msg["Subject"] = payload.subject
    msg["From"] = formataddr((payload.from_name, payload.from_address))
    msg["To"] = payload.to

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send email via SMTP: {e}"
        )

    return {"message": "successfully sent"}
