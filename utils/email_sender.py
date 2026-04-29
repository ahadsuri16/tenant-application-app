import os
import io
import base64
import resend

def send_tenant_email(pdf_buffer: io.BytesIO, applicant_name: str, cnic_content: bytes = None, cnic_filename: str = None):
    """
    Sends email with PDF attachment via Resend HTTP API (works on Railway free tier).
    Requires RESEND_API_KEY environment variable.
    """
    resend.api_key = os.environ.get('RESEND_API_KEY')
    recipient = os.environ.get('EMAIL_RECIPIENT', 'ahadsuri804@gmail.com')

    if not resend.api_key:
        print("Warning: RESEND_API_KEY not set.")
        return False

    # PDF attachment
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.read()
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

    attachments = [
        {
            "filename": f"Tenant_Application_{applicant_name.replace(' ', '_')}.pdf",
            "content": pdf_b64
        }
    ]

    # CNIC attachment
    if cnic_content and cnic_filename:
        ext = cnic_filename.rsplit('.', 1)[-1].lower()
        cnic_b64 = base64.b64encode(cnic_content).decode('utf-8')
        attachments.append({
            "filename": f"CNIC_{applicant_name.replace(' ', '_')}.{ext}",
            "content": cnic_b64
        })

    params = {
        "from": "onboarding@resend.dev",
        "to": [recipient],
        "subject": f"New Tenant Application: {applicant_name}",
        "html": f"<p>A new tenant application has been submitted by <b>{applicant_name}</b>.</p><p>The full structured PDF is attached to this email.</p>",
        "attachments": attachments
    }

    try:
        resend.Emails.send(params)
        print(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"Resend error: {e}")
        raise e
