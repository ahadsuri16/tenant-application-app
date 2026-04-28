from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import ValidationError
import re
import os

from utils.pdf_generator import generate_tenant_pdf
from utils.email_sender import send_tenant_email

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

@app.post("/submit")
async def submit_application(
    # Basic
    fullName: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    
    # CNIC File (Optional or Required depending on strictness, we'll make it optional in API but required in UI)
    cnic: UploadFile = File(None),
    
    # Tenant Details
    peopleDetails: str = Form(...),
    hasPets: str = Form(None),
    petDetails: str = Form(None),
    
    # Employment
    occupation: str = Form(...),
    company: str = Form(None),
    jobType: str = Form(None),
    businessInfo: str = Form(None),
    institute: str = Form(None),
    studentIncome: str = Form(None),
    incomeSourceDetails: str = Form(None),
    income: str = Form(None),
    employmentDuration: str = Form(None),
    
    # Preferences
    moveInDate: str = Form(...),
    stayDuration: str = Form(None),
    rentRange: str = Form(None),
    securityDeposit: str = Form(None),
    
    # History
    rentedBefore: str = Form(None),
    previousLandlord: str = Form(None),
    reasonForLeaving: str = Form(None),
    
    # Rules
    rule1: str = Form(None),
    rule2: str = Form(None),
    rule3: str = Form(None),
    rule4: str = Form(None),
    rule5: str = Form(None),
    rule6: str = Form(None),
    legalIssues: str = Form(None)
):
    try:
        # 1. Validation
        if not fullName.strip() or not address.strip() or not peopleDetails.strip() or not occupation.strip() or not moveInDate.strip():
            raise HTTPException(status_code=400, detail="Missing required fields.")
            
        if not validate_phone(phone):
            raise HTTPException(status_code=400, detail="Invalid phone number format.")
            
        # Check eligibility checkboxes (in the UI they must be checked, but we double check backend if they sent "on")
        if not all([rule1, rule2, rule3, rule4, rule5, rule6]):
            raise HTTPException(status_code=400, detail="All eligibility rules must be accepted.")

        # 2. Collect Data dictionary
        data = {
            "fullName": fullName,
            "phone": phone,
            "address": address,
            "peopleDetails": peopleDetails,
            "hasPets": hasPets,
            "petDetails": petDetails,
            "occupation": occupation,
            "company": company,
            "jobType": jobType,
            "businessInfo": businessInfo,
            "institute": institute,
            "studentIncome": studentIncome,
            "incomeSourceDetails": incomeSourceDetails,
            "income": income,
            "employmentDuration": employmentDuration,
            "moveInDate": moveInDate,
            "stayDuration": stayDuration,
            "rentRange": rentRange,
            "securityDeposit": securityDeposit,
            "rentedBefore": rentedBefore,
            "previousLandlord": previousLandlord,
            "reasonForLeaving": reasonForLeaving,
            "legalIssues": legalIssues
        }
        
        # 3. Read CNIC File
        cnic_content = None
        cnic_filename = None
        if cnic and cnic.filename:
            # Basic size check (e.g., < 5MB)
            cnic_content = await cnic.read()
            if len(cnic_content) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="CNIC image must be less than 5MB.")
            cnic_filename = cnic.filename

        # 4. Generate PDF
        pdf_buffer = generate_tenant_pdf(data, cnic_content)
        
        # 5. Send Email
        # If EMAIL_USER is not configured in env, this will gracefully fail or skip
        success = send_tenant_email(pdf_buffer, fullName, None, None)
        
        if success:
            return {"status": "success", "message": "Application submitted successfully."}
        else:
            return {"status": "warning", "message": "Application processed but email could not be sent (missing SMTP config)."}
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your application.")

# Mount frontend directory for easy deployment
frontend_path = os.path.join(os.path.dirname(__file__), "..")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/style.css")
def serve_css():
    return FileResponse(os.path.join(frontend_path, "style.css"))

# Run with: uvicorn app:app --reload
