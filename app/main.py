import logging
import sys
from datetime import datetime

# Configure logging
log_filename = f"app_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Print to console
        logging.FileHandler(log_filename)   # Save to file
    ]
)

# Additional application-level code can be placed here if needed.
