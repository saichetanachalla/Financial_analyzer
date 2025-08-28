"""
Fixes:
- Implemented PDF reading using PyPDF2 (robust and widely available).
- Implemented a simple search_tool fallback (no external API required).
- Implemented basic investment analysis and risk assessment functions that extract numeric values using regex and compute simple ratios.
- Made read_data_tool a @staticmethod for easy use as a callable.
"""
import re
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

def _extract_numbers_from_text(text):
    num_pattern = r'[-]?\(?\$?\s?[\d\.,]+(?:\)?)*'
    candidates = re.findall(num_pattern, text)
    mapping = {}
    lines = text.splitlines()
    for line in lines:
        lower = line.lower()
        if any(k in lower for k in ["total assets", "assets"]):
            nums = re.findall(r'[-]?\d[\d,\.]+', line.replace(",", ""))
            if nums:
                try:
                    mapping["total_assets"] = float(nums[-1])
                except:
                    pass
        if any(k in lower for k in ["total liabilities", "liabilities"]):
            nums = re.findall(r'[-]?\d[\d,\.]+', line.replace(",", ""))
            if nums:
                try:
                    mapping["total_liabilities"] = float(nums[-1])
                except:
                    pass
        if any(k in lower for k in ["revenue", "total revenue", "sales"]):
            nums = re.findall(r'[-]?\d[\d,\.]+', line.replace(",", ""))
            if nums:
                try:
                    mapping["revenue"] = float(nums[-1])
                except:
                    pass
        if any(k in lower for k in ["net income", "profit", "net profit"]):
            nums = re.findall(r'[-]?\d[\d,\.]+', line.replace(",", ""))
            if nums:
                try:
                    mapping["net_income"] = float(nums[-1])
                except:
                    pass
        if any(k in lower for k in ["equity", "shareholders' equity", "total equity"]):
            nums = re.findall(r'[-]?\d[\d,\.]+', line.replace(",", ""))
            if nums:
                try:
                    mapping["equity"] = float(nums[-1])
                except:
                    pass
    return mapping

class FinancialDocumentTool:
    @staticmethod
    async def read_data_tool(path: str = "data/sample.pdf"):
        """
        Read PDF text and return as a single string.
        Uses PyPDF2 if available, otherwise raises an informative error.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")
        if PdfReader is None:
            raise RuntimeError("PyPDF2 is required for PDF reading. Please install with 'pip install PyPDF2'")

        reader = PdfReader(str(p))
        full_text = []
        for page in reader.pages:
            try:
                text = page.extract_text()
            except Exception:
                text = ""
            if text:
                # Normalize whitespace
                text = '\n'.join([ln.strip() for ln in text.splitlines() if ln.strip()])
                full_text.append(text)
        return "\n\n".join(full_text)

class InvestmentTool:
    @staticmethod
    async def analyze_investment_tool(financial_document_data: str):
        if not financial_document_data:
            return "No document text provided."

        extracted = _extract_numbers_from_text(financial_document_data)
        results = {}
        revenue = extracted.get("revenue")
        net_income = extracted.get("net_income")
        total_liabilities = extracted.get("total_liabilities")
        equity = extracted.get("equity")
        total_assets = extracted.get("total_assets")

        if revenue and net_income:
            try:
                results["profit_margin"] = net_income / revenue
            except Exception:
                results["profit_margin"] = None

        if total_liabilities and equity:
            try:
                results["debt_to_equity"] = total_liabilities / equity if equity != 0 else None
            except Exception:
                results["debt_to_equity"] = None

        if total_assets and net_income:
            try:
                results["return_on_assets"] = net_income / total_assets
            except Exception:
                results["return_on_assets"] = None

     
        summary_lines = []
        summary_lines.append("Extracted financial values (heuristic):")
        for k, v in extracted.items():
            summary_lines.append(f"- {k}: {v}")
        summary_lines.append("")
        summary_lines.append("Computed ratios (when possible):")
        for k, v in results.items():
            if v is None:
                summary_lines.append(f"- {k}: n/a")
            else:
                summary_lines.append(f"- {k}: {v:.4f}")
        summary_lines.append("")
        summary_lines.append("Notes: These results are heuristic. Manual verification is recommended.")
        return "\n".join(summary_lines)

class RiskTool:
    @staticmethod
    async def create_risk_assessment_tool(financial_document_data: str):
        """
        Produce a simple risk level based on heuristics:
        - high debt_to_equity -> higher risk
        - negative profit margin -> higher risk
        """
        extracted = _extract_numbers_from_text(financial_document_data)
        total_liabilities = extracted.get("total_liabilities")
        equity = extracted.get("equity")
        revenue = extracted.get("revenue")
        net_income = extracted.get("net_income")

        risk_score = 0.0
        reasons = []

        if total_liabilities and equity and equity != 0:
            dte = total_liabilities / equity
            risk_score += min(dte / 2.0, 2.0)  # scaled
            reasons.append(f"Debt-to-equity ~ {dte:.2f}")
        if revenue and net_income:
            if net_income < 0:
                risk_score += 1.0
                reasons.append("Negative net income")
            else:
                pm = net_income / revenue
                if pm < 0.02:
                    risk_score += 0.8
                    reasons.append(f"Very low profit margin ~ {pm:.4f}")
        if risk_score >= 2.0:
            level = "HIGH"
        elif risk_score >= 1.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        return f"Risk level: {level}\nReasons: {', '.join(reasons) if reasons else 'Not enough data to determine risk.'}"

# Simple search tool fallback (no external API)
async def search_tool(query: str, limit: int = 3):
    """
    A very small, deterministic search-tool stub that returns zero or simple canned results.
    Replace this with a SerpAPI/Serper integration for real searches.
    """
    if not query:
        return []
    
    return [
        {"title": "Company Filings (example)", "link": "https://www.example.com/filings"},
        {"title": "Financial Ratios Reference", "link": "https://www.example.com/ratios"}
    ]
