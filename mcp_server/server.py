import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import mcp_tools

app = FastAPI(title="Migration Control Protocol Server", version="1.0.0")
class ToolCallRequest(BaseModel):
    params: Dict[str, Any]

@app.get("/", summary="Health Check")
async def health_check():
    return {"status": "ok", "message": "MCP Server is running."}

@app.post("/call/{tool_name}", summary="Execute a registered tool")
async def call_tool(tool_name: str, request: ToolCallRequest):
    if not hasattr(mcp_tools, tool_name):
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")
    tool_function = getattr(mcp_tools, tool_name)
    try:
        print(f"MCP Server: Received call for tool '{tool_name}' with params: {request.params}")
        result = tool_function(**request.params)
        print(f"MCP Server: Tool '{tool_name}' executed successfully.")
        return {"result": result}
    except Exception as e:
        error_msg = f"Error executing tool '{tool_name}': {e}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)