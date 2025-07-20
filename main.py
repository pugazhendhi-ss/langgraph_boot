import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.routers.nudge import nudge_router

app = FastAPI(title="LangGraph ERP Workflow")

app.include_router(nudge_router)

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def serve_frontend(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8900)
