# Report: Offline Customer Support Chatbot using Ollama and Llama 3.2 (3B)

## 1. Introduction

This project evaluates whether a local Large Language Model (LLM) can support customer service workflows for an e-commerce business without sending sensitive data to third-party cloud providers. The chatbot is deployed fully offline using Ollama and llama3.2:3b.

This approach is relevant for organizations that must reduce privacy and compliance risk under data protection regulations such as GDPR (EU), CCPA (California), and DPDP Act 2023 (India). By processing requests locally, customer data can remain inside the company network.

The primary objective is to compare two prompt engineering strategies:

- Zero-Shot prompting
- One-Shot prompting

## 2. Methodology

### 2.1 System Design

- Client script: chatbot.py
- Local API endpoint: http://localhost:11434/api/generate
- Model: llama3.2:3b
- Inference mode: synchronous non-streaming generation

### 2.2 Query Dataset

Twenty realistic e-commerce support queries were used, adapted from technical support style problems (inspired by Ubuntu Dialogue Corpus patterns) into customer-service scenarios such as checkout failures, shipping issues, account access, and return/refund requests.

### 2.3 Prompt Design

- Zero-shot template:
	- Role assignment: customer support agent for Chic Boutique
	- Friendly and concise behavior constraints
	- No example included

- One-shot template:
	- Same role and constraints
	- Exactly one hardcoded example (return policy query/response) to guide tone and structure

### 2.4 Evaluation Rubric

Manual scoring was performed across three metrics:

- Relevance (1-5): Does the response address the customer intent?
- Coherence (1-5): Is the response clear, grammatically correct, and readable?
- Helpfulness (1-5): Does it provide actionable and useful next steps?

Each of the 20 queries produced two responses (Zero-Shot and One-Shot), resulting in 40 scored responses.

## 3. Results and Analysis

### 3.1 Quantitative Summary

After manual scoring in eval/results.md, the averages are:

- Average Relevance (Zero-Shot): 3.95
- Average Relevance (One-Shot): 3.80
- Average Coherence (Zero-Shot): 4.00
- Average Coherence (One-Shot): 4.80
- Average Helpfulness (Zero-Shot): 3.05
- Average Helpfulness (One-Shot): 3.70

Overall trend: One-shot prompting produced clearer and better-structured responses (higher coherence) and was generally more actionable (higher helpfulness). Zero-shot slightly outperformed one-shot in relevance in this run because one-shot occasionally applied assumptions that did not match the query intent.

### 3.2 Qualitative Comparison

Observed strengths of One-Shot prompting typically include:

- More consistent customer-friendly tone
- Better format alignment with desired answer style
- More direct actionable guidance

Observed limitations that can appear in either mode:

- Occasional vague language when policy details are unknown
- Generic fallback responses for ambiguous queries
- Potential hallucination risk if asked for unavailable policy/order details

### 3.3 Example Comparisons from This Run

Example A: Discount code failure (Query 1)

- Zero-Shot: The response gave multiple troubleshooting steps and support escalation, but was longer and included generic placeholders.
- One-Shot: The response was concise, actionable, and asked a clear follow-up to help narrow the issue.
- Analysis: One-shot was more coherent and helpful because it reduced verbosity while preserving actionable guidance.

Example B: Delivered but not received (Query 7)

- Zero-Shot: The response asked for order details and suggested escalation, but with extra conversational filler.
- One-Shot: The response directly requested support contact and offered a clear investigation next step.
- Analysis: One-shot was easier to follow and more support-ready for a real agent workflow.

Example C: International shipping question (Query 14)

- Zero-Shot: The response acknowledged international shipping and suggested checking shipping details during checkout.
- One-Shot: The response incorrectly claimed international shipping is unavailable and added assumptions not grounded in provided policy context.
- Analysis: This illustrates a one-shot relevance failure mode where a single example improves style but can still misalign with intent when policy facts are not explicitly grounded.

## 4. Conclusion

Llama 3.2 (3B) running locally through Ollama is suitable for lightweight first-line customer support assistance where privacy and cost control are priorities. It can produce understandable and often helpful responses for common support intents.

Key strengths:

- Data stays local (privacy advantage)
- Zero API costs after setup
- Easy deployment via Ollama

Key weaknesses:

- Can produce generic or uncertain responses without policy grounding
- Less reliable than larger cloud-hosted models for complex edge cases
- Response latency can be noticeable on CPU-only devices

## 5. Limitations

- No real-time backend integration (orders, inventory, shipment APIs)
- Manual evaluation introduces reviewer subjectivity
- Hallucination remains possible for unknown details
- Local hardware constraints may increase latency

## 6. Recommended Next Steps

1. Add retrieval-augmented generation from local policy documents.
2. Connect to internal order/returns systems for factual grounding.
3. Add guardrails for refusal and escalation behavior.
4. Compare multiple local models (Mistral, Phi, etc.) under the same rubric.
5. Introduce test automation for prompt regression checks.
