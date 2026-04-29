import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage

def generate_tenant_pdf(data: dict, cnic_content: bytes = None) -> io.BytesIO:
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

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=20,
        alignment=1
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        spaceAfter=4,
        spaceBefore=14
    )
    normal_style = ParagraphStyle(
        'Normal2',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#1f2937')
    )

    story = []

    # Header
    story.append(Paragraph("Tenant Application Form", title_style))
    story.append(Paragraph(f"Submitted on {datetime.now().strftime('%d %B %Y at %H:%M')}", subtitle_style))
    story.append(Spacer(1, 0.1 * inch))

    def section_table(title, rows):
        story.append(Spacer(1, 0.15 * inch))
        # Section header row
        header = Table([[Paragraph(title, section_style)]], colWidths=[530])
        header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#10b981')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#10b981')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('ROUNDEDCORNERS', [4, 4, 0, 0]),
        ]))
        story.append(header)

        table_data = []
        for label, value in rows:
            if value:
                table_data.append([
                    Paragraph(f'<b>{label}</b>', normal_style),
                    Paragraph(str(value), normal_style)
                ])

        if table_data:
            t = Table(table_data, colWidths=[175, 355])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1fae5')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(t)

    # Sections
    section_table("Personal Information", [
        ("Full Name", data.get("fullName")),
        ("Phone Number", data.get("phone")),
        ("Current Address", data.get("address")),
    ])

    section_table("Tenant Details", [
        ("People Moving In", data.get("peopleDetails")),
        ("Has Pets", data.get("hasPets")),
        ("Pet Details", data.get("petDetails")),
    ])

    section_table("Employment & Income", [
        ("Occupation", data.get("occupation")),
        ("Company / Employer", data.get("company")),
        ("Job Type", data.get("jobType")),
        ("Business Info", data.get("businessInfo")),
        ("Institute", data.get("institute")),
        ("Student Income Source", data.get("studentIncome")),
        ("Income Source Details", data.get("incomeSourceDetails")),
        ("Monthly Income (PKR)", data.get("income")),
        ("Employment Duration", data.get("employmentDuration")),
    ])

    section_table("Rental Preferences", [
        ("Preferred Move-in Date", data.get("moveInDate")),
        ("Intended Stay Duration", data.get("stayDuration")),
        ("Rent Budget (PKR)", data.get("rentRange")),
        ("Security Deposit Ready", data.get("securityDeposit")),
    ])

    section_table("Rental History", [
        ("Rented Before?", data.get("rentedBefore")),
        ("Previous Landlord", data.get("previousLandlord")),
        ("Reason for Leaving", data.get("reasonForLeaving")),
        ("Legal Issues?", data.get("legalIssues")),
    ])

    section_table("Eligibility Agreement", [
        ("No subletting without permission", "✓ Agreed" if data.get("rule1") else "✗ Not Agreed"),
        ("No illegal activities", "✓ Agreed" if data.get("rule2") else "✗ Not Agreed"),
        ("No structural changes", "✓ Agreed" if data.get("rule3") else "✗ Not Agreed"),
        ("Maintain cleanliness", "✓ Agreed" if data.get("rule4") else "✗ Not Agreed"),
        ("Timely rent payment", "✓ Agreed" if data.get("rule5") else "✗ Not Agreed"),
        ("No loud noise / disturbances", "✓ Agreed" if data.get("rule6") else "✗ Not Agreed"),
    ])

    # CNIC Image
    if cnic_content:
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("CNIC / National ID Image", section_style))
        try:
            img_buf = io.BytesIO(cnic_content)
            pil_img = PILImage.open(img_buf)
            # Convert RGBA to RGB if needed
            if pil_img.mode in ('RGBA', 'P'):
                pil_img = pil_img.convert('RGB')
            # Resize to fit page width
            max_w = 5.2 * inch
            ratio = pil_img.height / pil_img.width
            img_h = max_w * ratio
            if img_h > 4 * inch:
                img_h = 4 * inch
                max_w = img_h / ratio
            img_buf.seek(0)
            rl_img = RLImage(img_buf, width=max_w, height=img_h)
            story.append(rl_img)
        except Exception as e:
            story.append(Paragraph(f"[CNIC image could not be embedded: {e}]", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
