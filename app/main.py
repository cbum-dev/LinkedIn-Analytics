from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, posts, analytics
from app.services.scheduler import scheduler_startup, scheduler_shutdown

app = FastAPI(title="LinkedIn Analytics Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

@app.get("/", tags=["meta"])
def root() -> dict:
    routes_info: list[dict[str, str | list[str]]] = []
    for route in app.routes:
        try:
            path = getattr(route, "path", None)
            methods = sorted(getattr(route, "methods", []) or [])
            name = getattr(route, "name", "")
            if path:
                routes_info.append({"path": path, "methods": list(methods), "name": name})
        except Exception:
            continue
    return {
        "app": app.title,
        "version": app.version,
        "routes": routes_info,
    }

@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}

@app.on_event("startup")
def on_startup() -> None:
    scheduler_startup()

@app.on_event("shutdown")
def on_shutdown() -> None:
    scheduler_shutdown()
