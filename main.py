from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openai
import os
import tempfile

# Load your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Allow frontend requests (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    try:
        # Read uploaded file
        contents = await file.read()

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        # Read file content as text
        with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
            contract_text = f.read()

        os.remove(tmp_path)

        # GPT-4o Prompt
        prompt = (
            "You are a legal AI assistant. Read the contract below. "
            "Summarise key clauses, obligations, risks, and any hidden traps. "
            "Explain it in plain English.\n\n"
            f"{contract_text}\n\nSummary:"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )

        summary = response["choices"][0]["message"]["content"]
        return JSONResponse(content={"summary": summary})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
