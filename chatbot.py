"""Offline customer support chatbot evaluator using Ollama + Llama 3.2 (3B).

This script compares zero-shot and one-shot prompting for 20 adapted
e-commerce support queries, then writes outputs to eval/results.md for
manual scoring.
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List

import requests


OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"
REQUEST_TIMEOUT_SECONDS = 90
MAX_RETRIES = 3
BACKOFF_SECONDS = 2

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
DEFAULT_OUTPUT_PATH = BASE_DIR / "eval" / "results.md"


# Adapted from common Ubuntu support-style issues into e-commerce scenarios.
ADAPTED_ECOMMERCE_QUERIES: List[str] = [
	"My discount code is not working at checkout.",
	"How do I track the shipping status of my recent order?",
	"I received a damaged product. How can I request a replacement?",
	"Can I change my delivery address after placing the order?",
	"My payment failed but the amount was deducted from my account.",
	"I was charged twice for the same order. Can you help?",
	"My order shows delivered, but I have not received the package.",
	"How can I cancel my order before it ships?",
	"I forgot my password and cannot log into my account.",
	"How do I update the phone number on my account?",
	"Can I exchange a product for a different size?",
	"How long does a refund take after a return is approved?",
	"I received the wrong item in my package.",
	"Do you offer international shipping, and what are the charges?",
	"Why is my order stuck on 'processing' for several days?",
	"Can I apply store credit and a coupon code in the same order?",
	"How do I download an invoice for my purchase?",
	"The gift card balance is not applying during checkout.",
	"I selected express shipping, but the delivery date still looks late.",
	"How can I subscribe or unsubscribe from back-in-stock notifications?",
]


def configure_logging() -> None:
	"""Configure console logging with clear severity levels."""
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(message)s",
	)


def parse_args() -> argparse.Namespace:
	"""Parse optional command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Run zero-shot vs one-shot evaluation using a local Ollama model."
	)
	parser.add_argument(
		"--output",
		default=str(DEFAULT_OUTPUT_PATH),
		help="Path to the markdown results file (default: eval/results.md).",
	)
	parser.add_argument(
		"--max-queries",
		type=int,
		default=0,
		help="Optional limit for the number of queries (0 = all).",
	)
	return parser.parse_args()


def read_template(template_path: Path) -> str:
	"""Load a prompt template from disk."""
	if not template_path.exists():
		raise FileNotFoundError(f"Prompt template not found: {template_path}")

	content = template_path.read_text(encoding="utf-8").strip()
	if "{query}" not in content:
		raise ValueError(f"Template missing '{{query}}' placeholder: {template_path}")

	return content


def query_ollama(prompt: str, session: requests.Session) -> str:
	"""Query Ollama with retry logic and robust response parsing."""
	payload = {
		"model": MODEL_NAME,
		"prompt": prompt,
		"stream": False,
	}

	last_error = "Unknown error"
	for attempt in range(1, MAX_RETRIES + 1):
		try:
			response = session.post(
				OLLAMA_ENDPOINT,
				json=payload,
				timeout=REQUEST_TIMEOUT_SECONDS,
			)
			response.raise_for_status()

			# Parse using requests first, then fallback to json for robustness.
			try:
				data: Dict[str, object] = response.json()
			except ValueError:
				data = json.loads(response.text)

			response_text = str(data.get("response", "")).strip()
			if response_text:
				return response_text

			last_error = "Empty response field returned by Ollama"
			logging.warning("Attempt %s/%s: %s", attempt, MAX_RETRIES, last_error)

		except (requests.exceptions.RequestException, json.JSONDecodeError) as exc:
			last_error = str(exc)
			logging.warning("Attempt %s/%s failed: %s", attempt, MAX_RETRIES, last_error)

		if attempt < MAX_RETRIES:
			sleep_seconds = BACKOFF_SECONDS ** (attempt - 1)
			time.sleep(sleep_seconds)

	return f"Error: Could not get a valid response from the model. Details: {last_error}"


def escape_markdown_cell(value: str) -> str:
	"""Escape text for safe inclusion in a markdown table cell."""
	return value.replace("|", "\\|").replace("\n", " ").strip()


def write_results_markdown(
	output_path: Path,
	query_results: List[Dict[str, str]],
) -> None:
	"""Write evaluation rubric and result table to markdown file."""
	output_path.parent.mkdir(parents=True, exist_ok=True)

	lines: List[str] = []
	lines.append("# Evaluation Results")
	lines.append("")
	lines.append("## Scoring Rubric")
	lines.append("")
	lines.append("- Relevance (1-5): How well the answer addresses the customer query.")
	lines.append("- Coherence (1-5): Grammar, clarity, and readability of the answer.")
	lines.append("- Helpfulness (1-5): Actionability and usefulness of the guidance.")
	lines.append("")
	lines.append("| Query # | Customer Query | Prompting Method | Response | Relevance | Coherence | Helpfulness |")
	lines.append("|---|---|---|---|---|---|---|")

	for item in query_results:
		query_id = item["query_id"]
		customer_query = escape_markdown_cell(item["customer_query"])

		zero_shot_response = escape_markdown_cell(item["zero_shot_response"])
		lines.append(
			f"| {query_id} | {customer_query} | Zero-Shot | {zero_shot_response} |  |  |  |"
		)

		one_shot_response = escape_markdown_cell(item["one_shot_response"])
		lines.append(
			f"| {query_id} | {customer_query} | One-Shot | {one_shot_response} |  |  |  |"
		)

	output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_evaluation(output_path: Path, max_queries: int) -> None:
	"""Run the full zero-shot vs one-shot evaluation workflow."""
	zero_shot_template = read_template(PROMPTS_DIR / "zero_shot_template.txt")
	one_shot_template = read_template(PROMPTS_DIR / "one_shot_template.txt")

	queries = ADAPTED_ECOMMERCE_QUERIES
	if max_queries > 0:
		queries = queries[:max_queries]

	logging.info("Starting evaluation with %s query/queries.", len(queries))
	logging.info("Model: %s", MODEL_NAME)
	logging.info("Endpoint: %s", OLLAMA_ENDPOINT)

	results: List[Dict[str, str]] = []

	with requests.Session() as session:
		try:
			for index, query in enumerate(queries, start=1):
				logging.info("Processing query %s/%s", index, len(queries))

				try:
					zero_prompt = zero_shot_template.format(query=query)
					zero_response = query_ollama(zero_prompt, session)

					one_prompt = one_shot_template.format(query=query)
					one_response = query_ollama(one_prompt, session)
				except Exception as exc:  # pylint: disable=broad-except
					logging.error("Query %s failed: %s", index, exc)
					zero_response = f"Error: Query processing failed. Details: {exc}"
					one_response = f"Error: Query processing failed. Details: {exc}"

				results.append(
					{
						"query_id": str(index),
						"customer_query": query,
						"zero_shot_response": zero_response,
						"one_shot_response": one_response,
					}
				)
		except KeyboardInterrupt:
			logging.warning("Evaluation interrupted by user. Writing partial results.")

	write_results_markdown(output_path, results)
	logging.info("Evaluation complete. Results written to: %s", output_path)


def main() -> None:
	"""Entrypoint for the chatbot evaluation script."""
	configure_logging()
	args = parse_args()

	output_override = os.getenv("RESULTS_OUTPUT_PATH", "").strip()
	output_path = Path(output_override) if output_override else Path(args.output)

	try:
		run_evaluation(output_path=output_path, max_queries=args.max_queries)
	except Exception as exc:  # pylint: disable=broad-except
		logging.error("Execution failed: %s", exc)
		raise


if __name__ == "__main__":
	main()
