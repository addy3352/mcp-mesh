
def list_tools():
    return [
        {
            "name": "nutrition.write_meal",
            "description": "Log a meal with calories/macros into nutrition DB",
            "input_schema": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "format": "date"},
                    "meal": {"type": "string"},
                    "description": {"type": "string"},
                    "calories": {"type": "number"},
                    "protein": {"type": "number"},
                    "carbs": {"type": "number"},
                    "fat": {"type": "number"}
                },
                "required": ["date", "meal", "calories"]
            }
        },
        {
            "name": "nutrition.get_daily_summary",
            "description": "Get total calories/macros for a given date",
            "input_schema": {
                "type": "object",
                "properties": { "date": {"type":"string","format":"date"} },
                "required": ["date"]
            }
        },
        {
            "name": "nutrition.list_meals",
            "description": "List meals for a date or date range",
            "input_schema": {
                "type": "object",
                "properties": {
                    "date": {"type":"string","format":"date"},
                    "start_date": {"type":"string","format":"date"},
                    "end_date": {"type":"string","format":"date"}
                }
            }
        }
    ]
