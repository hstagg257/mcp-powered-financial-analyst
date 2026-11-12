import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    FixedRatioVersionSelectionRule,
    PromptAgentDefinition,
    ProtocolConfiguration,
    ResponsesProtocolConfiguration,
    VersionSelector,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


load_dotenv()

project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.getenv("FOUNDRY_AGENT_NAME", "financial-analyst")


AGENT_INSTRUCTIONS = """
You are a careful financial analysis assistant.

Your role is to analyse financial information supplied by the user and produce
clear, decision-useful insights.

When responding:

1. Identify important trends, variances, risks and anomalies.
2. Show the reasoning behind calculations.
3. Clearly distinguish facts from assumptions.
4. Do not invent missing financial data.
5. State when the supplied information is insufficient.
6. Use GBP when the data is expressed in pounds.
7. Present important calculations clearly.
8. Keep the analysis concise and business-focused.
9. Do not provide regulated investment, tax or legal advice.
10. Describe the output as analysis rather than professional financial advice.
"""


def create_financial_analyst() -> None:
    credential = DefaultAzureCredential()

    try:
        with AIProjectClient(
            endpoint=project_endpoint,
            credential=credential,
        ) as project_client:

            agent_version = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model_name,
                    instructions=AGENT_INSTRUCTIONS,
                ),
            )

            print("Agent version created successfully.")
            print(f"Agent name: {agent_version.name}")
            print(f"Agent version: {agent_version.version}")
            print(f"Agent ID: {agent_version.id}")

            endpoint_config = AgentEndpointConfig(
                version_selector=VersionSelector(
                    version_selection_rules=[
                        FixedRatioVersionSelectionRule(
                            agent_version=agent_version.version,
                            traffic_percentage=100,
                        )
                    ]
                ),
                protocol_configuration=ProtocolConfiguration(
                    responses=ResponsesProtocolConfiguration()
                ),
            )

            project_client.agents.update_details(
                agent_name=agent_name,
                agent_endpoint=endpoint_config,
            )

            print(
                f"Responses endpoint configured to use "
                f"version {agent_version.version}."
            )

    finally:
        credential.close()


if __name__ == "__main__":
    create_financial_analyst()