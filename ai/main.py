


import os
import re
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# --- 1. Load .env reliably ---
BASE_DIR = Path(__file__).resolve().parent
dotenv_path = BASE_DIR / ".env"
print("Loading .env from:", dotenv_path)

# Force load .env file
load_dotenv(dotenv_path=str(dotenv_path))

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print("GEMINI_API_KEY loaded successfully.")
else:
    print("WARNING: GEMINI_API_KEY not found. Gemini API calls will fail until this is set.")

# --- 2. Import course data ---
from course_data import COURSE_CATALOG_CHUNKS

# --- 3. FastAPI setup ---
app = FastAPI(
    title="IntelliCourse AI Assistant API",
    description="A REST API for querying Northwood University's course catalogs using the Gemini API (RAG). 🚀"
)

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Pydantic Models ---
class QueryRequest(BaseModel):
    user_query: str

class QueryResponse(BaseModel):
    answer: str

# --- 5. Initialize Gemini client ---
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Gemini client initialized successfully.")
    except Exception as e:
        client = None
        print(f"ERROR: Could not initialize Gemini client. Details: {e}")
else:
    print("Gemini client NOT initialized. Set GEMINI_API_KEY to enable AI responses.")

# --- 6. Core RAG Logic ---
def get_course_answer(user_query: str) -> str:
    """
    Implements the Retrieval-Augmented Generation (RAG) pipeline 
    to answer course-related questions using Gemini 2.5 Flash.
    """
    query_lower = user_query.lower()
    search_terms = re.findall(r'[a-z]{2,4}\s*\d{3}', query_lower)
    search_terms.extend([word for word in query_lower.split() if len(word) > 2])

    retrieved_context = [
        chunk for chunk in COURSE_CATALOG_CHUNKS
        if any(term in chunk.lower() for term in search_terms)
    ]

    unique_context = "\n---\n".join(list(set(retrieved_context)))

    if not unique_context:
        return "I'm sorry, I couldn't find any relevant course information in the catalog."

    system_instruction = (
        "You are IntelliCourse, an AI assistant for Northwood University's course catalog. "
        "Answer questions only using the provided course context. Be concise, direct, and accurate."
    )

    prompt = f"""
    CONTEXT:
    {unique_context}
    
    USER QUESTION: {user_query}
    
    GENERATED ANSWER:
    """

    if not client:
        return "Gemini API client not initialized. Cannot generate AI answer."

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "An internal error occurred while generating the answer."

# --- 7. FastAPI Endpoints ---
@app.post("/api/query", response_model=QueryResponse, tags=["IntelliCourse"])
async def query_catalog(request: QueryRequest):
    try:
        answer = get_course_answer(request.user_query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", tags=["Health"])
async def root():
    return {"message": "IntelliCourse API is running! Access /docs for the interface."}
