
def list_tools():
    return [
        {
            "name": "portal.update_health_panel",
            "description": "Update DO Portal health dashboard with a daily snapshot + recommendation.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date"},
                    "steps": {"type": "number"},
                    "calories": {"type": "number"},
                    "rhr": {"type": "number"},
                    "hrv": {"type": "number"},
                    "sleep_hours": {"type": "number"},
                    "stress_score": {"type": "number"},
                    "recommendation": {"type": "string"}
                },
                "required": ["date","recommendation"]
            }
        }
    ]
