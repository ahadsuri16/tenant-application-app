import os
import smtplib
import io
from email.message import EmailMessage

def send_tenant_email(pdf_buffer: io.BytesIO, applicant_name: str, cnic_content: bytes = None, cnic_filename: str = None):
    """
    Sends email with PDF attachment via Gmail SMTP.
    Requires EMAIL_USER and EMAIL_PASS (Gmail App Password) environment variables.
    """
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    recipient = os.environ.get('EMAIL_RECIPIENT', email_user)

    if not email_user or not email_pass:
        print("Warning: EMAIL_USER or EMAIL_PASS not set.")
        return False

    msg = EmailMessage()
    msg['Subject'] = f"New Tenant Application: {applicant_name}"
    msg['From'] = email_user
    msg['To'] = recipient
    msg.set_content(f"""Hello,

A new tenant application has been submitted by {applicant_name}.

Please find the full structured application attached as a PDF.
{f"The applicant's CNIC image is also attached." if cnic_content else ""}

This email was generated automatically by the Tenant Application Platform.
""")

    # Attach PDF
    pdf_buffer.seek(0)
    msg.add_attachment(
        pdf_buffer.read(),
        maintype='application',
        subtype='pdf',
        filename=f"Tenant_Application_{applicant_name.replace(' ', '_')}.pdf"
    )

    # Attach CNIC image if provided
    if cnic_content and cnic_filename:
        ext = cnic_filename.rsplit('.', 1)[-1].lower()
        subtype = 'jpeg' if ext in ('jpg', 'jpeg') else ext if ext in ('png', 'gif', 'webp') else 'octet-stream'
        maintype = 'image' if subtype != 'octet-stream' else 'application'
        msg.add_attachment(
            cnic_content,
            maintype=maintype,
            subtype=subtype,
            filename=f"CNIC_{applicant_name.replace(' ', '_')}.{ext}"
        )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as smtp:
            smtp.login(email_user, email_pass)
            smtp.send_message(msg)
        print(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"SMTP error: {e}")
        raise e
