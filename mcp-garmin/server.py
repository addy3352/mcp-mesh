from fastapi import FastAPI,HTTPException, Depends
from pydantic import BaseModel
#from router import router
from tools import list_tools
from typing import Any, Dict                                                                                                                                                                                
# Import all the tool functions and Pydantic models from your router file                                                                                                                            
# This allows us to call them directly from our new generic endpoint                                                                                                                                 
from router import (
    get_stats,
    get_user_summary,                                                                                                                                                                                
    get_stats_and_body,                                                                                                                                  
    get_steps_data,                                                                                                                 
    get_heart_rates,                                                                                                                                                                                 
    get_resting_hr,                                                                                                                                                                                  
    get_sleep_data,                                                                                                                                                                                  
    get_all_day_stress,                                                                                                                                                                              
    get_training_readiness,                                                                                                                                                                          
    get_training_status,                                                                                                                                                                             
    get_respiration_data,                                                                                                                                                                            
    get_spo2_data,                                                                                                                                                                                   
    get_max_metrics,                                                                                                                                                                                 
    get_hrv_data,                                                                                                                                                                                    
    get_fitnessage_data,                                                                                                                                                                             
    get_stress_data,                                                                                                                                                                                 
    get_lactate_threshold,                                                                                                                                                                           
    get_intensity_minutes,                                                                                                                                                                           
    get_activities_range,                                                                                                                                                                            
    sync_daily_data,                                                                                                                                                                                 
    DateBody,                                                                                                                                                                                        
    SyncBody,                                                                                                                                                                                        
    DateRange,                                                                                                                                                                                       
    get_client,      # The dependency factory function                                                                                                                                               
    GarminClient     # The dependency's type hint                                                                                                                                                    
    )
from tools import list_tools 
app = FastAPI(title="MCP Garmin Server")                                                                                                                                                                                                                                                                                                                                                                   
    # This Pydantic model defines the structure of the incoming request from the gateway                                                                                                                 
class ToolCall(BaseModel):
    name: str                                                                                                                                                                                        
    arguments: Dict[str, Any]                                                                                                                                                                                                                                                                                                                                                                              
    # This dispatch map connects the tool name string to the actual function that                                                                                                                       █
    # executes the tool and the Pydantic model it expects for its arguments.                                                                                         
tool_map = {
    "garmin.get_stats": (get_stats, DateBody),
    "garmin.get_user_summary": (get_user_summary, DateBody),   
    "garmin.get_stats_and_body": (get_stats_and_body, DateBody), 
    "garmin.get_steps_data": (get_steps_data, DateBody),
    "garmin.get_heart_rates": (get_heart_rates, DateBody),
    "garmin.get_resting_heart_rate": (get_resting_hr, DateBody),
    "garmin.get_sleep_data": (get_sleep_data, DateBody),
    "garmin.get_all_day_stress": (get_all_day_stress, DateBody),
    "garmin.get_training_readiness": (get_training_readiness, DateBody),
    "garmin.get_training_status": (get_training_status, DateBody),
    "garmin.get_respiration_data": (get_respiration_data, DateBody),
    "garmin.get_spo2_data": (get_spo2_data, DateBody),
    "garmin.get_max_metrics": (get_max_metrics, DateBody),
    "garmin.get_hrv_data": (get_hrv_data, DateBody),
    "garmin.get_fitnessage_data": (get_fitnessage_data, DateBody),
    "garmin.get_stress_data": (get_stress_data, DateBody),
    "garmin.get_lactate_threshold": (get_lactate_threshold, DateBody),
    "garmin.get_intensity_minutes_data": (get_intensity_minutes, DateBody),
    "garmin.get_activities_range": (get_activities_range, DateRange),
    "garmin.sync": (sync_daily_data, SyncBody)
}



# This is the new generic endpoint that matches the gateway's requests.                                                                                                                              
@app.post("/mcp/call")                                                                                                                                                                               
async def call_tool_generic(tool_call: ToolCall, client: GarminClient = Depends(get_client)):
    tool_name=tool_call.name
    args = tool_call.arguments
    if tool_name not in tool_map:                                                                                                                                                                    
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    target_func, body_model = tool_map[tool_name]                                                                                                                                                                                              
    # Create the required Pydantic model from the 'arguments' dictionary                                                                                                                             
    try:
        body = body_model(**args) if args else body_model()                                                                                                                                          
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid arguments for tool '{tool_name}': {e}")                                                                                                                                                                                                                                                                                                      
   # Call the target function, providing the client dependency where needed                                                                                                                         
    try:
        if tool_name == "garmin.sync":                                                                                                                                                               
                 # sync_daily_data does not require the 'client' dependency
            return await target_func(body)                                                                                                                                                          
        else:
            return await target_func(body, client)                                                                                                                                                  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool '{tool_name}': {e}")                                                                                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                              
                                                                                                                                                                 
                                                                                                                                                                                                    
    # The original router is no longer included because the new /mcp/call endpoint                                                                                                                       
 # handles all tool calls directly.                                                                                                                                                                   
    # from router import router                                                                                                                                                                         █
    # app.include_router(router, prefix="/mcp/call", tags=["garmin"]) 





@app.get("/ping")
def ping():
    return {"status":"ok","service":"mcp-garmin"}

@app.get("/mcp/tools")
def tools():
    return {"tools": list_tools()}

#app.include_router(router, prefix="/mcp/call", tags=["garmin"])
