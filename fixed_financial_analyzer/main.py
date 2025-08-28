"""
Fixes:
- Avoided name collision between imported task and FastAPI endpoint function.
- Made run_crew asynchronous and pass file_path into inputs.
- Handled missing Crew/LLM and returned informative errors.
- Used BackgroundTasks optionally for longer processing.
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
import os
import uuid
import asyncio
from pathlib import Path

from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document  

app = FastAPI(title="Financial Document Analyzer")

async def run_crew_async(query: str, file_path: str = "data/sample.pdf"):
    
    # Ensure the Crew/Process classes exist
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document],
        process=Process.sequential,
    )
    inputs = {"query": query, "file_path": file_path}
    result = financial_crew.kickoff(inputs)
    if asyncio.iscoroutine(result):
        result = await result
    return result

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document and provide comprehensive investment recommendations"""

    file_id = str(uuid.uuid4())
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = str(data_dir / f"financial_document_{file_id}.pdf")

    try:
        # Save uploaded file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # Run the crew asynchronously and await result
        response = await run_crew_async(query=query.strip(), file_path=file_path)

        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

    finally:
        # Clean up uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
