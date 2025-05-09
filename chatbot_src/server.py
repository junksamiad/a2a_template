from fastapi import FastAPI
from fastapi.responses import JSONResponse # FileResponse no longer needed if not serving other files
from pathlib import Path
import json

# try:
#     from a2a import A2AServer
# except ImportError:  # placeholder if library not yet installed
#     A2AServer = None  # type: ignore

# try:
#     from mcp.server import MCPServerStdio  # example; adjust once mcp-server lib API is confirmed
# except ImportError:
#     MCPServerStdio = None  # type: ignore

BASE_DIR = Path(__file__).resolve().parent
AGENT_CARD_PATH = BASE_DIR / "agent.json"

if not AGENT_CARD_PATH.exists():
    raise FileNotFoundError("agent.json not found – ensure it exists before starting the server.")

with AGENT_CARD_PATH.open() as f:
    agent_card_data = json.load(f)

app = FastAPI(title="Urmston Town Agent Card Service") # Simplified title

# Instantiate A2A server if library available - COMMENTED OUT FOR MINIMAL DEPLOY
# if A2AServer is not None:
#     try:
#         from . import skills # Ensures skills are loaded for discovery by A2AServer
#     except ImportError as e:
#         print(f"Warning: Could not import skills.py for A2A server: {e}")
# 
#     a2a_server = A2AServer(agent_card=agent_card_data)
#     app.include_router(a2a_server.router, prefix="") # Mounts A2A routes like /tasks/send

# Instantiate MCP server - COMMENTED OUT FOR MINIMAL DEPLOY
# if MCPServerStdio is not None:
#     mcp_server = MCPServerStdio(params={"command": "echo", "args": ["MCP placeholder"]})
#     app.include_router(mcp_server.router, prefix="/tasks") # MCP default prefix is often /mcp


@app.get("/.well-known/agent.json", response_class=JSONResponse, tags=["discovery"])
async def get_agent_card():
    """Return the static agent card."""
    return agent_card_data 