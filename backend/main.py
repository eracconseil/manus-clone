from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import router as agent_router
from .api.billing import router as billing_router
from .api.history import router as history_router
from .api.share import router as share_router
from .api.memory import router as memory_router

app = FastAPI(title="Orion API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router, prefix="/api")
app.include_router(billing_router)
app.include_router(history_router)
app.include_router(share_router)
app.include_router(memory_router)
