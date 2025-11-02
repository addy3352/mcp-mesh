
def list_tools():
    return [
        {
            "name": "linkedin.create_post",
            "description": "Publish an architecture/governance update to LinkedIn (no health/PII).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "visibility": {"type": "string", "enum": ["PUBLIC", "CONNECTIONS"]}
                },
                "required": ["message"]
            }
        }
    ]
