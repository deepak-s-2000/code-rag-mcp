
from fastapi import FastAPI, Request
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware
from app.config import RAGConfig
import time
import logging
import json
from app.api.routes.api import router as api_router
from app.api.cronjobs.add_cron_api import setup_cron_jobs
from apscheduler.schedulers.background import BackgroundScheduler
def create_application() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    application = FastAPI()
    
    application.title = RAGConfig().app_name
    application.version = RAGConfig().app_version
    application.debug = RAGConfig().debug
    
    application.include_router(api_router)
    
    @application.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        logging.info(f"Request {request.url.path} took {process_time:.2f} seconds")
        response.headers["X-Process-Time"] = str(process_time)
        return response

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    scheduler = BackgroundScheduler()
    setup_cron_jobs(scheduler)
    application.add_event_handler("startup", scheduler.start)
    
    mcp = FastApiMCP(application)
    mcp.mount()
    return application


application = create_application()