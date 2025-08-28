"""
Fixes:
- Rewrote task descriptions and expected outputs to be clear.
- Used the verifier agent for verification tasks and financial_analyst for analysis.
- Kept tasks deterministic and structured.
"""
from crewai import Task

from agents import financial_analyst, verifier
from tools import FinancialDocumentTool, InvestmentTool, RiskTool, search_tool

analyze_financial_document = Task(
    description=(
        "Analyze the uploaded financial document. Steps:\n"
        "1) Verify the document type.\n"
        "2) Extract key financial statements (balance sheet, income statement, cash flow) where possible.\n"
        "3) Compute basic financial ratios (profit margin, debt-to-equity, ROA) heuristically.\n"
        "4) Produce a concise summary, a list of assumptions, and recommended next steps for due diligence.\n"
        "Inputs available: {query}, and tools that can read the file."
    ),
    expected_output=(
        "Return a structured response (preferably JSON or bullet list) with these sections:\n"
        "- verification: {is_financial_document: bool, doc_type: str, explanation: str}\n"
        "- extracted_values: {revenue, net_income, total_assets, total_liabilities, equity}\n"
        "- ratios: {profit_margin, debt_to_equity, return_on_assets}\n"
        "- summary: short human-friendly summary\n"
        "- assumptions: list\n"
        "- next_steps: list of recommended manual checks\n"
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool, InvestmentTool.analyze_investment_tool, RiskTool.create_risk_assessment_tool, search_tool],
    async_execution=False,
)

# Investment analysis task
investment_analysis = Task(
    description=(
        "Analyze extracted financial data and compute ratios (profit margin, debt-to-equity, return on assets). "
        "Provide an educational summary of financial strengths and weaknesses. "
        "Do not give personalized investment advice."
    ),
    expected_output=(
        "Return a structured summary with:\n"
        "- extracted_values: dict\n"
        "- ratios: dict\n"
        "- analysis: short bullet list of strengths & weaknesses"
    ),
    agent=financial_analyst,  # could also use investment_advisor agent
    tools=[InvestmentTool.analyze_investment_tool],
    async_execution=False,
)

# Risk assessment task
risk_assessment = Task(
    description=(
        "Assess the financial risk based on ratios and extracted values. "
        "Highlight risk factors such as high debt, low profitability, or negative income."
    ),
    expected_output=(
        "Return a risk report with fields: {risk_level: LOW/MEDIUM/HIGH, reasons: list of strings}"
    ),
    agent=financial_analyst,  # could also use risk_assessor agent
    tools=[RiskTool.create_risk_assessment_tool],
    async_execution=False,
)

# A verification task that uses the verifier agent
verification = Task(
    description=(
        "Verify whether the uploaded file is likely a financial document such as a balance sheet,"
        " income statement or cash flow statement. Return boolean and short explanation."
    ),
    expected_output="Return a dict-like string: {'is_financial_document': bool, 'doc_type': '...' , 'explanation': '...'}",
    agent=verifier,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)
