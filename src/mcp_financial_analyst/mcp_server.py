import json
import logging
import sys
from datetime import datetime, timezone

from mcp.server import MCPServer

from .financial_analysis import run_financial_analysis
from .foundry_client import invoke_financial_analyst


class JsonLogFormatter(logging.Formatter):
    """
    Format application logs as single-line JSON records.
    """

    standard_attributes = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in self.standard_attributes:
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_entry,
            default=str,
            ensure_ascii=False,
        )


def configure_logging() -> None:
    """
    Configure JSON logging to stderr.

    stdout must remain reserved for MCP stdio protocol messages.
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonLogFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


configure_logging()

logger = logging.getLogger(__name__)

mcp = MCPServer("Financial Analyst MCP Server")


@mcp.tool()
def analyse_finances(
    financial_data: str,
    question: str,
) -> dict[str, str]:
    """
    Analyse supplied business financial data using the Microsoft Foundry
    financial analyst agent.

    Use this tool when the user provides financial figures and asks for
    calculations, trend analysis, variance analysis, risks, insights or
    recommended management actions.

    Do not use this tool for live market prices, regulated financial advice,
    tax advice or legal advice.

    Args:
        financial_data: The financial figures and business context to analyse.
        question: The specific financial analysis the user wants performed.

    Returns:
        The analysis returned by the Microsoft Foundry financial analyst.
    """
    logger.info("Received an analyse_finances MCP tool request.")

    if not financial_data.strip():
        return {
            "status": "error",
            "analysis": "",
            "message": "Financial data must be supplied.",
        }

    if not question.strip():
        return {
            "status": "error",
            "analysis": "",
            "message": "An analysis question must be supplied.",
        }

    try:
        analysis = invoke_financial_analyst(
            financial_data=financial_data,
            question=question,
        )

        logger.info("Foundry financial analysis completed.")

        return {
            "status": "success",
            "analysis": analysis,
            "source": "Microsoft Foundry financial-analyst agent",
        }

    except Exception:
        logger.exception(
            "The Foundry financial analysis request failed."
        )

        return {
            "status": "error",
            "analysis": "",
            "message": (
                "The Microsoft Foundry financial analyst could not complete "
                "the request. Check Azure authentication, project access and "
                "the MCP server logs."
            ),
        }


if __name__ == "__main__":
    mcp.run()