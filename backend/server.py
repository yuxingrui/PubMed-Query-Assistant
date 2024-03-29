import sys
sys.path.append("d:/Clinfo.AI/src")
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os
from utils.websocket_manager import WebSocketManager
from .functions import *
from config        import OPENAI_API_KEY, NCBI_API_KEY, EMAIL
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str


app = FastAPI()

app.mount("/site", StaticFiles(directory="./frontend"), name="site")
app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")

templates = Jinja2Templates(directory="./frontend")

manager = WebSocketManager()


# Dynamic directory for outputs once first research is run
@app.on_event("startup")
def startup_event():
    if not os.path.isdir("outputs"):
        os.makedirs("outputs")
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "report": None})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        print("2")
        while True:
            data = await websocket.receive_text()
            print('data:',data)
            if data.startswith("start"):
                json_data = json.loads(data[6:])
                task = json_data.get("task")
                if task:
                    report = await manager.start_streaming(task,OPENAI_API_KEY,EMAIL, websocket)
                    await websocket.send_json({"type": "report", "output": report})
                    path = await write_md_to_pdf(report)
                    await websocket.send_json({"type": "path", "output": path})
                else:
                    print("Error: not enough parameters provided.")

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
