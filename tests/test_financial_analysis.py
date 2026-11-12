import pytest

from mcp_financial_analyst.financial_analysis import (
    MAX_FINANCIAL_DATA_CHARACTERS,
    MAX_QUESTION_CHARACTERS,
    looks_like_financial_data,
    validate_analysis_request,
)


def test_valid_financial_data_is_accepted() -> None:
    data, question = validate_analysis_request(
        financial_data=(
            "Revenue was £120,000 and operating costs were £85,000."
        ),
        question="Calculate operating profit.",
    )

    assert "£120,000" in data
    assert question == "Calculate operating profit."


def test_whitespace_is_normalised() -> None:
    data, question = validate_analysis_request(
        financial_data="  Revenue: £120,000\r\nCosts: £85,000  ",
        question="  Calculate profit.  ",
    )

    assert data == "Revenue: £120,000\nCosts: £85,000"
    assert question == "Calculate profit."


@pytest.mark.parametrize(
    "financial_data",
    [
        "",
        "   ",
    ],
)
def test_empty_financial_data_is_rejected(
    financial_data: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="Financial data must be supplied",
    ):
        validate_analysis_request(
            financial_data=financial_data,
            question="Calculate profit.",
        )


def test_empty_question_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="analysis question must be supplied",
    ):
        validate_analysis_request(
            financial_data="Revenue: £120,000",
            question="  ",
        )


def test_oversized_financial_data_is_rejected() -> None:
    oversized_data = (
        "Revenue £100. "
        + "1" * MAX_FINANCIAL_DATA_CHARACTERS
    )

    with pytest.raises(
        ValueError,
        match="20,000-character",
    ):
        validate_analysis_request(
            financial_data=oversized_data,
            question="Analyse revenue.",
        )


def test_oversized_question_is_rejected() -> None:
    oversized_question = "x" * (
        MAX_QUESTION_CHARACTERS + 1
    )

    with pytest.raises(
        ValueError,
        match="2,000-character",
    ):
        validate_analysis_request(
            financial_data="Revenue: £120,000",
            question=oversized_question,
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Revenue was £120,000.", True),
        ("Operating margin was 21.5%.", True),
        ("Sales were 500 units.", True),
        ("This contains no numbers.", False),
        ("12345", False),
    ],
)
def test_financial_data_detection(
    value: str,
    expected: bool,
) -> None:
    assert looks_like_financial_data(value) is expected