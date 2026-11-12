from unittest.mock import Mock

from mcp_financial_analyst.financial_analysis import run_financial_analysis


def test_successful_analysis_uses_foundry_dependency() -> None:
    mock_foundry = Mock(
        return_value=(
            "Operating profit was £35,000 and margin was 29.2%."
        )
    )

    result = run_financial_analysis(
        financial_data=(
            "Revenue was £120,000 and costs were £85,000."
        ),
        question="Calculate operating profit and margin.",
        foundry_analyser=mock_foundry,
    )

    assert result["status"] == "success"
    assert "£35,000" in result["analysis"]
    assert result["source"] == (
        "Microsoft Foundry financial-analyst agent"
    )

    mock_foundry.assert_called_once_with(
        "Revenue was £120,000 and costs were £85,000.",
        "Calculate operating profit and margin.",
    )


def test_invalid_input_does_not_call_foundry() -> None:
    mock_foundry = Mock()

    result = run_financial_analysis(
        financial_data="This is not financial information.",
        question="Analyse it.",
        foundry_analyser=mock_foundry,
    )

    assert result["status"] == "error"
    assert result["analysis"] == ""
    assert "numeric financial data" in result["message"]

    mock_foundry.assert_not_called()


def test_foundry_failure_returns_safe_error() -> None:
    mock_foundry = Mock(
        side_effect=RuntimeError(
            "Internal Azure infrastructure detail"
        )
    )

    result = run_financial_analysis(
        financial_data="Revenue: £120,000",
        question="Analyse revenue.",
        foundry_analyser=mock_foundry,
    )

    assert result["status"] == "error"
    assert result["analysis"] == ""
    assert "could not complete" in result["message"]
    assert "Internal Azure" not in result["message"]


def test_empty_foundry_response_returns_error() -> None:
    mock_foundry = Mock(return_value="")

    result = run_financial_analysis(
        financial_data="Revenue: £120,000",
        question="Analyse revenue.",
        foundry_analyser=mock_foundry,
    )

    assert result["status"] == "error"
    assert "could not complete" in result["message"]


def test_inputs_are_normalised_before_foundry_call() -> None:
    mock_foundry = Mock(return_value="Analysis complete.")

    result = run_financial_analysis(
        financial_data="  Revenue: £120,000\r\nCosts: £85,000  ",
        question="  Calculate profit.  ",
        foundry_analyser=mock_foundry,
    )

    assert result["status"] == "success"

    mock_foundry.assert_called_once_with(
        "Revenue: £120,000\nCosts: £85,000",
        "Calculate profit.",
    )