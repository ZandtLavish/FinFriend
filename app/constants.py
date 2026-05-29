from pathlib import Path

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"

KNOWN_SERIES = {
    "FEDFUNDS":       "Fed funds rate",
    "SOFR":           "Secured overnight financing rate",
    "CPIAUCSL":       "CPI inflation (headline)",
    "CPILFESL":       "Core CPI (ex food & energy)",
    "PCEPI":          "PCE inflation",
    "PCEPILFE":       "Core PCE (Fed preferred)",
    "UNRATE":         "Unemployment rate",
    "PAYEMS":         "Nonfarm payrolls",
    "ICSA":           "Initial jobless claims",
    "GDP":            "Nominal GDP",
    "GDPC1":          "Real GDP",
    "A191RL1Q225SBEA":"Real GDP growth rate",
    "DGS10":          "10yr treasury yield",
    "DGS2":           "2yr treasury yield",
    "T10Y2Y":         "10yr-2yr yield curve spread",
    "T5YIE":          "5yr breakeven inflation rate",
    "T10YIE":         "10yr breakeven inflation rate",
    "BAMLC0A0CM":     "Investment grade credit spread",
    "BAMLH0A0HYM2":   "High yield credit spread",
}

EDGAR_HEADERS = {"user-agent": f"{settings.SEC_APP_NAME} {settings.SEC_EMAIL}"}