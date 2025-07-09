from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# It loads gpt key from .env file securely
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI() #creating fastAPI app

class TextInput(BaseModel):#takes input text
    text: str

class SummaryOutput(BaseModel): # provides output summary
    summary: str

@app.post("/generate-summary", response_model=SummaryOutput)
async def generate_summary(input: TextInput):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured or key expired.")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes text and provides concise summary."},
                {"role": "user", "content": f"Summarize this: {input.text}"}
            ],
            max_tokens=200,
            temperature=0.4 # keeping temperature 0.4 to keep balanced randomness
        )
        summary = response.choices[0].message.content.strip()#choosing best response from the llm
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
