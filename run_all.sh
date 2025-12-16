#!/bin/bash
# Run all three generation strategies

echo "=========================================="
echo "Starting all generation runs"
echo "=========================================="
echo ""

# Activate venv
source .venv/bin/activate

echo "Run 1: Batch generation (10 prompts)"
echo "------------------------------------------"
python generate_prompts.py 1
echo ""
echo "Waiting 30 seconds before next run..."
sleep 30
echo ""

echo "Run 2: Individual generation (50 prompts)"
echo "------------------------------------------"
python generate_prompts.py 2 --delay 2.0
echo ""
echo "Waiting 30 seconds before next run..."
sleep 30
echo ""

echo "Run 3: Large batch generation (50 prompts)"
echo "------------------------------------------"
python generate_prompts.py 3
echo ""

echo "Generating PDFs for all runs..."
echo "------------------------------------------"
python generate_pdfs.py
echo ""

echo "=========================================="
echo "All runs complete!"
echo "Check the runs/ directory for results"
echo "=========================================="
