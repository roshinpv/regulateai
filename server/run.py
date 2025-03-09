import uvicorn
import logging
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    logger.info("Starting Regulatory Compliance API server")
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )