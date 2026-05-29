import re
from pydantic import BaseModel, Field, field_validator
import logging
logger = logging.getLogger(__name__)

class FREDSearchInput(BaseModel):
    query: str = Field(
        description=(
            "A natural language description of the economic indicator to find."
            "e.g. 'headline inflation', '10 year treasury yield', 'unemployment rate'"
            "Never guess or construct an economic indicator."
        )
    )
    limit: int = Field(default=3, description="Number of results to return (max 10)")
    

class MacroIndicatorInput(BaseModel):
    series_id: str = Field(
        description=(
            "A valid FRED series ID string e.g. 'FEDFUNDS', 'CPIAUCSL', 'DGS10'. "
            "If you do not know the exact series ID, call search_fred_series first "
            "to find it. Never guess or construct a series ID."
        )
    )
    
    # Structurally catch hallucinated FRED series IDs
    @field_validator("series_id")
    @classmethod
    def validate_series_id(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r'^[A-Z0-9]{1,20}$', v):
            logger.error(f"Hallucinated FRED series_id detected: `{v}`")
            
            raise ValueError(
                f"'{v}' is not a valid FRED series ID format. "
                "A valid ID contains only letters and numbers, up to 20 characters "
                "e.g. 'FEDFUNDS', 'DGS10', 'CPIAUCSL'. "
                "Call search_fred_series to find the correct ID."
            )
        return v