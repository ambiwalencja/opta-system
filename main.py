# gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000
# gunicorn -c gunicorn_config.py main:app
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi_pagination import add_pagination
from dotenv import load_dotenv
import os, uuid

from db import db_connect
# from db_models import user_data, client_data, config
from routers import (
    user_endpoints, pacjent_endpoints, grupa_endpoints, wizyta_endpoints,
    config_endpoints, frontend_specific_endpoints, spot_grup_endpoints,
    report_endpoints
)
from old_db import old_db_endpoints
from old_db.old_db_connect import initialize_old_db
from logging_setup import setup_logger, request_id_var

if os.name == "nt":
    load_dotenv()

app = FastAPI(
    title="OPTA system",
    description="System dokumentacji i ewaluacji OPTA",
    version="0.1",
)

# LOGGER
logger = setup_logger()

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 1. Generate a unique ID
    rid = str(uuid.uuid4())
    
    # 2. Set it in our ContextVar so the Filter can find it
    token = request_id_var.set(rid)
    
    try:
        # 3. Process the request
        response = await call_next(request)
        
        # 4. Optional: Send the ID back to the user in a header (great for support!)
        response.headers["X-Request-ID"] = rid
        return response
    finally:
        # 5. Clean up the ContextVar after the request is finished
        request_id_var.reset(token)

# PAGINATION
add_pagination(app)

origins = [
    "http://localhost:3000",
    "*",  # Allow all origins for development purposes
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_endpoints.router)
app.include_router(pacjent_endpoints.router)
app.include_router(grupa_endpoints.router)
app.include_router(wizyta_endpoints.router)
app.include_router(config_endpoints.router)
app.include_router(frontend_specific_endpoints.router)
app.include_router(spot_grup_endpoints.router)
app.include_router(report_endpoints.router)

old_db_enabled = os.getenv("OLD_DB_MODE", "false").lower() == "true"
if old_db_enabled:
    initialize_old_db()
    app.include_router(old_db_endpoints.router)



@app.get("/", response_class=HTMLResponse)
def root():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>OPTA System</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f5f5f5;
                }
                .container {
                    text-align: center;
                }
                h1 {
                    color: #333;
                    margin-bottom: 30px;
                }
                .docs-button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 15px 32px;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    border: none;
                    transition: background-color 0.3s;
                }
                .docs-button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>OPTA System</h1>
                <p>System dokumentacji i ewaluacji OPTA</p>
                <a href="/docs" class="docs-button">Dokumentacja API</a>
            </div>
        </body>
    </html>
    """
    return html_content

# create schemas and tables when starting program
db_connect.create_schema('client_data')
db_connect.create_schema('user_data')
db_connect.create_schema('config')

db_connect.Base.metadata.create_all(db_connect.engine)

logger.info("OPTA System started successfully.")