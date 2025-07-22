from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.pydantics.base_schema import ChatData
from app.services.workflow import run_erp_workflow, get_visual_graph

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


@nudge_router.get("/visualize")
async def stream_visual_graph():
    """
    Streams the LangGraph workflow image to the frontend.
    """
    try:
        image_path = get_visual_graph()
        return FileResponse(
            path=str(image_path),
            media_type="image/png",
            filename="workflow_graph.png"
        )

    except Exception as e:
            print(f"Error: {e}")
            raise e



