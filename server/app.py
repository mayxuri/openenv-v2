import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app  # re-export the FastAPI app

__all__ = ["app"]


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()
