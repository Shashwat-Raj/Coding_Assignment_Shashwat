from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
import json
from dotenv import load_dotenv

load_dotenv() # It loads gpt key from .env file securely(please use your key incase this gets restricted)
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("knowledge_base.json", "r") as f: # Retrieving knowledge base from JSON file
    documents = json.load(f) # i have provided some info about ML,Cloud,me(Shashwat). Please ask question around it or add extra knowledge into .json file

app = FastAPI()


class QueryInput(BaseModel): #input request model
    query: str

def retrieve_context(query: str):# retrieving most relevant document using TF-IDF (could have used openai Embedding too)
    texts = [doc["text"] for doc in documents]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts + [query]) #converting into vector form
    similarity = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]) # using cosine similarity to get best match
    best_match_index = similarity.argmax()
    return texts[best_match_index]

def generate_answer(query: str, context: str):#using language generation capability of open ai gpt 3.5
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip() # returning best choice from the list of choices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))#handling exception incase retireval or generation goes into error

# API endpoint to post query and get output
@app.post("/generate-summary")
def generate_summary(input: QueryInput):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured or key expired.")
    
    context = retrieve_context(input.query)  #serving llm with relevant similar document as a context
    answer = generate_answer(input.query, context)
    return {"answer": answer}
