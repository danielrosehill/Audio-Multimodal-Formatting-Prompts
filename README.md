# Audio-Multimodal-Formatting-Prompts

Generate creative system prompts for audio-to-text transformation workflows using AI.

## Overview

This project generates system prompts that instruct audio multimodal models to transform voice recordings into formatted text in creative and diverse ways.

## Quick Start

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Or use uv
uv pip install -r requirements.txt
```

### Running Generations

**Run All (Recommended)**
```bash
./run_all.sh
```
Runs all three strategies sequentially with appropriate delays between runs.

**Individual Runs:**

**Run 1: Batch Generation (10 prompts)**
```bash
source .venv/bin/activate
python generate_prompts.py 1
```
Uses `system-prompts/1.md` to generate 10 prompts in a single API call.

**Run 2: Individual Generation (50 prompts)**
```bash
source .venv/bin/activate
python generate_prompts.py 2
```
Uses `system-prompts/2.md` to generate 50 unique prompts (50 individual API calls with 1s delay).

**Run 3: Large Batch Generation (50 prompts)**
```bash
source .venv/bin/activate
python generate_prompts.py 3
```
Uses `system-prompts/3.md` to generate 50 diverse prompts in a single API call with maximum creative diversity.

### Options

```bash
# Use a different model
python generate_prompts.py 1 --model anthropic/claude-3.5-sonnet

# Adjust delay between requests (for run 2)
python generate_prompts.py 2 --delay 2.0
```

### Available Models

- `google/gemini-2.5-flash` (default - latest, fast, good reasoning)
- `google/gemini-2.5-flash-lite` (even faster, lighter)
- `google/gemini-2.0-flash-exp:free` (free tier)
- `anthropic/claude-3.5-sonnet` (higher quality, costs credits)

## Output Structure

Outputs are organized into two directories:

### `runs/` - Programmatic Data
Contains JSON files with structured data for programmatic access:
- `run1_batch_10_{timestamp}.json`
- `run2_individual_50_{timestamp}.json`
- `run3_batch_50_{timestamp}.json`

### `outputs/` - Human-Readable Data
Organized by run with markdown and PDF formats:

```
outputs/
├── run1/
│   ├── markdown/
│   │   ├── {run_name}_{timestamp}_all.md  (consolidated)
│   │   └── prompts/                         (individual files)
│   │       ├── 001_prompt-name.md
│   │       ├── 002_prompt-name.md
│   │       └── ...
│   └── pdf/
│       └── {run_name}_{timestamp}.pdf
├── run2/
│   └── ...
└── run3/
    └── ...
```

**Each Prompt Contains:**
- `name`: Short descriptive name (e.g., "Meeting Minutes - Action Items")
- `description`: What the transformation does and when to use it
- `prompt`: Complete system prompt ready for audio multimodal models

### Generating PDFs

After running the generators, create PDFs with:

```bash
source .venv/bin/activate
python generate_pdfs.py
```

This creates a formatted PDF for each run with:
- Cover page with run metadata
- One prompt per page with title, description, and full prompt
- Professional formatting for easy reading and printing

### Consolidating All Runs

To create a single consolidated view of all prompts across all three runs:

```bash
source .venv/bin/activate
python consolidate_runs.py
```

This creates:
- `outputs/consolidated/markdown/all_prompts_{timestamp}.md` - All 118 prompts organized by run
- `outputs/consolidated/pdf/all_prompts_{timestamp}.pdf` - Single PDF with all prompts and run indicators in footers

The consolidated output includes:
- Run descriptions explaining each generation strategy
- All prompts organized by run number
- Footer on each prompt page indicating which run it came from

## System Prompts

- `system-prompts/1.md`: Batch generator (10 prompts)
- `system-prompts/2.md`: Single-turn generator (1 prompt per call)
- `system-prompts/3.md`: Deep ideation generator (50 prompts with maximum diversity)

## Configuration

Add your OpenRouter API key to `.env`:

```
OPENROUTER_API_KEY=your_key_here
```
