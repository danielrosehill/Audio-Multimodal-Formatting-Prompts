#!/usr/bin/env python3
"""
Consolidate all prompts from the three runs into a single markdown and PDF.
"""

import json
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Run descriptions
RUN_DESCRIPTIONS = {
    "run1": "Batch generation of 10 diverse prompts",
    "run2": "Individual generation of 50 unique prompts with maximum diversity",
    "run3": "Deep ideation batch generation of 50+ prompts with creative edge cases"
}

def load_all_runs():
    """Load all JSON files from runs/ directory."""
    runs_dir = Path("runs")
    all_prompts = []

    for run_num in [1, 2, 3]:
        json_files = list(runs_dir.glob(f"run{run_num}_*.json"))
        if json_files:
            # Get the most recent file for this run
            json_file = max(json_files, key=lambda p: p.stat().st_mtime)

            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for prompt_data in data['prompts']:
                prompt_data['run_number'] = run_num
                prompt_data['run_description'] = RUN_DESCRIPTIONS[f"run{run_num}"]
                all_prompts.append(prompt_data)

    return all_prompts

def create_consolidated_markdown(prompts):
    """Create consolidated markdown file with all prompts."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("outputs/consolidated/markdown")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"all_prompts_{timestamp}.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Audio Multimodal Formatting Prompts - Consolidated\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Prompts**: {len(prompts)}\n\n")

        f.write("## Run Descriptions\n\n")
        for run_num in [1, 2, 3]:
            f.write(f"**Run {run_num}**: {RUN_DESCRIPTIONS[f'run{run_num}']}\n\n")

        f.write("---\n\n")

        # Group prompts by run
        for run_num in [1, 2, 3]:
            run_prompts = [p for p in prompts if p['run_number'] == run_num]
            f.write(f"## Run {run_num} ({len(run_prompts)} prompts)\n\n")
            f.write(f"*{RUN_DESCRIPTIONS[f'run{run_num}']}*\n\n")

            for idx, prompt in enumerate(run_prompts, 1):
                f.write(f"### {idx}. {prompt['name']}\n\n")
                f.write(f"**Description**: {prompt['description']}\n\n")
                f.write(f"**Prompt**:\n\n")
                f.write(f"```\n{prompt['prompt']}\n```\n\n")
                f.write("---\n\n")

    print(f"Created consolidated markdown: {output_file}")
    return output_file

def create_consolidated_pdf(prompts):
    """Create consolidated PDF with all prompts."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("outputs/consolidated/pdf")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"all_prompts_{timestamp}.pdf"

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=12
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=12
    )

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor='#7f8c8d',
        alignment=TA_CENTER
    )

    story = []

    # Cover page
    story.append(Paragraph("Audio Multimodal Formatting Prompts", title_style))
    story.append(Paragraph("Consolidated Collection", styles['Heading2']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"<b>Total Prompts:</b> {len(prompts)}", body_style))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Spacer(1, 0.5*inch))

    story.append(Paragraph("<b>Run Descriptions:</b>", heading_style))
    for run_num in [1, 2, 3]:
        run_count = len([p for p in prompts if p['run_number'] == run_num])
        story.append(Paragraph(
            f"<b>Run {run_num}</b> ({run_count} prompts): {RUN_DESCRIPTIONS[f'run{run_num}']}",
            body_style
        ))

    story.append(PageBreak())

    # Add all prompts
    for idx, prompt in enumerate(prompts, 1):
        run_num = prompt['run_number']

        # Prompt header with run indicator
        story.append(Paragraph(
            f"<b>Prompt {idx}</b> | Run {run_num}",
            heading_style
        ))
        story.append(Paragraph(f"<b>{prompt['name']}</b>", styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))

        # Description
        story.append(Paragraph(f"<b>Description:</b>", body_style))
        story.append(Paragraph(prompt['description'], body_style))
        story.append(Spacer(1, 0.1*inch))

        # Prompt content
        story.append(Paragraph(f"<b>System Prompt:</b>", body_style))

        # Split prompt into paragraphs for better formatting
        prompt_text = prompt['prompt'].replace('\n', '<br/>')
        story.append(Paragraph(prompt_text, body_style))

        # Footer with run info
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"<i>Run {run_num}: {RUN_DESCRIPTIONS[f'run{run_num}']}</i>",
            footer_style
        ))

        # Page break between prompts
        if idx < len(prompts):
            story.append(PageBreak())

    doc.build(story)
    print(f"Created consolidated PDF: {output_file}")
    return output_file

def main():
    print("=" * 50)
    print("Consolidating all runs...")
    print("=" * 50)
    print()

    # Load all prompts
    prompts = load_all_runs()
    print(f"Loaded {len(prompts)} total prompts from all runs")
    print(f"  Run 1: {len([p for p in prompts if p['run_number'] == 1])} prompts")
    print(f"  Run 2: {len([p for p in prompts if p['run_number'] == 2])} prompts")
    print(f"  Run 3: {len([p for p in prompts if p['run_number'] == 3])} prompts")
    print()

    # Create markdown
    print("Creating consolidated markdown...")
    md_file = create_consolidated_markdown(prompts)
    print()

    # Create PDF
    print("Creating consolidated PDF...")
    pdf_file = create_consolidated_pdf(prompts)
    print()

    print("=" * 50)
    print("Consolidation complete!")
    print(f"Markdown: {md_file}")
    print(f"PDF: {pdf_file}")
    print("=" * 50)

if __name__ == "__main__":
    main()
