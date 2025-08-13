from pydantic import BaseModel, Field
from typing import Optional, List

class CanonicalEntity(BaseModel):
    entity_type: str  # bill | person | committee | event | vote | other
    jurisdiction: str # federal | provincial:<code> | city:<name>
    external_id: str
    title: Optional[str] = None
    summary: Optional[str] = None
    data: dict = Field(default_factory=dict)
    hash: Optional[str] = None