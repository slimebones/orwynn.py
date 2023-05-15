import httpx
from fastapi import Response as FastAPIResponse
from fastapi.responses import FileResponse as FastAPI_FileResponse
from fastapi.responses import HTMLResponse as FastAPI_HTMLResponse
from fastapi.responses import JSONResponse as FastAPI_JSONResponse

HttpResponse = FastAPIResponse
JsonHttpResponse = FastAPI_JSONResponse
HtmlHttpResponse = FastAPI_HTMLResponse
TestHttpResponse = httpx.Response
FileHttpResponse = FastAPI_FileResponse
