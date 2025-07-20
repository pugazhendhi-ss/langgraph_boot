from pydantic import BaseModel, Field
from typing import Optional


class ChatData(BaseModel):
    session_id: Optional[str] = Field(default=None, json_schema_extra={'examples': ['dyuiu3henfiu3rieouf']})
    query: str = Field(..., json_schema_extra={'examples': ['Analyze the tasks']})


