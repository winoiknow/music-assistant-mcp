FROM python:3.12-slim

LABEL maintainer="music-assistant-mcp"
LABEL description="FastMCP server exposing Music Assistant API as MCP tools"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Environment variables  ^`^t override at runtime
ENV MA_URL="http://localhost:8095"
ENV MA_TOKEN=""

# Default: run with stdio transport (for MCP clients)
# Override with docker-compose command or docker run args for HTTP transport
CMD ["python", "server.py"]
