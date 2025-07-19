import json
import os
from datetime import datetime
from typing import Optional, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langgraph.graph import StateGraph, END
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

# FastAPI app
app = FastAPI(title="LangGraph ERP Tasks API")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Request/Response models
class TaskRequest(BaseModel):
    target_date: Optional[str] = None
    query: Optional[str] = "Summarize my tasks"


class TaskResponse(BaseModel):
    summary: str
    raw_tasks: list


# State for LangGraph - use TypedDict instead of Pydantic
from typing import TypedDict, List


class GraphState(TypedDict):
    messages: List[Dict[str, str]]
    target_date: Optional[str]
    tasks: List[str]
    summary: str


# Mock ERP function (replace with your actual implementation)
def get_erp_tasks(target_date: Optional[str] = None) -> list:
    """
    Your ERP tasks function
    Args:
        target_date: Optional date string (YYYY-MM-DD format)
    Returns:
        List of tasks
    """
    # Mock data - replace with your actual ERP call
    mock_tasks = [
        "Completed the PDF summarizer test task",
        "Fixed bugs in DeskMate socket implementation",
        "Worked on Perky Pet AI document extraction",
        "Prepared for ML interview",
        "Built MCP server for team seminar",
        "Enhanced chatbot prompts",
        "Migrated database to Linux server",
        "Set up WhatsApp integration",
        "Did R&D on AI integrations",
        "Refined Perky Pet data extraction prompts"
    ]

    if target_date:
        # Filter tasks by date logic here
        return mock_tasks[:5]  # Return fewer tasks for specific date
    else:
        # Return last 10 days tasks
        return mock_tasks


# Tool definitions for LangGraph
def get_tasks_with_date(target_date: str) -> str:
    """Get ERP tasks for a specific date"""
    tasks = get_erp_tasks(target_date)
    return json.dumps({"tasks": tasks, "date": target_date})


def get_recent_tasks() -> str:
    """Get recent ERP tasks (last 10 days)"""
    tasks = get_erp_tasks()
    return json.dumps({"tasks": tasks, "period": "last_10_days"})


# LangGraph nodes
def call_erp_tool(state: GraphState) -> GraphState:
    """Decide which tool to call and execute it"""

    if state.get("target_date"):
        # Call tool with date
        result = get_tasks_with_date(state["target_date"])
        tool_used = "get_tasks_with_date"
    else:
        # Call tool without date
        result = get_recent_tasks()
        tool_used = "get_recent_tasks"

    # Parse result
    task_data = json.loads(result)
    state["tasks"] = task_data["tasks"]

    # Add tool call to messages
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append({
        "role": "assistant",
        "content": f"Called {tool_used}, found {len(state['tasks'])} tasks"
    })

    return state


def summarize_tasks(state: GraphState) -> GraphState:
    """Use LLM to summarize the tasks"""

    tasks = state.get("tasks", [])
    tasks_text = "\n".join([f"- {task}" for task in tasks])

    prompt = f"""
    Please provide a concise summary of these work tasks:

    {tasks_text}

    Focus on:
    - Key accomplishments
    - Main project areas
    - Overall productivity patterns

    Keep the summary brief and professional.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )

        state["summary"] = response.choices[0].message.content
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "role": "assistant",
            "content": f"Generated summary of {len(tasks)} tasks"
        })

    except Exception as e:
        state["summary"] = f"Error generating summary: {str(e)}"

    return state


# Create LangGraph workflow
def create_workflow():
    """Create the LangGraph workflow"""

    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("get_tasks", call_erp_tool)
    workflow.add_node("summarize", summarize_tasks)

    # Define the flow
    workflow.set_entry_point("get_tasks")
    workflow.add_edge("get_tasks", "summarize")
    workflow.add_edge("summarize", END)

    return workflow.compile()


# Initialize the graph
graph = create_workflow()


# FastAPI endpoints
@app.post("/analyze-tasks", response_model=TaskResponse)
async def analyze_tasks(request: TaskRequest):
    """
    Analyze ERP tasks using LangGraph workflow
    """
    try:
        # Initialize state
        initial_state: GraphState = {
            "target_date": request.target_date,
            "messages": [{"role": "user", "content": request.query}],
            "tasks": [],
            "summary": ""
        }

        # Run the graph
        result = graph.invoke(initial_state)

        return TaskResponse(
            summary=result.get("summary", ""),
            raw_tasks=result.get("tasks", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/tasks")
async def get_tasks_endpoint(target_date: Optional[str] = None):
    """
    Direct endpoint to get tasks without summarization
    """
    try:
        tasks = get_erp_tasks(target_date)
        return {"tasks": tasks, "count": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8900)