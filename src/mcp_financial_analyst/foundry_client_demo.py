from mcp_financial_analyst.foundry_client import invoke_financial_analyst


TEST_DATA = """
January:
- Revenue: £120,000
- Operating costs: £85,000
- Customers: 1,000

February:
- Revenue: £135,000
- Operating costs: £92,000
- Customers: 1,080

March:
- Revenue: £128,000
- Operating costs: £101,000
- Customers: 1,120
"""


TEST_QUESTION = """
Calculate monthly operating profit and operating margin.

Then identify:
1. The strongest positive trend.
2. The most important financial risk.
3. Three actions management should consider.
"""


def main() -> None:
    analysis = invoke_financial_analyst(
        financial_data=TEST_DATA,
        question=TEST_QUESTION,
    )

    print("FINANCIAL ANALYSIS")
    print("=" * 60)
    print(analysis)


if __name__ == "__main__":
    main()