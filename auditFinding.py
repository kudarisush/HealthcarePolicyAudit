from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    file_name: str
    page: int

class AuditFinding(BaseModel):
    status: str = Field(description="One of: Met, Unmet, or Partial")
    confidence: int = Field(description="Score from 0 to 100 based on evidence")
    evidence: str = Field(description="The direct quote or summary from the document")
    reason: str = Field(description="Why this specific confidence score was given")
    citations: list[SourceCitation] = Field(description="List of all files and pages where evidence was found")
