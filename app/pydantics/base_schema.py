from pydantic import BaseModel, Field


class ChatData(BaseModel):
    session_id: str = Field(..., json_schema_extra={'examples': ['dyuiu3henfiu3rieouf']})
    query: str = Field(..., json_schema_extra={'examples': ['Analyze the tasks done by pugazhendhi kumar']})
