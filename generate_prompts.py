#!/usr/bin/env python3
"""
Generate text transformation prompts using different strategies with structured output.

Run 1: Batch generation (10 prompts) using 1.md
Run 2: Individual generation (50 calls) using 2.md
Run 3: Large batch generation (50 prompts) using 3.md
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Output directory
OUTPUT_DIR = Path("runs")
OUTPUT_DIR.mkdir(exist_ok=True)

# JSON Schema for structured output
PROMPT_SCHEMA = {
    "type": "object",
    "properties": {
        "prompts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Short, descriptive name for the transformation (e.g., 'Formal Business Email', 'Action Items Extractor')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of what this transformation does and when to use it"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The complete system prompt ready to be used with an audio multimodal model"
                    }
                },
                "required": ["name", "description", "prompt"]
            }
        }
    },
    "required": ["prompts"]
}


def read_prompt_file(prompt_number: int) -> str:
    """Read a system prompt file."""
    prompt_file = Path(f"system-prompts/{prompt_number}.md")
    with open(prompt_file, 'r') as f:
        return f.read()


def call_openrouter_structured(system_prompt: str, model: str = "google/gemini-2.5-flash", max_retries: int = 5) -> dict:
    """
    Call OpenRouter API with structured output and retry logic.

    Default model: Gemini 2.5 Flash (latest, good reasoning)
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/danielrosehill/Audio-Multimodal-Formatting-Prompts",
    }

    # Add instruction for structured output
    enhanced_prompt = f"""{system_prompt}

IMPORTANT: You must respond with valid JSON matching this exact structure:

{{
  "prompts": [
    {{
      "name": "Short descriptive name",
      "description": "Brief description of the transformation",
      "prompt": "Complete system prompt ready to use"
    }}
  ]
}}

Generate your prompts now in this JSON format."""

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": enhanced_prompt}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "audio_transformation_prompts",
                "strict": True,
                "schema": PROMPT_SCHEMA
            }
        }
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            # Parse JSON response
            parsed = json.loads(content)
            return parsed

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = (2 ** attempt) * 2
                print(f"\nRate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise
            else:
                raise
        except json.JSONDecodeError as e:
            print(f"\nJSON parse error: {e}")
            if attempt == max_retries - 1:
                raise
            print(f"Retrying...")
            time.sleep(2)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) * 2
            print(f"\nError: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)


def save_prompts(prompts_data: dict, run_name: str, model: str, prompt_file: int, elapsed: float):
    """Save prompts to both JSON and individual markdown files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save master JSON file
    master_json = OUTPUT_DIR / f"{run_name}_{timestamp}.json"
    output_data = {
        "run_name": run_name,
        "timestamp": timestamp,
        "generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "model": model,
        "prompt_file": f"{prompt_file}.md",
        "elapsed_seconds": elapsed,
        "count": len(prompts_data.get("prompts", [])),
        "prompts": prompts_data.get("prompts", [])
    }

    with open(master_json, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Master JSON saved to: {master_json}")

    # Create run-specific directory for individual prompt files
    prompts_dir = OUTPUT_DIR / f"{run_name}_{timestamp}_prompts"
    prompts_dir.mkdir(exist_ok=True)

    # Save each prompt as individual markdown file
    for idx, prompt_obj in enumerate(prompts_data.get("prompts", []), 1):
        # Sanitize filename
        name_slug = prompt_obj["name"].lower().replace(" ", "-").replace("/", "-")[:50]
        prompt_file_path = prompts_dir / f"{idx:03d}_{name_slug}.md"

        with open(prompt_file_path, 'w') as f:
            f.write(f"# {prompt_obj['name']}\n\n")
            f.write(f"**Description:** {prompt_obj['description']}\n\n")
            f.write("---\n\n")
            f.write("## System Prompt\n\n")
            f.write(prompt_obj['prompt'])
            f.write("\n")

    print(f"✓ Individual prompts saved to: {prompts_dir}/ ({len(prompts_data.get('prompts', []))} files)")

    # Also create a consolidated markdown file
    consolidated_md = OUTPUT_DIR / f"{run_name}_{timestamp}_all.md"
    with open(consolidated_md, 'w') as f:
        f.write(f"# {run_name}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model:** {model}\n")
        f.write(f"**Total Prompts:** {len(prompts_data.get('prompts', []))}\n\n")
        f.write("---\n\n")

        for idx, prompt_obj in enumerate(prompts_data.get("prompts", []), 1):
            f.write(f"## {idx}. {prompt_obj['name']}\n\n")
            f.write(f"**Description:** {prompt_obj['description']}\n\n")
            f.write("```\n")
            f.write(prompt_obj['prompt'])
            f.write("\n```\n\n")
            f.write("---\n\n")

    print(f"✓ Consolidated markdown saved to: {consolidated_md}")


def run_batch_generation(prompt_number: int, run_name: str, model: str = "google/gemini-2.5-flash"):
    """
    Run batch generation - single API call that returns multiple structured prompts.
    """
    print(f"\n{'='*60}")
    print(f"Running {run_name}")
    print(f"Prompt file: {prompt_number}.md")
    print(f"Model: {model}")
    print(f"{'='*60}\n")

    system_prompt = read_prompt_file(prompt_number)

    print("Sending request to OpenRouter...")
    start_time = time.time()

    prompts_data = call_openrouter_structured(system_prompt, model)

    elapsed = time.time() - start_time
    print(f"Response received in {elapsed:.2f} seconds")
    print(f"Generated {len(prompts_data.get('prompts', []))} prompts")

    save_prompts(prompts_data, run_name, model, prompt_number, elapsed)

    return prompts_data


def run_individual_generation(prompt_number: int, num_iterations: int, run_name: str,
                              model: str = "google/gemini-2.5-flash", delay: float = 2.0):
    """
    Run individual generation - multiple API calls, one prompt at a time.
    Each call returns a single prompt in structured format.
    """
    print(f"\n{'='*60}")
    print(f"Running {run_name}")
    print(f"Prompt file: {prompt_number}.md")
    print(f"Model: {model}")
    print(f"Iterations: {num_iterations}")
    print(f"{'='*60}\n")

    system_prompt = read_prompt_file(prompt_number)
    all_prompts = []
    total_elapsed = 0

    for i in range(1, num_iterations + 1):
        print(f"Iteration {i}/{num_iterations}...", end=" ", flush=True)

        try:
            start_time = time.time()
            prompts_data = call_openrouter_structured(system_prompt, model)
            elapsed = time.time() - start_time
            total_elapsed += elapsed

            # Extract the single prompt (should be 1 in array)
            if prompts_data.get("prompts"):
                all_prompts.extend(prompts_data["prompts"])
                print(f"✓ ({elapsed:.2f}s) - Got {len(prompts_data['prompts'])} prompt(s)")
            else:
                print(f"✗ No prompts in response")

            # Rate limiting
            if i < num_iterations:
                time.sleep(delay)

        except Exception as e:
            print(f"✗ Error: {e}")

    print(f"\n✓ All iterations complete. Total prompts: {len(all_prompts)}")

    # Save all collected prompts
    combined_data = {"prompts": all_prompts}
    save_prompts(combined_data, run_name, model, prompt_number, total_elapsed)

    return all_prompts


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate text transformation prompts")
    parser.add_argument("run", type=int, choices=[1, 2, 3],
                       help="Run number (1=batch-10, 2=individual-50, 3=batch-50)")
    parser.add_argument("--model", type=str, default="google/gemini-2.5-flash",
                       help="Model to use (default: gemini-2.5-flash)")
    parser.add_argument("--delay", type=float, default=2.0,
                       help="Delay between requests for individual generation (default: 2.0s)")

    args = parser.parse_args()

    if args.run == 1:
        # Run 1: Batch generation (10 prompts)
        run_batch_generation(
            prompt_number=1,
            run_name="run1_batch_10",
            model=args.model
        )

    elif args.run == 2:
        # Run 2: Individual generation (50 iterations)
        run_individual_generation(
            prompt_number=2,
            num_iterations=50,
            run_name="run2_individual_50",
            model=args.model,
            delay=args.delay
        )

    elif args.run == 3:
        # Run 3: Large batch generation (50 prompts)
        run_batch_generation(
            prompt_number=3,
            run_name="run3_batch_50",
            model=args.model
        )

    print("\n✓ Generation complete!")


if __name__ == "__main__":
    main()
