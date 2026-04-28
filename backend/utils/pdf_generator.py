import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_tenant_pdf(data: dict, cnic_content: bytes = None) -> io.BytesIO:
    """
    Generates a professional PDF for the Tenant Application.
    Returns a BytesIO object containing the PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=5,
        alignment=1, # Center
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor("#ffffff"),
        backColor=colors.HexColor("#334155"),
        spaceAfter=15,
        spaceBefore=25,
        borderPadding=(6, 10, 6, 10),
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )

    story = []
    
    # Title Block
    story.append(Paragraph("OFFICIAL RENTAL APPLICATION", title_style))
    story.append(Paragraph(f"Application ID: {datetime.now().strftime('%Y%m%d%H%M')} | Submitted: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", subtitle_style))
    
    def add_section(title, fields):
        story.append(Paragraph(title.upper(), heading_style))
        data_table = []
        for key, val in fields.items():
            if not val:
                val = "N/A"
            clean_key = Paragraph(f"<b>{key}</b>", normal_style)
            clean_val = Paragraph(str(val), normal_style)
            data_table.append([clean_key, clean_val])
            
        t = Table(data_table, colWidths=[180, 340])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
        ]))
        story.append(t)

    # Basic Info
    add_section("Personal Information", {
        "Full Name": data.get("fullName"),
        "Phone Number": data.get("phone"),
        "Permanent Address": data.get("address")
    })
    
    # Tenant Details
    add_section("Tenant Details", {
        "Occupants & Relation": data.get("peopleDetails"),
        "Has Pets?": data.get("hasPets", "No").title(),
        "Pet Details": data.get("petDetails") if data.get("hasPets") == "yes" else None
    })
    
    # Employment / Income
    occ = data.get("occupation", "").title()
    emp_details = {}
    emp_details["Occupation Status"] = occ
    
    if occ.lower() == "job":
        emp_details["Company Name"] = data.get("company")
        emp_details["Job Type"] = data.get("jobType", "").title()
    elif occ.lower() == "business":
        emp_details["Business Info"] = data.get("businessInfo")
    elif occ.lower() == "student":
        emp_details["Institute"] = data.get("institute")
        emp_details["Has Other Income?"] = data.get("studentIncome", "No").title()
        if data.get("studentIncome") == "yes":
            emp_details["Income Source"] = data.get("incomeSourceDetails")

    # Add shared income fields unless strictly a student with no income
    if data.get("income"):
        emp_details["Monthly Income Range"] = data.get("income").replace("_", " ").title()
    if data.get("employmentDuration"):
        emp_details["Employment Duration"] = data.get("employmentDuration")
        
    add_section("Employment & Income", emp_details)
    
    # Preferences
    add_section("Rental Preferences", {
        "Desired Move-In Date": data.get("moveInDate"),
        "Planned Stay Duration": data.get("stayDuration"),
        "Preferred Rent Range": data.get("rentRange"),
        "Can Pay Security Deposit?": data.get("securityDeposit", "Yes").title()
    })
    
    # History
    add_section("Rental History", {
        "Has Rented Before?": data.get("rentedBefore", "No").title(),
        "Previous Landlord Contact": data.get("previousLandlord") if data.get("rentedBefore") == "yes" else None,
        "Reason for Leaving": data.get("reasonForLeaving") if data.get("rentedBefore") == "yes" else None
    })
    
    # Rules
    add_section("Rules & Eligibility", {
        "Agreed to pay on/before 10th": "Yes",
        "No criminal history": "Yes",
        "Residential use only": "Yes",
        "Maintain peaceful environment": "Yes",
        "Follow house rules": "Yes",
        "Information is accurate": "Yes",
    })
    
    # CNIC Image
    if cnic_content:
        story.append(Spacer(1, 10))
        story.append(Paragraph("CNIC / IDENTIFICATION", heading_style))
        try:
            img = Image(io.BytesIO(cnic_content))
            # Scale image proportionally to fit page width roughly
            aspect = img.imageHeight / float(img.imageWidth)
            img.drawWidth = 400
            img.drawHeight = 400 * aspect
            img.hAlign = 'CENTER'
            story.append(img)
        except Exception as e:
            story.append(Paragraph("<i>[Image provided but could not be rendered in PDF. It may be an unsupported format.]</i>", normal_style))
    
    # Footer Notice
    story.append(Spacer(1, 30))
    story.append(Paragraph("<i>This document is automatically generated from a secure web form submission.</i>", ParagraphStyle('Footer', parent=normal_style, alignment=1, fontSize=9, textColor=colors.gray)))
    
    # Build
    doc.build(story)
    buffer.seek(0)
    return buffer
