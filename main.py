import asyncio
import logging
import os
import webbrowser
import threading
from contextlib import asynccontextmanager
import yaml
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("work-reportor")


def main():
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    server_config = config.get("server", {})
    host = server_config.get("host", "127.0.0.1")
    port = server_config.get("port", 8765)
    db_path = config.get("database", {}).get("path", "data/work-reportor.db")

    # Initialize database
    from backend.storage.database import init_db
    init_db(db_path)
    logger.info("Database initialized")

    # Setup scheduler (collectors)
    from backend.core.scheduler import Scheduler
    from backend.core.event import set_event_loop

    scheduler = Scheduler()

    @asynccontextmanager
    async def lifespan(app):
        # Startup
        loop = asyncio.get_event_loop()
        set_event_loop(loop)
        scheduler.start()
        logger.info(f"Work Reportor running at http://{host}:{port}")

        def open_browser():
            import time
            time.sleep(1.5)
            webbrowser.open(f"http://{host}:{port}")

        threading.Thread(target=open_browser, daemon=True).start()

        yield

        # Shutdown
        scheduler.stop()
        logger.info("Work Reportor stopped")

    # Create FastAPI app with lifespan
    from backend.app import create_app
    app = create_app(lifespan=lifespan)

    # Run server
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
