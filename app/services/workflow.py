import json
from typing import Dict, Any, TypedDict

import openai
from langgraph.graph import StateGraph, END

from app.config.settings import OPENAI_API_KEY
from app.services.tools import get_tasks, get_user_data
from app.templates.system_prompt import PROMPT, GENERIC_RESPONSE, get_analyzer_prompt

# Set your OpenAI API key
openai.api_key = OPENAI_API_KEY


# Define the state schema
class ERPWorkflow(TypedDict):
    query: str
    email: str
    password: str
    tasks: list
    response: str
    next_action: str


# OpenAI-powered query analysis
def analyze_query_with_openai(query: str) -> Dict[str, Any]:
    """Use OpenAI to analyze the query and extract information"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": PROMPT},
                   {"role": "user", "content": query}],
            response_format={"type": "json_object"},
            temperature=0)

        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"OpenAI analysis error: {e}")
        return {"email": "", "password": "", "tasks": [], "intent": "help"}


# Node functions
def supervisor_node(state: ERPWorkflow) -> ERPWorkflow:
    """Supervisor node that analyzes query and determines next action"""
    query = state["query"]
    analysis = analyze_query_with_openai(query)

    # Extract information from analysis
    email = analysis.get("email", "")
    password = analysis.get("password", "")
    tasks = analysis.get("tasks", [])
    intent = analysis.get("intent", "help")

    # Determine next action based on intent
    if intent == "help":
        return {**state,
            "response": GENERIC_RESPONSE,
            "next_action": "end"}
    elif intent == "direct_tasks":
        return {**state, "tasks": tasks, "next_action": "summarize"}
    elif intent == "email_password":
        return {**state, "email": email, "password": password, "next_action": "fetch_tasks"}
    elif intent == "email_only":
        return {**state, "email": email, "next_action": "get_password"}
    else:
        return {**state, "email": email, "next_action": "get_password" if email else "end",
            "response": "Please provide your email address to get started." if not email else ""}


def get_password_node(state: ERPWorkflow) -> ERPWorkflow:
    """Node to fetch password from database"""
    email = state["email"]
    if not email:
        return {**state, "response": "Email not found", "next_action": "end"}

    try:
        password = get_user_data(email)
        if password:
            return {**state, "password": password, "next_action": "fetch_tasks"}
        else:
            return {**state, "response": "Password not found for this email", "next_action": "end"}
    except Exception as e:
        return {**state, "response": f"Error fetching password: {str(e)}", "next_action": "end"}


def fetch_tasks_node(state: ERPWorkflow) -> ERPWorkflow:
    """Node to fetch tasks from ERP"""
    email = state["email"]
    password = state["password"]

    if not email or not password:
        return {**state, "response": "Email or password missing", "next_action": "end"}

    try:
        tasks = get_tasks(email, password)
        return {**state, "tasks": tasks, "next_action": "summarize"}
    except Exception as e:
        return {**state, "response": f"Error fetching tasks: {str(e)}", "next_action": "end"}


def summarize_tasks_node(state: ERPWorkflow) -> ERPWorkflow:
    """Node to summarize tasks using OpenAI"""
    tasks = state["tasks"]
    query = state["query"]

    if not tasks:
        return {**state, "response": "No tasks found to summarize", "next_action": "end"}

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                "content": get_analyzer_prompt(query)},
                {"role": "user", "content": f"Tasks to analyze: {tasks}"}],
            temperature=0.3)

        summary = response.choices[0].message.content
        return {**state, "response": summary, "next_action": "end"}
    except Exception as e:
        return {**state, "response": f"Error summarizing tasks: {str(e)}", "next_action": "end"}


# Conditional edge function
def route_next_action(state: ERPWorkflow) -> str:
    """Route to next node based on next_action"""
    next_action = state.get("next_action", "end")
    if next_action == "get_password":
        return "get_password"
    elif next_action == "fetch_tasks":
        return "fetch_tasks"
    elif next_action == "summarize":
        return "summarize"
    else:
        return END


# Build the graph
def create_workflow():
    """Create and compile the LangGraph workflow"""
    workflow = StateGraph(ERPWorkflow)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("get_password", get_password_node)
    workflow.add_node("fetch_tasks", fetch_tasks_node)
    workflow.add_node("summarize", summarize_tasks_node)

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add conditional edges from supervisor
    workflow.add_conditional_edges("supervisor", route_next_action,
        {"get_password": "get_password", "fetch_tasks": "fetch_tasks", "summarize": "summarize", END: END})

    # Add conditional edges from other nodes
    workflow.add_conditional_edges("get_password", route_next_action, {"fetch_tasks": "fetch_tasks", END: END})

    workflow.add_conditional_edges("fetch_tasks", route_next_action, {"summarize": "summarize", END: END})

    workflow.add_edge("summarize", END)

    return workflow.compile()


# Main execution function
def run_erp_workflow(query: str) -> str:
    """Run the ERP workflow with a user query"""
    print(f"\nUser query ---> {query}\n")

    app = create_workflow()

    initial_state = ERPWorkflow(query=query, email="", password="", tasks=[], response="", next_action="")

    result = app.invoke(initial_state)
    llm_response = result.get("response", "No response generated")
    print(f"\nLLM response ---> {llm_response}\n")
    return llm_response
