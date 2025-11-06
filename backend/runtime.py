from __future__ import annotations

from config import AppConfig, setup_logging
from backend.api import create_app
from backend.controller.pipeline_controller import PipelineController

setup_logging()

CONFIG = AppConfig()
CONTROLLER = PipelineController(config=CONFIG, configure_logging=False)
API_APP = create_app(CONTROLLER)
