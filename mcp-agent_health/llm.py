from mcp_client import call_tool
import json

def get_prompt():
    with open("prompt.txt", "r") as f:
        return f.read()

async def get_llm_recommendation(data):
    prompt = get_prompt()
    
    # Format the data for the LLM
    # (This can be improved to be more structured)
    data_str = json.dumps(data, indent=2)
    
    full_prompt = f"{prompt}\n\nHere is the latest health data:\n{data_str}"
    
    llm_response = await call_tool("core.llm_completion", {"prompt": full_prompt})
    
    try:
        # Assuming the LLM returns a JSON string as requested in the prompt
        return json.loads(llm_response.get("result", "{}"))
    except json.JSONDecodeError:
        # Handle cases where the LLM doesn't return valid JSON
        return {"error": "Failed to decode LLM response", "raw_response": llm_response}
