from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import config
from starlette.middleware.sessions import SessionMiddleware

templates = Jinja2Templates(directory = "templates")

app = FastAPI(include_in_schema = False)
app.add_middleware(SessionMiddleware, secret_key = config.session_key)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
