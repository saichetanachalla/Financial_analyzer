"""
Fixes:
- Removed self-referential llm variable (was: llm = llm).
- Provided a safe llm fallback (None) and attempt to initialize an OpenAI-like LLM when OPENAI_API_KEY is present.
- Cleaned and corrected agent prompts to avoid hallucination and unsafe instructions.
- Used consistent 'tools' parameter name and pass callable references.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.agents import Agent

llm = None
try:
    # Attempting to import an LLM from crewai (if available). If not present, llm stays None.
    from crewai.llms import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm = OpenAI(api_key=api_key)
except Exception:
    llm = None

from tools import search_tool, FinancialDocumentTool

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Analyze the provided financial document, extract key financial statements and metrics, compute commonly used ratios, and provide a clear, well-explained summary. If calculations are uncertain, state assumptions explicitly.",
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced financial analyst. You read documents carefully, extract numbers precisely, and avoid making up facts."
        "Always include a short disclaimer that this is not personalized financial advice."
    ),
    tools=[FinancialDocumentTool.read_data_tool, search_tool] if hasattr(FinancialDocumentTool, "read_data_tool") else [search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=True
)

# Creating a document verifier agent 
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify whether the uploaded file looks like a financial document. Return a JSON-like summary with keys: is_financial_document (bool), doc_type (e.g., 'financial_statement', 'invoice', 'unknown'), and short_explanation.",
    verbose=True,
    memory=False,
    backstory=(
        "You were trained to identify common financial documents (balance sheet, income statement, cash flow)."
        "If uncertain, return is_financial_document: False and explain why."
    ),
    tools=[FinancialDocumentTool.read_data_tool] if hasattr(FinancialDocumentTool, "read_data_tool") else [],
    llm=llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)

investment_advisor = Agent(
    role="Investment Advisor (Educational Only)",
    goal="Based on extracted financial metrics, provide educational insights: possible strengths, weaknesses, and what an investor might want to investigate further. Do NOT sell products or provide personalized financial advice.",
    verbose=True,
    memory=False,
    backstory=(
        "You provide general educational commentary about investments and risks."
    ),
    llm=llm,
    tools=[FinancialDocumentTool.read_data_tool] if hasattr(FinancialDocumentTool, "read_data_tool") else [],
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)


risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal="Using computed ratios and available data, produce a concise risk assessment with clear reasoning, assumptions, and recommended next steps for due diligence.",
    verbose=True,
    memory=False,
    backstory=(
        "You are focused on coherent, well-explained risk assessments based on available data."
    ),
    llm=llm,
    tools=[FinancialDocumentTool.read_data_tool] if hasattr(FinancialDocumentTool, "read_data_tool") else [],
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)
