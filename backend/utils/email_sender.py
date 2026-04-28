import os
import io
import resend

def send_tenant_email(pdf_buffer: io.BytesIO, applicant_name: str, cnic_content: bytes = None, cnic_filename: str = None):
    """
    Sends an email to the property manager with the PDF and CNIC attached using Resend HTTP API.
    """
    resend.api_key = os.environ.get('RESEND_API_KEY')
    recipient = "ahadsuri804@gmail.com"
    
    if not resend.api_key:
        print("Warning: RESEND_API_KEY not set. Email will not be sent.")
        return False
        
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.read()
    
    attachments = [
        {
            "filename": f"Tenant_Application_{applicant_name.replace(' ', '_')}.pdf",
            "content": list(pdf_bytes)
        }
    ]
    
    if cnic_content and cnic_filename:
        attachments.append({
            "filename": f"CNIC_{applicant_name.replace(' ', '_')}_{cnic_filename}",
            "content": list(cnic_content)
        })
        
    params = {
        "from": "onboarding@resend.dev",
        "to": [recipient],
        "subject": f"New Tenant Application: {applicant_name}",
        "html": f"<p>A new tenant application has been submitted by <b>{applicant_name}</b>.</p><p>Please find the structured application and CNIC attached to this email.</p>",
        "attachments": attachments
    }
    
    try:
        email = resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Error sending email via Resend: {str(e)}")
        raise e
