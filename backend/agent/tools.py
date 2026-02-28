"""
agent/tools.py
--------------
Custom Langchain tools available to the agent.

WHY tools:
   Tools let the agent take actions beyond just answering - like looking up
   live account info, checking outage status, or escalating a ticket.
   Currently these are mock implementations. In production, each would
   call a real internal API or database.

How to add a tool to the agent:
   1. Define function with @tool decorator
   2. Add clear docstring - the LLM reads it to decide when to use the tool
   3. Import and add to tools list in graph.py if using tool-calling agent
"""

from langchain.tools import tool
from core.logging import setup_logger

logger = setup_logger(__name__)

@tool
def check_account_status(account_number: str) -> str:
    """
    Check the current status of a NovaTel customer account.
    Use when customer asks about their account standing, suspension, or balance.

    Args:
       account_number: The customer's NovaTel account number (e.g., '8847-2291')

       Returns:
            Account status summary as a string.
    """
    logger.info(f"Checking account status for: {account_number}")

    # In production: call internal CRM API
    # response = requests.get(f"{CRM_BASE_URL}/accounts/{account_number}")

    # Mock response for demo
    return (
        f"Account {account_number}: Status= Active | "
        f"Current Balance = $175.56 | "
        f"Next Bill Date = Dec 12, 2025 | "
        f"Autopay = Enabled"
    )

@tool
def check_network_outage(zip_code: str) -> str:
    """
    Check if there is a known network outage in the customer's area.
    Use when customer reports no signal, slow speeds, or connectivity issues.

    Args:
      zip_code: Customer's ZIP code(e.g., '90210')
    Returns:
      Outage status for the given area.
    """
    logger.info(f"Checking network outage for ZIP: {zip_code}")

    # In production: call Network Operations Center API
    # response = requests.get(f"{NOC_BASE_URL}/outages?zip={zip_code}")

    # Mock response for demo
    return (
        f"ZIP {zip_code}: No active outages detected."
        f"Last checked: 2 minutes ago. "
        f"Network status: Operational. "
        f"5G coverage: Available."
    )

@tool
def get_plan_details(plan_name: str) -> str:
    """
    Retrieved detailed information about a specifi NovaTel plan.
    Use when customer asks for specifics about a plan that may not be in context.

    Args:
        plan_name: Name of the plan (e.g., 'Unlimited Plus', 'Essential', 'Starter')
    
    Returns:
        Detailed plan information as a string.
    """
    logger.info(f"Fetching plan details for: {plan_name}")

    # In production: call plans API or database
    plans = {
        "starter": "NovaTel Starter: $19.99/mo | 5GB data | Unlimited calls & texts | 1GB hotspot",
        "essential": "NovaTel Essential: $34.99/mo | 15GB data | Unlimited calls & texts | 5GB hotspot | HD streaming",
        "unlimited plus": "NovaTel Unlimited Plus: $49.99/mo | Unlimited data* | 15GB hotspot | 4K streaming | International texts",
        "premium elite": "NovaTel Premium Elite: $69.99/mo | Unlimited data* | 50GB hotspot | 4k | 100+ intl mins | Apple TV+",
    }
    plan_key = plan_name.lower().strip()
    return plans.get(plan_key, f"Plan '{plan_name}' not found. Please check novatel.com/plans for full details.")
# ── Tool registry for agent ───────────────────────────────────────────────────
# Import this list in graph.py if binding tools to the LLM:
# llm_with_tools = llm.bind_tools(AVAILABLE_TOOLS)

AVAILABLE_TOOLS = [
    check_account_status,
    check_network_outage,
    get_plan_details,
]