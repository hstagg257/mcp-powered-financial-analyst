import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


load_dotenv()


def get_required_environment_variable(name: str) -> str:
    """
    Read a required environment variable.

    Raises:
        RuntimeError: If the variable is missing or empty.
    """
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not configured."
        )

    return value


def invoke_financial_analyst(
    financial_data: str,
    question: str,
) -> str:
    """
    Send financial data and an analysis question to the Microsoft Foundry agent.

    Args:
        financial_data: Financial information for the agent to analyse.
        question: The analysis or question to apply to the supplied data.

    Returns:
        The financial analysis returned by the Foundry agent.
    """
    project_endpoint = get_required_environment_variable(
        "FOUNDRY_PROJECT_ENDPOINT"
    )
    agent_name = os.getenv(
        "FOUNDRY_AGENT_NAME",
        "financial-analyst",
    )

    request = f"""
Analyse the financial data supplied below.

FINANCIAL DATA
--------------
{financial_data}

ANALYSIS REQUEST
----------------
{question}

Requirements:
- Base the analysis only on the supplied data.
- Clearly state any assumptions.
- Show important calculations where relevant.
- Do not invent missing values.
- Keep the response concise and business-focused.
""".strip()

    credential = DefaultAzureCredential()

    try:
        with AIProjectClient(
            endpoint=project_endpoint,
            credential=credential,
        ) as project_client:

            with project_client.get_openai_client(
                agent_name=agent_name,
            ) as openai_client:

                conversation = openai_client.conversations.create(
                    items=[
                        {
                            "type": "message",
                            "role": "user",
                            "content": request,
                        }
                    ]
                )

                try:
                    response = openai_client.responses.create(
                        conversation=conversation.id,
                    )

                    analysis = response.output_text

                    if not analysis:
                        raise RuntimeError(
                            "The Foundry agent returned an empty response."
                        )

                    return analysis

                finally:
                    openai_client.conversations.delete(
                        conversation_id=conversation.id
                    )

    finally:
        credential.close()