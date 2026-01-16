from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi_pagination import add_pagination

from dotenv import load_dotenv
import os
from db import db_connect
from db_models import user_data, client_data, config
from routers import (
    user_endpoints, pacjent_endpoints, grupa_endpoints, wizyta_endpoints,
    config_endpoints, frontend_specific_endpoints, spot_grup_endpoints,
    report_endpoints
)
from old_db import old_db_endpoints
from old_db.old_db_connect import initialize_old_db


if os.name == "nt":
    load_dotenv()

app = FastAPI(
    title="OPTA system",
    description="System dokumentacji i ewaluacji OPTA",
    version="0.1",
)

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

db_connect.create_schema('client_data')
db_connect.create_schema('user_data')
db_connect.create_schema('config')

# create tables when starting program
db_connect.Base.metadata.create_all(db_connect.engine)
