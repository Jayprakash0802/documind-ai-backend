from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.processing import router as processing_router
from routes.search import router as search_router


# Initialize FastAPI App with lifespan
app = FastAPI(title="Document Processing API", version="1.0")

# Enable CORS (Adjust for your frontend domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(processing_router, prefix="/api")
app.include_router(search_router, prefix="/api")

@app.get("/")
def root():
    """Root route for health check"""
    return {"message": "API is running"}

# Run with: uvicorn main:app --reload
