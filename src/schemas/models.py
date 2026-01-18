from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class ESGClaim(BaseModel):
    """Individual ESG claim extracted from company website."""

    category: str = Field(
        ...,
        description="ESG category (e.g., 'Carbon Emissions', 'Water Usage')"
    )
    statement: str = Field(
        ...,
        description="The specific claim text from the website"
    )
    target_year: Optional[int] = Field(
        None,
        description="Target year for the claim if specified",
        ge=2000,
        le=2100
    )
    metric: Optional[str] = Field(
        None,
        description="Quantifiable metric if present (e.g., '50% reduction')"
    )


class GreenwashReport(BaseModel):
    """Complete greenwashing analysis report."""

    company_name: str = Field(..., description="Name of the analyzed company")
    company_url: str = Field(..., description="URL that was analyzed")
    claims: List[ESGClaim] = Field(default_factory=list)
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Greenwashing risk: 0 (Trustworthy) to 100 (High Risk)"
    )
    conflicting_evidence: List[str] = Field(
        default_factory=list,
        description="List of evidence or red flags contradicting claims"
    )
    analysis_summary: Optional[str] = Field(
        None,
        description="Brief summary of the analysis"
    )
    timestamp: str = Field(..., description="ISO timestamp of the analysis")

    @field_validator('risk_score')
    @classmethod
    def validate_risk_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Risk score must be between 0 and 100')
        return v
