from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, ValidationError
import re
import os
import base64

from _utils.pdf_generator import generate_tenant_pdf
from _utils.email_sender import send_tenant_email

app = FastAPI(title="Tenant Application API")

# Allow React / Frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, change to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_phone(phone: str) -> bool:
    # Simple regex to check for numbers, spaces, plus, dashes, parens
    pattern = re.compile(r'^[\+\(\)\s\-0-9]{7,20}$')
    return bool(pattern.match(phone))

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Tenant API is running"}

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

@app.post("/api/submit")
async def submit_application(payload: ApplicationData):
    try:
        # 1. Validation
        if not payload.fullName.strip() or not payload.address.strip() or not payload.peopleDetails.strip() or not payload.occupation.strip() or not payload.moveInDate.strip():
            raise HTTPException(status_code=400, detail="Missing required fields.")
            
        if not validate_phone(payload.phone):
            raise HTTPException(status_code=400, detail="Invalid phone number format.")
            
        # Check eligibility checkboxes
        if not all([payload.rule1, payload.rule2, payload.rule3, payload.rule4, payload.rule5, payload.rule6]):
            raise HTTPException(status_code=400, detail="All eligibility rules must be accepted.")

        # 2. Collect Data dictionary (exclude base64 explicitly for dict passing)
        data = payload.dict(exclude={"cnic_base64", "cnic_filename"})
        
        # 3. Read CNIC File from base64
        cnic_content = None
        cnic_filename = None
        if payload.cnic_base64:
            # Extract base64 part
            if "," in payload.cnic_base64:
                base64_str = payload.cnic_base64.split(",")[1]
            else:
                base64_str = payload.cnic_base64
            cnic_content = base64.b64decode(base64_str)
            
            if len(cnic_content) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="CNIC image must be less than 5MB.")
            cnic_filename = payload.cnic_filename

        # 4. Generate PDF
        pdf_buffer = generate_tenant_pdf(data, cnic_content)
        
        # 5. Send Email
        success = send_tenant_email(pdf_buffer, payload.fullName, cnic_content, cnic_filename)
        
        if success:
            return {"status": "success", "message": "Application submitted successfully."}
        else:
            return {"status": "warning", "message": "Application processed but email could not be sent (missing SMTP config)."}
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your application.")

