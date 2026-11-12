import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


load_dotenv()

project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.getenv("FOUNDRY_AGENT_NAME", "financial-analyst")


TEST_REQUEST = """
Analyse the following monthly business performance.

All figures are in GBP.

January:
- Revenue: 120,000
- Operating costs: 85,000
- Customers: 1,000

February:
- Revenue: 135,000
- Operating costs: 92,000
- Customers: 1,080

March:
- Revenue: 128,000
- Operating costs: 101,000
- Customers: 1,120

Calculate and explain:

1. Monthly operating profit.
2. Monthly operating margin.
3. Revenue per customer.
4. The most important positive trend.
5. The most important financial risk.
6. Three recommended management actions.

Keep the response concise and show the key calculations.
"""


def test_financial_analyst() -> None:
    credential = DefaultAzureCredential()

    try:
        with AIProjectClient(
            endpoint=project_endpoint,
            credential=credential,
        ) as project_client:

            with project_client.get_openai_client(
                agent_name=agent_name
            ) as openai_client:

                conversation = openai_client.conversations.create(
                    items=[
                        {
                            "type": "message",
                            "role": "user",
                            "content": TEST_REQUEST,
                        }
                    ]
                )

                print(f"Conversation created: {conversation.id}")
                print("Waiting for the financial analyst...\n")

                response = openai_client.responses.create(
                    conversation=conversation.id,
                )

                print("FINANCIAL ANALYSIS")
                print("=" * 60)
                print(response.output_text)

                openai_client.conversations.delete(
                    conversation_id=conversation.id
                )

                print("\nConversation deleted.")

    finally:
        credential.close()


if __name__ == "__main__":
    test_financial_analyst()