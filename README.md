# Offline Customer Support Chatbot using Ollama and Llama 3.2 (3B)

## Project Overview

This project demonstrates how to build a fully offline customer support chatbot for a fictional e-commerce store (Chic Boutique) using:

- Ollama as the local model server
- llama3.2:3b as the LLM
- Python + requests for API integration

The workflow compares two prompt engineering strategies:

- Zero-Shot prompting
- One-Shot prompting

Responses are logged into a markdown file so they can be manually scored for quality.

## Video Demo

- Demo Link: https://drive.google.com/file/d/183FV7aPAyFwluDlADEAT8P8qON69vnTi/view?usp=sharing

## Why This Project Matters

Running inference locally is useful for privacy-sensitive workloads because customer data does not need to leave your network. This supports compliance efforts related to data protection regulations and removes recurring API costs.

## Features

- Fully offline chatbot evaluation workflow
- Direct integration with Ollama HTTP API (/api/generate)
- Uses required model: llama3.2:3b
- Compares zero-shot and one-shot responses for each query
- Evaluates at least 20 adapted e-commerce customer queries
- Produces structured markdown output with manual scoring columns
- Includes retry logic, timeout handling, and robust error messages

## Tech Stack

- Python 3.9+
- requests
- Ollama
- Llama 3.2 3B model (llama3.2:3b)

## Project Structure

```text
local-llm-chatbot/
├── chatbot.py
├── README.md
├── setup.md
├── report.md
├── requirements.txt
├── test_ollama.py
├── prompts/
│   ├── zero_shot_template.txt
│   └── one_shot_template.txt
└── eval/
		└── results.md
```

## How It Works

1. chatbot.py loads both prompt templates.
2. It iterates through 20 adapted e-commerce support queries.
3. For each query, it generates:
	 - one zero-shot response
	 - one one-shot response
4. It writes all outputs to eval/results.md in a markdown table with empty scoring columns.
5. You manually score Relevance, Coherence, and Helpfulness.

## Quick Start

Follow the full setup in setup.md. Minimal flow:

1. Install Ollama.
2. Pull model:

```bash
ollama pull llama3.2:3b
```

3. Ensure Ollama server is running.
4. Install Python dependencies:

```bash
pip install -r requirements.txt
```

5. Run evaluation:

```bash
python chatbot.py
```

6. Open eval/results.md and manually score each response.

## Optional Script Arguments

- Limit run size for quick testing:

```bash
python chatbot.py --max-queries 5
```

- Write output to a custom path:

```bash
python chatbot.py --output eval/results_experiment_2.md
```

## Troubleshooting

- Connection error to localhost:11434:
	- Make sure Ollama is running.
	- Verify endpoint is reachable.

- Slow response generation:
	- CPU-based local inference can be slow, especially on lower-end hardware.

- Empty or error rows in results:
	- Check Ollama logs and confirm the model exists locally.

## Next Improvements

- Add policy grounding from a local knowledge base
- Add automatic scoring heuristics before manual review
- Compare with additional local models (Mistral, Phi, etc.)
