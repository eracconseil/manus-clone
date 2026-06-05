from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum


class ModelType(str, Enum):
    CLAUDE = "claude"
    KIMI = "kimi"
    QWEN = "qwen"


class TaskComplexity(str, Enum):
    SIMPLE = "simple"
    LONG_CONTEXT = "long_context"
    COMPLEX = "complex"


class ImageAttachment(BaseModel):
    data: str        # base64
    media_type: str  # image/jpeg, image/png, etc.
    name: str


class RunRequest(BaseModel):
    session_id: str
    message: str
    images: Optional[list[ImageAttachment]] = None


class SubscriptionStatus(BaseModel):
    plan: str
    tasks_limit: int
    tasks_used: int
    tasks_left: int
    extra_tasks: int
    period_end: str
    reset_in_days: int


class SSEEvent(BaseModel):
    type: str
    data: Optional[Any] = None
