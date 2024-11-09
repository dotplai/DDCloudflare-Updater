import logging
from logging.handlers import RotatingFileHandler
import os

log_directory = 'logs'
log_file = os.path.join(log_directory, 'cloudflare_updater.log')

# Ensure the log directory exists
os.makedirs(log_directory, exist_ok=True)

# Create Log Levels
# logging.addLevelName(201, "Initializer")

# Create a logger object
logger = logging.getLogger("DDNCloudFlare")
logger.setLevel(logging.INFO)

# Define log format
log_format = logging.Formatter("%(asctime)s - (%(name)s - %(levelname)s): %(message)s", datefmt='%Y-%m-%d %H:%M:%S')


# RotatingFileHandler to manage log size and rotation
file_handler = RotatingFileHandler(log_file, maxBytes=(5 * 1024 * 1024), backupCount=5)  # 5 MB per file, keep 5 backups
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.INFO)

# StreamHandler for console output
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.INFO)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)