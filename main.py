from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, ORJSONResponse
from fastapi.templating import Jinja2Templates
import config
import Oauth
from starlette.middleware.sessions import SessionMiddleware

discord_o = Oauth.Oauth()

templates = Jinja2Templates(directory = "templates")

app = FastAPI(include_in_schema = False, docs_url = None, redoc_url = None)
app.add_middleware(SessionMiddleware, secret_key = config.session_key)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "username": request.session.get("username"), "disc": request.session.get("disc")})

@app.get("/login")
def login(request: Request):
    oauth = discord_o.get_discord_oauth('identify')
    request.session["state"] = oauth["state"]
    return RedirectResponse(oauth["url"])

@app.get("/login/confirm")
async def confirm_login(request: Request, code: str, state: str):
    if "userid" in request.session.keys():
        return RedirectResponse("/")
    else:
        # Validate the state first
        if request.session.get("state") != state:
            return ORJSONResponse({"detail": "Invalid State"}, status_code = 400)
    try:
        del request.session["state"]
    except:
        pass
    access_token = await discord_o.get_access_token(code, ['identify',])
    userjson = await discord_o.get_user_json(access_token["access_token"])
    if userjson["id"]:
        pass
    else:
        return RedirectResponse("/")
    request.session["access_token"] = access_token
    request.session["userid"] = userjson["id"]
    print(userjson)
    request.session["disc"] = userjson["dash"]
    request.session["username"] = str(userjson["name"])
    if userjson.get("avatar"):
        request.session["avatar"] = "https://cdn.discordapp.com/avatars/" + \
        userjson["id"] + "/" + userjson["avatar"]
    else:
        # No avatar in user
        request.session["avatar"] = "https://s3.us-east-1.amazonaws.com/files.tvisha.aws/posts/crm/panel/attachments/1580985653/discord-logo.jpg"
    return RedirectResponse("/")

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")
