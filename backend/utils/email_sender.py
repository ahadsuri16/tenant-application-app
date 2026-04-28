import os
import smtplib
from email.message import EmailMessage
import io

def send_tenant_email(pdf_buffer: io.BytesIO, applicant_name: str, cnic_content: bytes = None, cnic_filename: str = None):
    """
    Sends an email to the property manager with the PDF and CNIC attached.
    """
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    recipient = "ahadsuri804@gmail.com"
    
    if not email_user or not email_pass:
        print("Warning: EMAIL_USER or EMAIL_PASS not set. Email will not be sent.")
        return False
        
    msg = EmailMessage()
    msg['Subject'] = f"New Tenant Application: {applicant_name}"
    msg['From'] = email_user
    msg['To'] = recipient
    
    body = f"""
    Hello,
    
    A new tenant application has been submitted by {applicant_name}.
    
    Please find the structured application attached as a PDF.
    """
    
    if cnic_filename:
        body += "\nThe applicant's CNIC image is also attached to this email."
        
    msg.set_content(body)
    
    # Attach PDF
    pdf_buffer.seek(0)
    msg.add_attachment(
        pdf_buffer.read(),
        maintype='application',
        subtype='pdf',
        filename=f"Tenant_Application_{applicant_name.replace(' ', '_')}.pdf"
    )
    
    # Attach CNIC if exists
    if cnic_content and cnic_filename:
        # Determine subtype roughly from filename or default to octet-stream
        ext = cnic_filename.split('.')[-1].lower()
        subtype = 'jpeg' if ext in ['jpg', 'jpeg'] else 'png' if ext == 'png' else 'octet-stream'
        maintype = 'image' if subtype in ['jpeg', 'png'] else 'application'
        
        msg.add_attachment(
            cnic_content,
            maintype=maintype,
            subtype=subtype,
            filename=f"CNIC_{applicant_name.replace(' ', '_')}.{ext}"
        )
        
    # Send email
    try:
        # Use SMTP_SSL for port 465
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_user, email_pass)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise e
