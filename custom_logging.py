from loguru import logger as crypto_logger
import os
 
LOG_DIR = 'logs'
 
LOG_FORMAT: str = (
    "{time: YYYY-MM-DD HH:mm:ss.SSS}" + " | {level} | {file.name}:{function} | {message}"
)
 
crypto_logger.configure(
    handlers=[
        {
            "sink": os.path.join(LOG_DIR, f"app.log"),
            "level": "TRACE",
            "colorize": False,
            "format": LOG_FORMAT,
            "rotation": "10MB",
            "compression": "zip",
        },
    ]
)