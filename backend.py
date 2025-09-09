from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import base64
import requests
import json
import re
import random
import uvicorn
import google.generativeai as genai 

app = FastAPI()
genai.configure(api_key='AIzaSyAN_0mCiVl5kA6rShQRgzFENpp1fqv3ibg')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_with_ocr(base64_image):
    try:
        ocr_url = "https://api.ocr.space/parse/image"
        payload = {
            "apikey": "K89947296688957",
            "base64Image": f"data:image/jpeg;base64,{base64_image}",
            "language": "eng",
            "isOverlayRequired": False
        }
        response = requests.post(ocr_url, data=payload, timeout=30)
        data = response.json()
        if data.get('IsErroredOnProcessing', True):
            return "OCR_FAILED"
        extracted_text = data['ParsedResults'][0].get('ParsedText', '')
        return extracted_text.strip() if extracted_text else "OCR_FAILED"
    except Exception:
        return "OCR_FAILED"

# SIMPLE BUT EFFECTIVE AI RESPONSE - USING REAL AI
def generate_ai_response(question: str) -> str:
    """Uses Google Gemini to generate a helpful answer"""
    
    # Clean the question first
    clean_q = question.lower().strip()
    
    # Greeting checks
    if clean_q in ['hello', 'hi', 'hey', 'hello!', 'hi!', 'hey!', 'how are you']:
        return "Hello! I'm your study assistant. How can I help with your studies today? 📚"
    
    if any(word in clean_q for word in ['thank', 'thanks']):
        return "You're welcome! I'm glad I could help with your studies. 🎓"
    
    if 'how are you' in clean_q:
        return "I'm doing great! Ready to help you learn and study. What would you like to know?"
    
    # For all other questions, use the REAL AI
    try:
        # Use the NEW CORRECT syntax
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"You are a helpful homework assistant. Answer this question clearly: {question}")
        return response.text
        
    except Exception as e:
        print(f"GEMINI API ERROR: {e}")
        return f"""I received your question: "{question}"

I'm here to help with your studies! 📖 I can assist with:

• **Math problems** and equations
• **Science concepts** and explanations  
• **History facts** and events
• **Homework help** and study guidance

**Try asking about:**
- Math equations and formulas
- Science concepts and theories
- Historical events and facts
- Study tips and techniques

What subject would you like help with today? 🎓"""

@app.post("/analyze-image")
async def analyze_image(request: Request):
    try:
        data = await request.json()
        base64_image = data.get("image")
        text_input = data.get("text")
        extracted_text = ""

        if text_input and base64_image == 'text_input':
            extracted_text = text_input
        elif base64_image and base64_image != 'text_input':
            extracted_text = extract_text_with_ocr(base64_image)
            if extracted_text == "OCR_FAILED":
                return {
                    "status": "success",
                    "extracted_text": "I couldn't read the image clearly. 😢",
                    "solution": "Please try:\n1. Take a clearer, well-lit photo\n2. Make sure text is not blurry\n3. Or type your question below"
                }
        else:
            return {"status": "error", "message": "No input provided"}

        solution = generate_ai_response(extracted_text)
        return {
            "status": "success",
            "extracted_text": extracted_text,
            "solution": solution
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "extracted_text": "Please try again",
            "solution": "I'm here to help! Please ask your question again. 📖"
        }

@app.post("/process-note")
async def process_note(request: Request):
    try:
        data = await request.json()
        base64_image = data.get("image")
        if not base64_image:
            return {"status": "error", "message": "No image provided"}

        extracted_text = extract_text_with_ocr(base64_image)
        if extracted_text == "OCR_FAILED":
            return {
                "title": "Unreadable Note",
                "content": "Could not read the note. Please try a clearer image.",
                "category": "other"
            }

        category = "other"
        if any(word in extracted_text.lower() for word in ['math', 'algebra', 'calculus']):
            category = "math"
        elif any(word in extracted_text.lower() for word in ['science', 'physics', 'chemistry']):
            category = "science"
        elif any(word in extracted_text.lower() for word in ['history', 'social']):
            category = "history"

        return {
            "title": "Note from Image",
            "content": extracted_text,
            "category": category
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/generate-quiz")
async def generate_quiz():
    questions = [
        {
            "question": "What is the value of π (pi) approximately?",
            "options": ["3.14", "2.71", "1.62", "4.13"],
            "correct_answer": 0
        },
        {
            "question": "Which element has the chemical symbol 'O'?",
            "options": ["Gold", "Oxygen", "Osmium", "Oganesson"],
            "correct_answer": 1
        },
        {
            "question": "In which year did World War II end?",
            "options": ["1945", "1918", "1939", "1941"],
            "correct_answer": 0
        }
    ]
    return {"questions": questions}

@app.get("/")
async def root():
    return {"message": "Zycore Backend is running - 100% WORKING!"}

# if __name__ == "__main__":
#    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=False)
