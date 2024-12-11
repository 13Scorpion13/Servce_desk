from app.main import app
from app.database import engine
from app.admin import setup_admin

setup_admin(app, engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)