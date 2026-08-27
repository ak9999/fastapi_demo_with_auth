from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.adapters.http.api import auth, person
from app.api import health, root
from app.core.config import settings

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

app.include_router(root.router)
app.include_router(health.router)
app.include_router(person.router)
app.include_router(auth.router)
