from fpdf import FPDF
import io
import base64
from datetime import datetime

class TenantPDF(FPDF):
    def header(self):
        self.set_fill_color(16, 185, 129)  # emerald green
        self.rect(0, 0, 210, 22, 'F')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.set_y(5)
        self.cell(0, 12, 'Tenant Application Form', align='C')
        self.set_text_color(0, 0, 0)
        self.ln(18)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%d %B %Y at %H:%M")}  |  Page {self.page_no()}', align='C')

def section_title(pdf, title):
    pdf.set_fill_color(240, 253, 250)
    pdf.set_draw_color(16, 185, 129)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(5, 150, 105)
    pdf.cell(0, 9, f'  {title}', border='LB', fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

def data_row(pdf, label, value):
    if not value:
        return
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(65, 8, label, border=1, fill=True)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(125, 8, str(value), border=1, fill=True, ln=True)

def generate_tenant_pdf(data: dict, cnic_content: bytes = None) -> io.BytesIO:
    pdf = TenantPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(12, 28, 12)

    # --- Personal Information ---
    section_title(pdf, 'Personal Information')
    data_row(pdf, 'Full Name', data.get('fullName'))
    data_row(pdf, 'Phone Number', data.get('phone'))
    data_row(pdf, 'Current Address', data.get('address'))
    pdf.ln(4)

    # --- Tenant Details ---
    section_title(pdf, 'Tenant Details')
    data_row(pdf, 'People Moving In', data.get('peopleDetails'))
    data_row(pdf, 'Has Pets', data.get('hasPets'))
    data_row(pdf, 'Pet Details', data.get('petDetails'))
    pdf.ln(4)

    # --- Employment ---
    section_title(pdf, 'Employment & Income')
    data_row(pdf, 'Occupation', data.get('occupation'))
    data_row(pdf, 'Company / Employer', data.get('company'))
    data_row(pdf, 'Job Type', data.get('jobType'))
    data_row(pdf, 'Business Info', data.get('businessInfo'))
    data_row(pdf, 'Institute / University', data.get('institute'))
    data_row(pdf, 'Student Income Source', data.get('studentIncome'))
    data_row(pdf, 'Income Source Details', data.get('incomeSourceDetails'))
    data_row(pdf, 'Monthly Income (PKR)', data.get('income'))
    data_row(pdf, 'Employment Duration', data.get('employmentDuration'))
    pdf.ln(4)

    # --- Preferences ---
    section_title(pdf, 'Rental Preferences')
    data_row(pdf, 'Preferred Move-in Date', data.get('moveInDate'))
    data_row(pdf, 'Intended Stay Duration', data.get('stayDuration'))
    data_row(pdf, 'Rent Budget (PKR)', data.get('rentRange'))
    data_row(pdf, 'Security Deposit', data.get('securityDeposit'))
    pdf.ln(4)

    # --- Rental History ---
    section_title(pdf, 'Rental History')
    data_row(pdf, 'Rented Before?', data.get('rentedBefore'))
    data_row(pdf, 'Previous Landlord', data.get('previousLandlord'))
    data_row(pdf, 'Reason for Leaving', data.get('reasonForLeaving'))
    data_row(pdf, 'Legal Issues?', data.get('legalIssues'))
    pdf.ln(4)

    # --- Eligibility ---
    section_title(pdf, 'Eligibility Agreement')
    rules = [
        ('rule1', 'No subletting without permission'),
        ('rule2', 'No illegal activities'),
        ('rule3', 'No structural changes'),
        ('rule4', 'Maintain cleanliness'),
        ('rule5', 'Timely rent payment'),
        ('rule6', 'No loud noise / disturbances'),
    ]
    for key, label in rules:
        val = 'Agreed' if data.get(key) else 'Not Agreed'
        data_row(pdf, label, val)
    pdf.ln(4)

    # --- CNIC Image ---
    if cnic_content:
        pdf.add_page()
        section_title(pdf, 'CNIC / ID Image')
        pdf.ln(4)
        try:
            import tempfile, os
            suffix = '.jpg'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(cnic_content)
                tmp_path = tmp.name
            pdf.image(tmp_path, x=12, w=186)
            os.unlink(tmp_path)
        except Exception as e:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 10, f'[CNIC image could not be embedded: {e}]', ln=True)

    buffer = io.BytesIO()
    pdf_bytes = pdf.output()
    buffer.write(pdf_bytes)
    buffer.seek(0)
    return buffer
