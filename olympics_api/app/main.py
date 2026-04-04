"""Main FastAPI application — entry point for the Olympics API."""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database.connections import init_db
from app.routes import users, tokens, athletes, countries, sport


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup/shutdown logic."""
    # TODO: Connect to DB and load CSV data on startup
    init_db()
    yield
    # TODO: Close DB connection on shutdown


app = FastAPI(
    title="Olympics API",
    version="1.0.0",
    lifespan=lifespan,
)

# All routes are versioned under /v1
app.include_router(users.router, prefix="/v1")
app.include_router(tokens.router, prefix="/v1")
app.include_router(athletes.router, prefix="/v1")
app.include_router(countries.router, prefix="/v1")
app.include_router(sport.router, prefix="/v1")


@app.get("/")
def root():
    """Health check / welcome."""
    return {"message": "Olympics API is running", "docs": "/docs"}
