import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

def clean_markdown_for_pdf(text):
    # Format bold text **word** to <b>word</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Parse inline markdown links [text](url) to html style <a href="url">text</a>
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" color="#e65c00"><b>\1</b></a>', text)
    return text

def parse_content_to_story(content, styles, story):
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Times-Roman',
        fontSize=10.5,
        leading=15,
        spaceAfter=7,
        textColor=HexColor('#2b2b2b')
    )
    
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10.5,
        leading=15,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5,
        textColor=HexColor('#2b2b2b')
    )

    paragraphs = content.split('\n\n')
    for p in paragraphs:
        p_text = p.strip()
        if not p_text:
            continue
            
        # Heading 1
        if p_text.startswith('# '):
            h_text = p_text[2:].strip()
            h_style = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, leading=20, spaceAfter=10, spaceBefore=15, textColor=HexColor('#e65c00'))
            story.append(Paragraph(h_text, h_style))
        # Heading 2
        elif p_text.startswith('## '):
            h_text = p_text[3:].strip()
            h_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=16, spaceAfter=8, spaceBefore=12, textColor=HexColor('#e65c00'))
            story.append(Paragraph(h_text, h_style))
        # Heading 3
        elif p_text.startswith('### '):
            h_text = p_text[4:].strip()
            h_style = ParagraphStyle('H3', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=11, leading=14, spaceAfter=6, spaceBefore=10, textColor=HexColor('#e65c00'))
            story.append(Paragraph(h_text, h_style))
        # Bullet list items
        elif p_text.startswith('- ') or p_text.startswith('* '):
            # Split items on newlines starting with - or *
            items = re.split(r'\n[\-\*]\s+', p_text)
            for item in items:
                item_text = item.strip()
                if item_text.startswith('- ') or item_text.startswith('* '):
                    item_text = item_text[2:]
                if item_text:
                    cleaned = clean_markdown_for_pdf(item_text)
                    story.append(Paragraph(f"&bull; {cleaned}", bullet_style))
        else:
            cleaned = clean_markdown_for_pdf(p_text)
            cleaned = cleaned.replace('\n', '<br/>')
            story.append(Paragraph(cleaned, body_style))

def build_pdf_document(title, subtitle, sections):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom Title & Header styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        spaceAfter=6,
        textColor=HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=14,
        spaceAfter=15,
        textColor=HexColor('#555555')
    )
    
    divider_style = ParagraphStyle(
        'DocDivider',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=1,
        leading=1,
        spaceAfter=15,
        backColor=HexColor('#dddddd')
    )

    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, subtitle_style))
    story.append(Paragraph("", divider_style))
    story.append(Spacer(1, 10))
    
    for idx, (sec_title, sec_content) in enumerate(sections):
        if idx > 0 and sec_title == "PAGE_BREAK":
            story.append(PageBreak())
            continue
            
        if sec_title:
            sec_title_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=15,
                leading=19,
                spaceAfter=10,
                spaceBefore=15,
                textColor=HexColor('#2c3e50')
            )
            story.append(Paragraph(sec_title, sec_title_style))
            
        parse_content_to_story(sec_content, styles, story)
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_report_pdf(topic, report_content):
    return build_pdf_document(
        title="Research Report",
        subtitle=f"Topic: {topic}",
        sections=[(None, report_content)]
    )

def generate_critic_pdf(topic, critic_content):
    return build_pdf_document(
        title="Critic Evaluation",
        subtitle=f"Topic: {topic}",
        sections=[(None, critic_content)]
    )

def generate_combined_pdf(topic, report_content, critic_content):
    return build_pdf_document(
        title="Research & Evaluation Portfolio",
        subtitle=f"Topic: {topic}",
        sections=[
            ("Research Report", report_content),
            ("PAGE_BREAK", ""),
            ("Critic Evaluation", critic_content)
        ]
    )
