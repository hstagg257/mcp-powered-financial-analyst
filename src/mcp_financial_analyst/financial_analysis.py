import logging
import re
from collections.abc import Callable
from typing import TypedDict


logger = logging.getLogger(__name__)


MAX_FINANCIAL_DATA_CHARACTERS = 20_000
MAX_QUESTION_CHARACTERS = 2_000

MIN_FINANCIAL_DATA_CHARACTERS = 10


class AnalysisResult(TypedDict, total=False):
    status: str
    analysis: str
    source: str
    message: str


FoundryAnalysisFunction = Callable[[str, str], str]


def normalise_text(value: str) -> str:
    """
    Remove leading and trailing whitespace and normalise line endings.
    """
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def looks_like_financial_data(value: str) -> bool:
    """
    Perform a lightweight check for numeric financial content.

    This is not intended to prove that the figures are correct. It only
    prevents clearly unsuitable or empty content from being sent to Foundry.
    """
    has_digit = bool(re.search(r"\d", value))

    has_financial_signal = bool(
        re.search(
            (
                r"£|\$|€|%|"
                r"\b(revenue|income|cost|costs|expense|expenses|"
                r"profit|loss|margin|budget|forecast|cash|customers|"
                r"sales|assets|liabilities)\b"
            ),
            value,
            flags=re.IGNORECASE,
        )
    )

    return has_digit and has_financial_signal


def validate_analysis_request(
    financial_data: str,
    question: str,
) -> tuple[str, str]:
    """
    Validate and normalise an analysis request.

    Returns:
        The normalised financial data and question.

    Raises:
        ValueError: If either input is missing, too large or unsuitable.
    """
    if not isinstance(financial_data, str):
        raise ValueError("financial_data must be a string.")

    if not isinstance(question, str):
        raise ValueError("question must be a string.")

    clean_data = normalise_text(financial_data)
    clean_question = normalise_text(question)

    if not clean_data:
        raise ValueError("Financial data must be supplied.")

    if not clean_question:
        raise ValueError("An analysis question must be supplied.")

    if len(clean_data) < MIN_FINANCIAL_DATA_CHARACTERS:
        raise ValueError(
            "The supplied financial data is too short to analyse."
        )

    if len(clean_data) > MAX_FINANCIAL_DATA_CHARACTERS:
        raise ValueError(
            "Financial data exceeds the 20,000-character V1 limit."
        )

    if len(clean_question) > MAX_QUESTION_CHARACTERS:
        raise ValueError(
            "The analysis question exceeds the 2,000-character V1 limit."
        )

    if not looks_like_financial_data(clean_data):
        raise ValueError(
            "The supplied content does not appear to contain numeric "
            "financial data."
        )

    return clean_data, clean_question


def run_financial_analysis(
    financial_data: str,
    question: str,
    foundry_analyser: FoundryAnalysisFunction,
) -> AnalysisResult:
    """
    Validate a request and invoke a supplied Foundry analysis function.

    Passing the Foundry function as a dependency makes this logic easy to
    test without calling Azure or consuming model tokens.
    """
    logger.info(
        "financial_analysis_requested",
        extra={
            "financial_data_length": len(financial_data),
            "question_length": len(question),
        },
    )

    try:
        clean_data, clean_question = validate_analysis_request(
            financial_data=financial_data,
            question=question,
        )

        analysis = foundry_analyser(
            clean_data,
            clean_question,
        )

        if not isinstance(analysis, str) or not analysis.strip():
            raise RuntimeError(
                "The Foundry agent returned an empty analysis."
            )

        logger.info("financial_analysis_completed")

        return {
            "status": "success",
            "analysis": analysis.strip(),
            "source": "Microsoft Foundry financial-analyst agent",
        }

    except ValueError as error:
        logger.warning(
            "financial_analysis_validation_failed",
            extra={"validation_error": str(error)},
        )

        return {
            "status": "error",
            "analysis": "",
            "message": str(error),
        }

    except Exception:
        logger.exception("financial_analysis_failed")

        return {
            "status": "error",
            "analysis": "",
            "message": (
                "The Microsoft Foundry financial analyst could not complete "
                "the request. Check Azure authentication, project access and "
                "the MCP server logs."
            ),
        }