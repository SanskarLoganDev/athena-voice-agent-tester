"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(title="Athena Voice Agent Tester")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
