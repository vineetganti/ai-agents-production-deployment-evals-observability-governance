# AI agents on AWS: production deployment, evals, observability and governance

Hands-on labs for taking Strands agents from a notebook to production on AWS, then measuring and governing them.

| Folder | Labs |
|---|---|
| [`production-deployment`](production-deployment) | Lambda, ECS Fargate, AgentCore Runtime, AgentCore Gateway, and a multi-agent MCP + A2A system on AgentCore |
| [`evals-observability-governance`](evals-observability-governance) | Agent evaluation, tracing (console, Jaeger, Langfuse, LangSmith, CloudWatch/ADOT), Bedrock Guardrails, AgentCore Policy (Cedar) |

Each lab has a Bedrock edition and a `-groq` edition that runs the model on Groq instead.

## Origin and changes

This is course material from *Agentic AI on AWS* (MIT licensed, see [LICENSE](LICENSE): Copyright (c) 2025 Packt, Copyright (c) 2026 Shivank Agrawal). Sections 6 (production deployment) and 7 (evals, observability, governance) are published here on their own, with fixes made while running the labs on Windows (Git Bash):

- Git Bash path handling in the Lambda and ECS Fargate deploy scripts (`/tmp` file URIs, `/health` and `/ecs/...` argument rewriting) and passing the architecture to `sam build`.
- Langfuse tracing for the AgentCore account agent (`agentcore_agent_langfuse.py`) and loading credentials from `.env` in the Langfuse notebook.
- `validationMode="IGNORE_ALL_FINDINGS"` for the intentionally broad Cedar `permit` in the AgentCore Policy notebook.

Notebook outputs are cleared, so run the cells to regenerate them.

## Before you run anything

The labs create real AWS resources (and some call Groq, Langfuse and other APIs) that can cost money. Each lab has a cleanup step; run it when you finish. Keep API keys in a local `.env` file, which is git-ignored, and never commit it.
