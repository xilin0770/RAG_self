from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.api import importer, courses, search, questions, qa, conversations

WEB_DIR = Path(__file__).resolve().parent / "web"
WEB_STATIC_DIR = WEB_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="教育知识库 RAG 系统",
    description="面向教育培训场景的智能知识库系统，支持内容导入、课程检索、文档检索、题库检索和知识问答",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(importer.router)
app.include_router(courses.router)
app.include_router(search.router)
app.include_router(questions.router)
app.include_router(qa.router)
app.include_router(conversations.router)
app.mount("/web/static", StaticFiles(directory=str(WEB_STATIC_DIR)), name="web-static")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


@app.get("/")
def root():
    return {"message": "教育知识库 RAG 系统 API", "docs": "/docs"}


@app.get("/web", include_in_schema=False)
@app.get("/web/", include_in_schema=False)
def web_console():
    return FileResponse(str(WEB_DIR / "index.html"))
