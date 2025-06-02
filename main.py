from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
import json

SMTP_HOST = "ann.naruto-u.ac.jp"
SMTP_PORT = 25

with open("apikeys.json", "r") as f:
    API_KEYS = {entry["key"]: entry["label"] for entry in json.load(f)}

app = FastAPI()

class EmailPayload(BaseModel):
    to: EmailStr
    subject: str
    body: str
    from_address: EmailStr
    from_name: str  # ← 表示名

@app.post("/send")
def send_email(payload: EmailPayload, request: Request):
    api_key = request.headers.get("X-API-KEY")
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    msg = MIMEText(payload.body)
    msg["Subject"] = payload.subject
    msg["From"] = formataddr((payload.from_name, payload.from_address))
    msg["To"] = payload.to

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMTP送信失敗: {e}")

    return {"message": "メールを送信しました"}