# MCP-Powered Financial Analyst

An educational Python project demonstrating how GitHub Copilot in Visual
Studio Code can discover and invoke a custom Model Context Protocol tool that
delegates financial analysis to a Microsoft Foundry prompt agent.

## Purpose

This project demonstrates:

- The MCP host-client-server architecture
- MCP tool definition and discovery
- Tool schema generation from Python type hints
- Tool selection and invocation by GitHub Copilot
- Integration between an MCP server and Microsoft Foundry
- Microsoft Entra ID authentication through `DefaultAzureCredential`
- Input validation, structured logging and unit testing
- The difference between MCP integration and direct API integration

This is an educational prototype. It is not intended to provide investment,
tax, legal or regulated financial advice.

## Architecture

```text
User
  ↓
GitHub Copilot in Visual Studio Code
  ↓
VS Code MCP host
  ↓
VS Code-managed MCP client
  ↓ MCP over stdio
Local Python MCP server
  ↓ analyse_finances
Financial analysis and validation layer
  ↓
Azure AI Projects SDK
  ↓
Microsoft Foundry financial-analyst agent
  ↓
Financial analysis
  ↓
MCP tool result
  ↓
GitHub Copilot
  ↓
User
```

## Component responsibilities

| Component | Responsibility |
|---|---|
| GitHub Copilot | Interprets the user request and selects an appropriate tool |
| Visual Studio Code | Hosts the MCP client and manages trust and tool invocation |
| MCP server | Exposes the `analyse_finances` capability |
| Validation layer | Validates input and handles application-level errors |
| Foundry client | Authenticates and invokes the Foundry agent |
| Foundry agent | Produces financial reasoning and recommendations |
| Microsoft Entra ID | Authenticates the local application to Azure |

## Prerequisites

- Visual Studio Code with GitHub Copilot enabled
- Python 3.13
- `uv`
- Azure CLI
- A Microsoft Foundry project
- A deployed model
- An existing Foundry prompt agent called `financial-analyst`
- The Foundry User role on the project

## Installation

Clone or open the project and install its dependencies:

```bash
uv sync
```

Verify Python:

```bash
uv run python --version
```

## Azure authentication

Sign in:

```bash
az login
```

Check the active account and subscription:

```bash
az account show --output table
```

If necessary, select the correct subscription:

```bash
az account set --subscription "YOUR SUBSCRIPTION NAME OR ID"
```

The application uses `DefaultAzureCredential`. During local development it
uses the Azure CLI credential established by `az login`.

No Azure password, access token or API key is stored in the project.

## Configuration

Copy the example configuration:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Set:

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
FOUNDRY_AGENT_NAME=financial-analyst
FOUNDRY_MODEL_NAME=YOUR-MODEL-DEPLOYMENT-NAME
```

Do not commit `.env`.

## Test the Foundry integration directly

```bash
uv run python src/test_foundry_client.py
```

This test calls the real Foundry agent and may consume model tokens.

## Run the automated unit tests

```bash
uv run pytest -v
```

The unit tests mock the Foundry call. They do not call Azure and do not consume
model tokens.

Run coverage:

```bash
uv run pytest --cov=src.financial_analysis --cov-report=term-missing
```

## Test with MCP Inspector

```bash
uv run mcp dev src/mcp_server.py
```

In the Inspector:

1. List the available tools.
2. Select `analyse_finances`.
3. Check its input schema.
4. Supply `financial_data` and `question`.
5. Invoke the tool.
6. Inspect the structured result.

## Connect from Visual Studio Code

The workspace-root `.mcp.json` contains:

```json
{
  "mcpServers": {
    "financial-analyst-local": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "python",
        "src/mcp_server.py"
      ],
      "tools": [
        "analyse_finances"
      ]
    }
  }
}
```

Open:

```text
Chat: Open Customizations → MCP Servers
```

Start `financial-analyst-local` and confirm that `analyse_finances` is
available.

## Example Copilot prompt

```text
Use the analyse_finances tool to analyse this data:

January:
- Revenue: £120,000
- Operating costs: £85,000

February:
- Revenue: £135,000
- Operating costs: £92,000

Calculate operating profit and margin for each month. Identify the main trend,
the most significant risk and two recommended management actions.
```

Verify that Copilot shows an actual `analyse_finances` tool invocation. A
correct answer without a tool-call record does not prove that MCP was used.

## MCP tool contract

### Tool

```text
analyse_finances
```

### Inputs

| Input | Type | Required | Limit |
|---|---|---|---:|
| `financial_data` | String | Yes | 20,000 characters |
| `question` | String | Yes | 2,000 characters |

### Example result

```json
{
  "status": "success",
  "analysis": "January operating profit was £35,000...",
  "source": "Microsoft Foundry financial-analyst agent"
}
```

## Logging

The server writes structured JSON logs to `stderr`.

`stdout` is reserved for MCP protocol messages when using the `stdio`
transport. Do not add `print()` statements to the MCP server.

The application logs metadata such as input length, but does not intentionally
log the supplied financial data.

## Security controls

V1 includes:

- Microsoft Entra ID authentication
- No embedded Azure credentials
- Explicit MCP tool allow-listing
- Input-size limits
- Basic financial-data shape validation
- Safe user-facing errors
- Structured logging to `stderr`
- Temporary isolated Foundry conversations
- Unit tests that mock external model calls

## Known limitations

- The agent uses probabilistic model reasoning.
- Calculations are not guaranteed to be deterministic.
- Validation does not confirm that financial figures are accurate.
- Free-form text is returned rather than a strict financial schema.
- Conversation history is not retained across tool calls.
- The server uses a local `stdio` connection.
- There is no central telemetry platform or distributed trace.
- The solution is not approved for regulated financial advice.
- The server has not been deployed for multiple users.

## Troubleshooting

### Azure authentication fails

```bash
az login
az account show --output table
```

Check that the account has the Foundry User role.

### The agent cannot be found

Confirm:

```dotenv
FOUNDRY_AGENT_NAME=financial-analyst
```

### VS Code does not show the tool

1. Check `.mcp.json`.
2. Reload the VS Code window.
3. Restart the MCP server.
4. Start a new Copilot session.
5. Confirm the `analyse_finances` tool is enabled.

### The MCP protocol is corrupted

Remove `print()` calls from code executed by the MCP server. Use logging
configured for `stderr`.

## Project files

| File | Purpose |
|---|---|
| `src/create_agent.py` | Creates or versions the Foundry prompt agent |
| `src/foundry_client.py` | Invokes the Foundry agent |
| `src/financial_analysis.py` | Validates and orchestrates analysis requests |
| `src/mcp_server.py` | Exposes the MCP tool |
| `tests/test_financial_analysis.py` | Tests validation |
| `tests/test_mcp_tool.py` | Tests orchestration with a mocked Foundry call |
| `.mcp.json` | Configures the server for VS Code |
| `.env.example` | Documents environment variables safely |

## Licence and disclaimer

This project is intended for learning and prototyping. Its outputs should be
independently reviewed before being used in financial, operational or
commercial decisions.