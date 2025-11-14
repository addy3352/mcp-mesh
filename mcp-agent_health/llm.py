import os
import json
import openai

# Initialize the OpenAI client
# It will automatically use the OPENAI_API_KEY from the environment
client = openai.AsyncOpenAI()

def get_prompt():
    with open("prompt.txt", "r") as f:
        return f.read()

async def get_llm_recommendation(data):
    prompt = get_prompt()
    
    # Format the data for the LLM
    data_str = json.dumps(data, indent=2)
    
    full_prompt = f"{prompt}\n\nHere is the latest health data:\n{data_str}"
    
    try:
        completion = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI health assistant. Your response must be a JSON object."},
                {"role": "user", "content": full_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        llm_response = completion.choices[0].message.content
        
        return json.loads(llm_response)
        
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return {"error": "Failed to get LLM recommendation"}
