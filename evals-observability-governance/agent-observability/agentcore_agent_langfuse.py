"""Customer account agent traced with Langfuse.

Same agent as agentcore_agent.py, but instrumented with the Langfuse SDK instead
of the AWS Distro for OpenTelemetry. Run it directly (not with
`opentelemetry-instrument`): the Langfuse SDK registers itself as the global
OpenTelemetry tracer provider, and only one provider is allowed per process.

    python agentcore_agent_langfuse.py

Needs LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY and LANGFUSE_BASE_URL, either
exported or in a .env file next to this script.
"""

import os

from dotenv import load_dotenv

# Load credentials BEFORE the Langfuse client is created, otherwise it
# initialises with missing or wrong keys.
load_dotenv()
os.environ.setdefault("LANGFUSE_TRACING_ENVIRONMENT", "development")

from langfuse import get_client, propagate_attributes  # noqa: E402

# Creating the client registers the OTel tracer provider that Strands emits its
# spans to, so it must happen before the agent runs.
langfuse = get_client()

from strands import Agent, tool  # noqa: E402
from strands.models import BedrockModel  # noqa: E402

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
APP_VERSION = "1.0.0"


@tool
def lookup_account(account_id: str) -> str:
    """Look up account details by account ID."""
    # Simulated account data
    accounts = {
        "ACC-001": {"name": "Acme Corp", "tier": "Enterprise", "balance": 142500.00},
        "ACC-002": {"name": "Startup Inc", "tier": "Growth", "balance": 28750.00},
    }
    account = accounts.get(account_id)
    if account:
        return f"Account {account_id}: {account['name']}, Tier: {account['tier']}, Balance: ${account['balance']:,.2f}"
    return f"Account {account_id} not found."


@tool
def calculate_discount(amount: float, tier: str) -> str:
    """Calculate discount based on customer tier."""
    rates = {"Enterprise": 0.15, "Growth": 0.10, "Starter": 0.05}
    rate = rates.get(tier, 0.0)
    discount = amount * rate
    return f"{tier} tier discount: {rate * 100:.0f}% off ${amount:,.2f} = ${discount:,.2f} savings"


model = BedrockModel(model_id=MODEL_ID)

agent = Agent(
    name="account-assistant",  # shows up in the span name instead of the generic "Strands Agents"
    model=model,
    system_prompt="You are a customer account assistant. Use the available tools to help with account inquiries.",
    tools=[lookup_account, calculate_discount],
)


def handle_account_inquiry(question: str, user_id: str, session_id: str) -> str:
    """One agent run = one trace. The root observation carries only the user
    question and the final answer, not the function arguments."""
    with langfuse.start_as_current_observation(
        as_type="agent",
        name="handle-account-inquiry",
        input=question,
    ) as root:
        with propagate_attributes(
            user_id=user_id,
            session_id=session_id,
            trace_name="account-inquiry",
            tags=["account-assistant", "strands"],
            version=APP_VERSION,
            metadata={"model_id": MODEL_ID, "app": "agentcore-agent"},
        ):
            answer = str(agent(question))
        root.update(output=answer)
    return answer


if __name__ == "__main__":
    try:
        print(
            handle_account_inquiry(
                "Look up account ACC-001 and calculate what discount they would get on a $50,000 purchase.",
                user_id="demo-user",
                session_id="account-demo-session",
            )
        )
    finally:
        # Short-lived script: send buffered spans before the process exits.
        langfuse.flush()
