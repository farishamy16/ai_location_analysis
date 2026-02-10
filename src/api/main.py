"""FastAPI application initialization for Complaint Location Analyzer API."""

import uvicorn
from fastapi import FastAPI, status

from src.api.complaints import router as complaints_router
from src.api.health import router as health_router


# Initialize FastAPI app
app = FastAPI(
    title="Complaint Location Analyzer API",
    description="AI-powered complaint location analyzer with routing and notification capabilities",
    version="1.0.0"
)


# Register exception handler
async def generic_exception_handler(request, exc: Exception):
    """Handle generic exceptions."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(health_router.router, tags=["Health"])
app.include_router(complaints_router.router, prefix="/api", tags=["Complaints"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
