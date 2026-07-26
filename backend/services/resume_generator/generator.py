import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth  # Imported to calculate text width
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    FrameBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    Image
)

from resume_generator.data_format import convert_data_to_format

# ----------------------------------------------------------------------
# 2. ATS-Optimized PDF Builder
# ----------------------------------------------------------------------
def build_ats_friendly_pdf(data, output_path):
    # Setup document geometry
    margin = 36
    page_width, page_height = A4
    
    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin
    )
    
    # Calculate Frame Dimensions
    header_height = 60
    footer_height = 60  
    content_height = page_height - (2 * margin) - header_height - footer_height
    
    # Define Column Widths (58% Left, 42% Right)
    gap = 20
    available_width = page_width - (2 * margin) - gap
    left_col_width = available_width * 0.58
    right_col_width = available_width * 0.42
    
    # Define Frames
    frame_header = Frame(
        margin, page_height - margin - header_height, 
        page_width - (2 * margin), header_height, 
        id='header', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
    )
    
    frame_left = Frame(
        margin, margin + footer_height, 
        left_col_width, content_height, 
        id='left', leftPadding=0, rightPadding=10, topPadding=0, bottomPadding=0
    )
    
    frame_right = Frame(
        margin + left_col_width + gap, margin + footer_height, 
        right_col_width, content_height, 
        id='right', leftPadding=10, rightPadding=0, topPadding=0, bottomPadding=0
    )

    frame_footer = Frame(
        margin, margin,
        page_width - (2 * margin), footer_height,
        id='footer', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0
    )
    
    doc.addPageTemplates([PageTemplate(id='Layout', frames=[frame_header, frame_left, frame_right, frame_footer])])
    
    # Styles
    styles = getSampleStyleSheet()
    
    style_header = ParagraphStyle(
        'HeaderStyle', fontName='Helvetica-Bold', fontSize=15, leading=16,
        alignment=TA_CENTER, textColor=colors.HexColor('#F49F47')
    )
    style_sub_header = ParagraphStyle(
        'SubHeaderStyle', fontName='Helvetica', fontSize=12, leading=14,
        alignment=TA_CENTER, textColor=colors.HexColor('#F49F47')
    )
    style_body = ParagraphStyle('BodyStyle', fontName='Helvetica', fontSize=9, leading=12)
    style_bullet = ParagraphStyle(
        'BulletStyle', fontName='Helvetica', fontSize=8.5, leading=12,
        leftIndent=10, firstLineIndent=-5
    )
    style_footer_text = ParagraphStyle(
        'FooterText', fontName='Helvetica', fontSize=8, leading=12, textColor=colors.black
    )

    def create_section_header(title):
        title_p = Paragraph(f'<b><font color="#F49F47" size=11>{title.upper()}</font></b>', styles['Normal'])
        line = HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceBefore=0, spaceAfter=0)
        
        t = Table([[title_p], [line]], colWidths=['*'])
        t.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (0,0), 3),
            ('BOTTOMPADDING', (0,1), (0,1), 0),
        ]))
        return t

    story = []

    # ------------------------------------------------------------------
    # FRAME 1: Header 
    # ------------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph(data["name"], style_header))
    story.append(Spacer(1, 4))
    story.append(Paragraph(data["role"], style_sub_header))
    story.append(FrameBreak()) 

    # ------------------------------------------------------------------
    # FRAME 2: Left Column 
    # ------------------------------------------------------------------
    story.append(create_section_header("EXPERIENCE"))
    story.append(Spacer(1, 15))
    
    for exp in data["experience"]:
        story.append(Paragraph(f'<font color="#F49F47" size=10>{exp["title"]}</font>', style_body))
        story.append(Paragraph(f'<b><font color="#F49F47" size=9>{exp["company"]}</font></b>', style_body))
        story.append(Paragraph(f'<font color="#7F7F7F" size=8> {exp["date"]} &nbsp;&nbsp;&nbsp; {exp["location"]}</font>', style_body))
        story.append(Spacer(1, 4))
        for bullet in exp["desc"]:
            story.append(Paragraph(f"• {bullet}", style_bullet))
        story.append(Spacer(1, 15))


    story.append(create_section_header("EDUCATION"))
    story.append(Spacer(1, 15))
    
    for edu in data.get("education", []):
        story.append(Paragraph(f'<b><font size=9.5>{edu.get("degree", "")}</font></b>', style_body))
        story.append(Paragraph(f'<b><font color="#0070C0" size=8.5>{edu.get("college", "")}</font></b>', style_body))
        
        # Safely handle missing dates or locations (prevents "None" from printing)
        date_text = edu.get("date", "")
        loc_text = edu.get("location")
        loc_str = f" &nbsp;&nbsp;&nbsp; {loc_text}" if loc_text and str(loc_text).strip().lower() != "none" else ""
        story.append(Paragraph(f'<font color="#7F7F7F" size=8> {date_text}{loc_str}</font>', style_body))
        
        story.append(Spacer(1, 2))
        
        # Safely handle 'desc' based on your mapping (it will be a string or None)
        desc_data = edu.get("desc")
        
        # Convert to a list so it renders as a single bullet point
        if not desc_data:
            desc_list = []
        elif isinstance(desc_data, str):
            desc_list = [desc_data]
        else:
            desc_list = desc_data
            
        for bullet in desc_list:
            story.append(Paragraph(f"• {bullet}", style_bullet))
            
        story.append(Spacer(1, 15))


    story.append(FrameBreak())

    # ------------------------------------------------------------------
    # FRAME 3: Right Column 
    # ------------------------------------------------------------------
    story.append(create_section_header("SUMMARY"))
    story.append(Spacer(1, 15))
    if data["summary"]:
        story.append(Paragraph(data["summary"], style_body))
    story.append(Spacer(1, 30)) 
    
    # --- DYNAMIC SKILLS SECTION ---
    story.append(create_section_header("SKILLS"))
    story.append(Spacer(1, 10)) 
    
    skill_style = ParagraphStyle(
        'Skill', fontName='Helvetica-Bold', fontSize=9.5, 
        textColor=colors.HexColor('#2F3B44'), alignment=TA_CENTER
    )
    
    current_row = []
    current_row_width = 0
    max_width = right_col_width
    
    for skill in data["skills"]:
        # Accurately calculate the text width and add minimal padding
        text_width = stringWidth(skill, 'Helvetica-Bold', 9.5)
        box_width = text_width + 16 # 8pt padding on left/right
        
        # Tiny inner table for the individual skill box
        skill_box = Table([[Paragraph(skill, skill_style)]], colWidths=[box_width], rowHeights=[18])
        skill_box.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#A0A0A0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        
        # Wrap to next row if current box exceeds the available column width
        if current_row_width + box_width + 6 > max_width and current_row:
            row_table = Table([current_row], hAlign='LEFT')
            row_table.setStyle(TableStyle([
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 6), # 6pt horizontal gap between boxes
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(row_table)
            story.append(Spacer(1, 4)) # 4pt vertical gap between rows
            
            # Reset for new row
            current_row = [skill_box]
            current_row_width = box_width
        else:
            current_row.append(skill_box)
            current_row_width += box_width + 6 # Include the gap in running width
            
    # Flush the last remaining row
    if current_row:
        row_table = Table([current_row], hAlign='LEFT')
        row_table.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(row_table)

    story.append(FrameBreak())

    # ------------------------------------------------------------------
    # FRAME 4: Footer
    # ------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=0, spaceAfter=8))
    
    current_directory = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
    logo_filename = os.path.join(current_directory, "logo.png")
    
    if os.path.exists(logo_filename):
        logo_item = Image(logo_filename, width=150, height=35)
        logo_item.hAlign = 'LEFT'
    else:
        logo_item = Paragraph("<i>[Missing logo.png]</i>", style_body)

    footer_text = f"""
    {data['footer']['address_1']}<br/>
    {data['footer']['address_2']}<br/>
    {data['footer']['contact']}
    """
    text_item = Paragraph(footer_text, style_footer_text)

    footer_table = Table([[logo_item, text_item]], colWidths=[left_col_width + gap, right_col_width])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(footer_table)

    # Build Document
    doc.build(story)
    print(f"Successfully generated ATS-friendly PDF with Compact Skills: {output_path}")


def build_format_resume(resume_metadata):
    output_directory = "reportlab_output"
    os.makedirs(output_directory, exist_ok=True)

    resume_data = convert_data_to_format(resume_metadata)


    build_ats_friendly_pdf(resume_data, os.path.join(output_directory, "sample.pdf"))