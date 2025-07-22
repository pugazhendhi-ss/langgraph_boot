

PROMPT = """Analyze the user query and extract information. Return a JSON with:
                    - email: extracted email address (empty string if not found)
                    - password: extracted password (empty string if not found)  
                    - tasks: extracted task list (empty list if not found)
                    - intent: one of 'get_productivity', 'help', 'direct_tasks', 'email_only', 'email_password'

                    Examples:
                    - "analyze my productivity, email is joe@gmail.com" -> {"email": "joe@gmail.com", "password": "", "tasks": [], "intent": "email_only"}
                    - "email: x@y.com password: 123" -> {"email": "x@y.com", "password": "123", "tasks": [], "intent": "email_password"}
                    - "analyze these tasks: [task1, task2]" -> {"email": "", "password": "", "tasks": ["task1", "task2"], "intent": "direct_tasks"}
                    - "what can you do?" -> {"email": "", "password": "", "tasks": [], "intent": "help"}
                    """

GENERIC_RESPONSE = ("I can fetch and analyze your ERP task data. Provide your email or email and password "
                    "to kick of the work flow. \n"
                    "You can see my workflow graph here: [visual graph](http://127.0.0.1:8900/visualize)")


def get_analyzer_prompt(query: str):
    analyzer_prompt = f"""Analyze the following tasks and provide a productivity summary. 
                    Consider the user's original query: {query}

                    Provide insights on:
                    - Task completion patterns
                    - Technologies knowledge possessed
                    - Productivity levels
                    - Work life balance
                    - Overall performance assessment
                    - Rating out of 10
                    """
    return analyzer_prompt
