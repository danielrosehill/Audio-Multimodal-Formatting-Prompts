#!/usr/bin/env python3
"""
Generate PDF compilations for each run.
Each prompt gets its own page with title, description, and prompt content.
"""

import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

RUNS_DIR = Path("runs")


def create_pdf_for_run(json_file: Path):
    """Create a PDF document for a run with one prompt per page."""

    # Load the JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Determine run number from filename
    run_name = data.get('run_name', json_file.stem)
    run_num = run_name.split('_')[0].replace('run', '')

    # Create PDF in outputs/runX/pdf/
    pdf_dir = Path("outputs") / f"run{run_num}" / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_filename = pdf_dir / f"{json_file.stem}.pdf"

    # Create PDF document
    doc = SimpleDocTemplate(
        str(pdf_filename),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2C3E50',
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Custom description style
    description_style = ParagraphStyle(
        'CustomDescription',
        parent=styles['Normal'],
        fontSize=12,
        textColor='#34495E',
        spaceAfter=20,
        alignment=TA_LEFT,
        fontName='Helvetica-Oblique',
        leftIndent=20,
        rightIndent=20
    )

    # Custom prompt style
    prompt_style = ParagraphStyle(
        'CustomPrompt',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#000000',
        spaceAfter=12,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leftIndent=10,
        rightIndent=10,
        leading=16
    )

    # Section header style
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#7F8C8D',
        spaceAfter=12,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )

    # Cover page
    elements.append(Spacer(1, 2*inch))

    run_title = data.get('run_name', 'Prompt Collection').replace('_', ' ').title()
    elements.append(Paragraph(run_title, title_style))
    elements.append(Spacer(1, 0.5*inch))

    metadata_text = f"""
    <b>Generated:</b> {data.get('generated', 'N/A')}<br/>
    <b>Model:</b> {data.get('model', 'N/A')}<br/>
    <b>Total Prompts:</b> {data.get('count', 0)}<br/>
    <b>Source:</b> {data.get('prompt_file', 'N/A')}
    """
    elements.append(Paragraph(metadata_text, description_style))
    elements.append(PageBreak())

    # Add each prompt on its own page
    for idx, prompt_data in enumerate(data.get('prompts', []), 1):
        # Title
        title_text = f"{idx}. {prompt_data.get('name', 'Untitled')}"
        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 0.3*inch))

        # Description section
        elements.append(Paragraph("Description", section_style))
        desc_text = prompt_data.get('description', 'No description available.')
        elements.append(Paragraph(desc_text, description_style))
        elements.append(Spacer(1, 0.3*inch))

        # Prompt section
        elements.append(Paragraph("System Prompt", section_style))
        prompt_text = prompt_data.get('prompt', 'No prompt available.')
        # Escape special characters for ReportLab
        prompt_text = prompt_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Convert newlines to <br/> tags
        prompt_text = prompt_text.replace('\n', '<br/>')
        elements.append(Paragraph(prompt_text, prompt_style))

        # Add page break except for last prompt
        if idx < len(data.get('prompts', [])):
            elements.append(PageBreak())

    # Build PDF
    doc.build(elements)
    print(f"✓ PDF created: {pdf_filename}")
    return pdf_filename


def main():
    """Generate PDFs for all run JSON files."""
    print("Generating PDFs for all runs...\n")

    # Find all JSON files in runs directory
    json_files = sorted(RUNS_DIR.glob("run*.json"))

    if not json_files:
        print("No run JSON files found in runs/ directory")
        return

    pdf_files = []
    for json_file in json_files:
        print(f"Processing {json_file.name}...")
        try:
            pdf_file = create_pdf_for_run(json_file)
            pdf_files.append(pdf_file)
        except Exception as e:
            print(f"✗ Error processing {json_file.name}: {e}")

    print(f"\n{'='*60}")
    print(f"Successfully generated {len(pdf_files)} PDF(s)")
    print(f"{'='*60}")

    for pdf in pdf_files:
        print(f"  - {pdf}")


if __name__ == "__main__":
    main()
