from fastapi import APIRouter

from app.pydantics.base_schema import ChatData
from app.services.workflow import run_erp_workflow

nudge_router = APIRouter(tags=["ERP Workflow"])


@nudge_router.post("/chat")
async def generate_answer(
    chat_data: ChatData
):
    try:
        query = chat_data.query.strip()
        llm_response = run_erp_workflow(query)
        return {"llm_response": llm_response}
    except Exception as e:
        print(f"Error: {e}")
        raise e
