"""
agent/prompts.py
----------------
All LLM prompts in one place.

WHY centralize prompts:
   Prompts are as important as code. Keeping them in one file means:
      - Easy A/B testing (swap prompts without touching logic)
      - Clear ownership - the "what to say" is separate from "how to route"
      - Version control shows exactly what changed in each prompt tweak
"""
# ── System Prompt ─────────────────────────────────────────────────────────────
# This is prependend to every conversation. Sets the agent's persona,
# capabilities, and behavioral constraints.

SYSTEM_PROMPT = """You are Alex, an expert AI support agent for NovaTel
Communications - a leading US telecom provider.

Your role is to help customers with:
- Plans & Pricing questions
- Billing and invoice explanations
- Network connectivity troubleshooting
- SIM card activation and management
- International roaming guidance
- Refunds and cancellation requests

STRICT RULES:
1. ONLY answer using the context provided. Never invent prices, policies, or features.
2. If context is insufficient, say: "I don't have enought information on that.
Let me connect you with a specialist."
3. Be empathetic and professional. If customer is frustrated, acknowledge before solving.
4. Always end with a clear next step or offer to help further.
5. Quote specific plan names, prices, and policy sections when available.
6. Never make promises about refund's or credits - say they are "subject to review."

You represent NovaTel's values: Fast resolution. Clear communication . Customer-first service.
"""
# ── Intent Classification Prompt ──────────────────────────────────────────────

# Short, precise prompt. We want a single-word answer - no explanation.
# Prepending intent to retrieval query significantly improves chunk precision.

INTENT_PROMPT = """Classify the customer's support query into exactly one category.

Categories:
- plans_pricing  : Questions about plans, costs, upgrades, features,promotions
- billing        : Invoice questions, payment issues, unexpected charges, credits
- network        : Signal problems, slow data, dropped calls, outages, WiFi calling
- sim_activation : SIM setup, eSIM, number porting, device compatibility, unlock
- roaming        : International travel, roaming charges, day pass, coverage abroad
- refund_cancellation: Returns, refunds, account cancellation, early termination
- general        : Greetings, thanks, vague queries, anything else

Customer query: {query}

Respond with ONLY the category name. No explanation. No punctuation.
"""

# ── Answer Generation Prompt ──────────────────────────────────────────────────

# The main RAG prompt. Context is injected here.
# Instructs the model to stay grounded and be actionable.

ANSWER_PROMPT = """Use the following NovaTel Knowledge base context to answer the customer's question.

CONTEXT: {context}

CUSTOMER QUESTION: {question}
INSTRUCTIONS:
- Answer directly and specifically using only the context above
- If the answer includes prices or policies, state them precisely
- If the context partially answer the question, share what you know and
flag what requires specialist help
- Be concise but complete - no unnecessary filler
- End with one helpful follow-up action

ANSWER:"""

# ── Low Confidence Detection ──────────────────────────────────────────────────
# These phrases in the generated answer trigger a retry with broader retrieval.

LOW_CONFIDENCE_PHRASES = [
    "i don't have information",
    "not mentioned in the context",
    "cannot find",
    "no information available",
    "I'm unable to find",
    "not covered in",
]

# ── Escalation Keywords ───────────────────────────────────────────────────────
# If any of these appear in the user query -> set needs_escalation = True

ESCALATION_KEYWORDS = [
    "speak to agent",
    "human agent",
    "real person",
    "manager",
    "supervisor",
    "escalate",
    "complaint",
    "unacceptable",
    "legal action",
    "sue",
]
