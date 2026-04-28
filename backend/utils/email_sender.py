import os
import resend

def send_tenant_email(data: dict, cnic_content: bytes = None, cnic_filename: str = None):
    """
    Sends a rich HTML email to the property manager with the applicant's data and CNIC attached using Resend.
    """
    resend.api_key = os.environ.get('RESEND_API_KEY')
    recipient = "ahadsuri804@gmail.com"
    applicant_name = data.get("fullName", "Unknown")
    
    if not resend.api_key:
        print("Warning: RESEND_API_KEY not set. Email will not be sent.")
        return False
        
    attachments = []
    
    if cnic_content and cnic_filename:
        attachments.append({
            "filename": f"CNIC_{applicant_name.replace(' ', '_')}_{cnic_filename}",
            "content": list(cnic_content)
        })
        
    # Build Rich HTML Table
    table_rows = ""
    for key, value in data.items():
        if value:
            # Format key (e.g. 'fullName' -> 'Full Name')
            formatted_key = ''.join([' '+c if c.isupper() else c for c in key]).title()
            table_rows += f'<tr><td style="background-color: #f3f4f6; padding: 10px; font-weight: bold; width: 35%; border-bottom: 1px solid #e5e7eb;">{formatted_key}</td><td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{value}</td></tr>'

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #10b981; text-align: center;">New Tenant Application</h2>
        <p style="text-align: center; color: #6b7280; margin-bottom: 30px;">An application has been submitted by <b>{applicant_name}</b>.</p>
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb;">
            {table_rows}
        </table>
        <p style="margin-top: 30px; font-size: 12px; color: #9ca3af; text-align: center;">Generated automatically by Tenant Application Platform</p>
    </div>
    """

    params = {
        "from": "onboarding@resend.dev",
        "to": [recipient],
        "subject": f"New Tenant Application: {applicant_name}",
        "html": html_content
    }
    
    if attachments:
        params["attachments"] = attachments
    
    try:
        email = resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Error sending email via Resend: {str(e)}")
        raise e
