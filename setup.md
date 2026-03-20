# Setup Guide

## 1. Install Ollama

Download and install Ollama for your operating system from the official site.

After installation, verify:

```bash
ollama --version
```

## 2. Pull the Required Model

```bash
ollama pull llama3.2:3b
```

This downloads the local model weights used by chatbot.py.

## 3. Start or Verify Ollama Server

On Windows and macOS, Ollama usually starts as a background app.

Optional health check:

```bash
ollama run llama3.2:3b
```

Type a quick message, then enter /bye to exit.

## 4. Create Python Virtual Environment

From project root:

```bash
python -m venv venv
```

Activate virtual environment:

- Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

- Windows (Command Prompt):

```cmd
venv\Scripts\activate.bat
```

- macOS/Linux:

```bash
source venv/bin/activate
```

## 5. Install Dependencies

Required by project brief:

```bash
pip install requests datasets
```

Or install everything listed in requirements.txt:

```bash
pip install -r requirements.txt
```

## 6. Run the Chatbot Evaluation

```bash
python chatbot.py
```

Output file generated:

- eval/results.md

## 7. Manual Evaluation

Open eval/results.md and score each response for:

- Relevance (1-5)
- Coherence (1-5)
- Helpfulness (1-5)

## Optional Commands

Run only first 5 queries:

```bash
python chatbot.py --max-queries 5
```

Custom output file:

```bash
python chatbot.py --output eval/results_trial.md
```

## Common Issues

1. Error: connection refused to localhost:11434
	- Ensure Ollama is running.

2. Error: model not found
	- Run: ollama pull llama3.2:3b

3. Slow responses
	- Local CPU inference is expected to be slower than cloud GPU services.
