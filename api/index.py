from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import os
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

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

def validate_phone(phone: str) -> bool:
    pattern = re.compile(r'^[\+\(\)\s\-0-9]{7,20}$')
    return bool(pattern.match(phone))

@app.post("/api/submit")
async def submit_application(payload: ApplicationData):
    try:
        if not payload.fullName.strip() or not payload.address.strip() or not payload.peopleDetails.strip() or not payload.occupation.strip() or not payload.moveInDate.strip():
            return {"status": "error", "detail": "Missing required fields."}, 400

        if not validate_phone(payload.phone):
            return {"status": "error", "detail": "Invalid phone number."}, 400

        if not all([payload.rule1, payload.rule2, payload.rule3, payload.rule4, payload.rule5, payload.rule6]):
            return {"status": "error", "detail": "All eligibility rules must be accepted."}, 400

        # Decode CNIC image
        cnic_content = None
        cnic_filename = None
        if payload.cnic_base64:
            raw = payload.cnic_base64
            if "," in raw:
                raw = raw.split(",")[1]
            cnic_content = base64.b64decode(raw)
            cnic_filename = payload.cnic_filename

        # Build application data dict
        data = payload.dict(exclude={"cnic_base64", "cnic_filename"})

        # Try to send email
        try:
            import resend
            resend.api_key = os.environ.get("RESEND_API_KEY", "")
            if not resend.api_key:
                raise ValueError("RESEND_API_KEY not set")

            # Build HTML table of all data
            rows = ""
            labels = {
                "fullName": "Full Name", "phone": "Phone", "address": "Address",
                "peopleDetails": "People Moving In", "hasPets": "Has Pets", "petDetails": "Pet Details",
                "occupation": "Occupation", "company": "Company", "jobType": "Job Type",
                "businessInfo": "Business Info", "institute": "Institute", "studentIncome": "Student Income",
                "incomeSourceDetails": "Income Source", "income": "Monthly Income", "employmentDuration": "Employment Duration",
                "moveInDate": "Move-in Date", "stayDuration": "Stay Duration", "rentRange": "Rent Budget",
                "securityDeposit": "Security Deposit", "rentedBefore": "Rented Before",
                "previousLandlord": "Previous Landlord", "reasonForLeaving": "Reason for Leaving",
                "legalIssues": "Legal Issues",
                "rule1": "No Subletting", "rule2": "No Illegal Activities", "rule3": "No Structural Changes",
                "rule4": "Maintain Cleanliness", "rule5": "Timely Rent", "rule6": "No Disturbances"
            }
            for key, label in labels.items():
                val = data.get(key)
                if val:
                    rows += f'<tr><td style="background:#f0fdf4;padding:8px 12px;font-weight:bold;border-bottom:1px solid #d1fae5;width:40%">{label}</td><td style="padding:8px 12px;border-bottom:1px solid #d1fae5">{val}</td></tr>'

            html = f"""
            <div style="font-family:Arial,sans-serif;max-width:650px;margin:0 auto">
              <div style="background:linear-gradient(135deg,#10b981,#059669);padding:24px;text-align:center;border-radius:8px 8px 0 0">
                <h1 style="color:white;margin:0;font-size:22px">New Tenant Application</h1>
              </div>
              <table style="width:100%;border-collapse:collapse;border:1px solid #d1fae5">
                {rows}
              </table>
              <p style="color:#6b7280;font-size:12px;text-align:center;margin-top:16px">Submitted automatically via Tenant Application Platform</p>
            </div>"""

            attachments = []
            if cnic_content and cnic_filename:
                attachments.append({
                    "filename": f"CNIC_{payload.fullName.replace(' ','_')}_{cnic_filename}",
                    "content": base64.b64encode(cnic_content).decode()
                })

            params = {
                "from": "onboarding@resend.dev",
                "to": ["ahadsuri804@gmail.com"],
                "subject": f"New Tenant Application: {payload.fullName}",
                "html": html
            }
            if attachments:
                params["attachments"] = attachments

            resend.Emails.send(params)
            return {"status": "success", "message": "Application submitted successfully."}

        except Exception as email_err:
            print(f"Email error: {email_err}")
            # Still return success to user — data was received
            return {"status": "warning", "message": f"Application received but email failed: {str(email_err)}"}

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"status": "error", "detail": str(e)}
