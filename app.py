from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import re
import os
import base64

from utils.pdf_generator import generate_tenant_pdf
from utils.email_sender import send_tenant_email

app = FastAPI(title="Tenant Application API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_phone(phone: str) -> bool:
    return bool(re.compile(r'^[\+\(\)\s\-0-9]{7,20}$').match(phone))

class ApplicationData(BaseModel):
    fullName: str
    phone: str
    address: str
    peopleDetails: str
    hasPets: str = None
    petDetails: str = None
    occupation: str
    company: str = None
    jobType: str = None
    businessInfo: str = None
    institute: str = None
    studentIncome: str = None
    incomeSourceDetails: str = None
    income: str = None
    employmentDuration: str = None
    moveInDate: str
    stayDuration: str = None
    rentRange: str = None
    securityDeposit: str = None
    rentedBefore: str = None
    previousLandlord: str = None
    reasonForLeaving: str = None
    rule1: str = None
    rule2: str = None
    rule3: str = None
    rule4: str = None
    rule5: str = None
    rule6: str = None
    legalIssues: str = None
    cnic_base64: str = None
    cnic_filename: str = None

@app.get("/health")
def health():
    return {"status": "ok", "message": "Railway server is running"}

@app.post("/submit")
async def submit_application(payload: ApplicationData):
    try:
        # Validation
        if not all([payload.fullName.strip(), payload.address.strip(),
                    payload.peopleDetails.strip(), payload.occupation.strip(),
                    payload.moveInDate.strip()]):
            raise HTTPException(status_code=400, detail="Missing required fields.")

        if not validate_phone(payload.phone):
            raise HTTPException(status_code=400, detail="Invalid phone number format.")

        if not all([payload.rule1, payload.rule2, payload.rule3,
                    payload.rule4, payload.rule5, payload.rule6]):
            raise HTTPException(status_code=400, detail="All eligibility rules must be accepted.")

        # Build data dict for PDF
        data = payload.dict(exclude={"cnic_base64", "cnic_filename"})

        # Decode CNIC image from base64
        cnic_content = None
        cnic_filename = None
        if payload.cnic_base64:
            raw = payload.cnic_base64
            if "," in raw:
                raw = raw.split(",")[1]
            cnic_content = base64.b64decode(raw)
            if len(cnic_content) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="CNIC image must be under 5MB.")
            cnic_filename = payload.cnic_filename

        # Generate PDF
        pdf_buffer = generate_tenant_pdf(data, cnic_content)

        # Send Email with PDF attached
        success = send_tenant_email(pdf_buffer, payload.fullName, cnic_content, cnic_filename)

        if success:
            return {"status": "success", "message": "Application submitted successfully."}
        else:
            return {"status": "warning", "message": "Application received but email not configured."}

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend static files
@app.get("/style.css")
def serve_css():
    return FileResponse("style.css", media_type="text/css")

@app.get("/")
def serve_index():
    return FileResponse("index.html")
