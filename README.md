[README.md](https://github.com/user-attachments/files/22029601/README.md)
# Financial Document Analyzer - Debug Assignment

This repository contains a version of a Financial Document Analyzer originally built using CrewAI.  

## Fixes

### Deterministic bugs
- NameError / self-referential llm: `agents.py` contained `llm = llm` which raised a `NameError`. Replaced with safe LLM initialization that falls back to `None`.
- PDF reading: `tools.py` used an undefined `Pdf` class and was missing imports. Rewrote PDF reader using `PyPDF2.PdfReader`.
- Endpoint name collision: `main.py` imported `analyze_financial_document` from `task.py` but also defined a function with the same name for the FastAPI endpoint. Renamed the endpoint to `analyze_endpoint`.
- run_crew did not pass file path: `run_crew` in `main.py` did not pass `file_path` into the crew kickoff inputs. Fixed by making it asynchronous and passing both `query` and `file_path`.
- Tools and tasks references: Standardized the tools callables and used `@staticmethod` to make them easy to pass into agents/tasks.

### Inefficient/unsafe prompts
- Replaced prompts that encouraged hallucination, fabrication, or unsafe financial advice with precise, safety-focused prompts:
  - Agents now explicitly avoid fabricating facts and include disclaimers.
  - Tasks describe structured outputs (verification, extracted values, ratios, summary, assumptions, next steps).
  - Verification agent now returns structured verification info.

## Improved components
- `tools.py`:
  - `FinancialDocumentTool.read_data_tool(path)` — reads PDF using PyPDF2 and returns normalized text.
  - `InvestmentTool.analyze_investment_tool(text)` — simple deterministic extraction and ratio computation.
  - `RiskTool.create_risk_assessment_tool(text)` — simple deterministic risk heuristics.
  - `search_tool(query)` — deterministic, safe stub (replaceable with Serp/Serper integration).

- `agents.py`:
  - Agents rewritten with safer backstories, limits on iteration, more helpful goals, and consistent `tools` usage.

- `task.py`:
  - Clear task descriptions and expected output formats. Tasks are deterministic and structured.

- `main.py`:
  - Async `run_crew_async`, cleaned-up endpoint `analyze_endpoint`, safe file handling and cleanup.

## Setup & Usage

1. Clone the fixed repo (or copy these files into your project):
   ```bash
   git clone <your-repo-url>
   cd fixed_financial_analyzer
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows use venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Example `requirements.txt` (not included automatically):
   ```
   fastapi
   uvicorn
   python-dotenv
   PyPDF2
   crewai  # if you use the original CrewAI package
   crewai_tools  # optional, if you integrate real search tools
   ```

3. Set environment variables (optional)
   - `OPENAI_API_KEY` if you want to enable an OpenAI-backed LLM for CrewAI (if supported).
   - Any CrewAI-specific config.

4. Run the API
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. Test the `/analyze` endpoint
   Use `curl` or Postman to POST a PDF file and an optional `query` form field.

   Example `curl`:
   ```bash
   curl -X POST "http://127.0.0.1:8000/analyze" \
     -F "file=@/path/to/financial_report.pdf" \
     -F "query=Summarize the company's financial health"
   ```

## API Documentation

- `GET /` - Health check. Returns `{"message":"Financial Document Analyzer API is running"}`.
- `POST /analyze` - Upload a PDF and an optional `query` form string. Returns:
  ```json
  {
    "status": "success",
    "query": "...",
    "analysis": "string (structured output from CrewAI)",
    "file_processed": "original_filename.pdf"
  }
  ```


If you'd like, I can:
- Add a `docker-compose.yml` with Redis + Celery + FastAPI setup.
- Implement a Celery-based worker and example tasks.
- Add a small SQLite DB integration with SQLAlchemy and example migrations.

