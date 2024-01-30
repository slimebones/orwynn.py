import httpx
from fastapi import Response as FastAPIResponse
from fastapi.responses import FileResponse as FastAPI_FileResponse
from fastapi.responses import HTMLResponse as FastAPI_HTMLResponse
from fastapi.responses import JSONResponse as FastAPI_JSONResponse
from starlette.responses import RedirectResponse as Starlette_RedirectResponse

HttpResponse = FastAPIResponse
JsonHttpResponse = FastAPI_JSONResponse
HtmlHttpResponse = FastAPI_HTMLResponse
TestHttpResponse = httpx.Response
FileHttpResponse = FastAPI_FileResponse
RedirectHttpResponse = Starlette_RedirectResponse
