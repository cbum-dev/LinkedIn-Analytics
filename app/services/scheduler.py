from datetime import datetime, timezone
import random
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.post import Post, PostStatus

_scheduler: BackgroundScheduler | None = None


def _simulate_linkedin_publish(post: Post) -> None:
    _ = post.id


def _tick_publish_due() -> None:
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        candidates = (
            db.query(Post)
            .filter(
                Post.status == PostStatus.scheduled,
                Post.scheduled_at <= now.replace(second=59, microsecond=999999),
            )
            .all()
        )
        for post in candidates:
            scheduled_second = post.scheduled_second or 0
            if now >= post.scheduled_at.replace(second=scheduled_second, microsecond=0): 
                _simulate_linkedin_publish(post)
                post.status = PostStatus.published
                post.published_at = now
        if candidates:
            db.commit()
    finally:
        db.close()


def scheduler_startup() -> None:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone=str(timezone.utc))
        _scheduler.add_job(_tick_publish_due, "interval", seconds=1, id="publish_due")
        _scheduler.start()


def scheduler_shutdown() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
