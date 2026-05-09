import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .api.dashboard_api import router as dashboard_router
from .api.activity_api import router as activity_router
from .api.report_api import router as report_router
from .api.settings_api import router as settings_router
from .api.project_api import router as project_router
from .api.websocket_api import router as ws_router


def create_app(lifespan=None) -> FastAPI:
    app = FastAPI(title="Work Reportor", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
    app.include_router(activity_router, prefix="/api/activity", tags=["activity"])
    app.include_router(report_router, prefix="/api/reports", tags=["reports"])
    app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
    app.include_router(project_router, prefix="/api/projects", tags=["projects"])
    app.include_router(ws_router, tags=["websocket"])

    # Serve frontend static files
    frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    if os.path.isdir(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

    return app
