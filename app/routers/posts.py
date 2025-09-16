from datetime import datetime, timezone
import random
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.session import get_db
from app.deps import get_current_user, require_admin
from app.models.post import Post, PostStatus
from app.models.user import User, UserRole
from app.schemas.posts import PostCreate, PostOut, PostUpdate

router = APIRouter()


@router.post("/", response_model=PostOut)
def create_post(payload: PostCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    scheduled_at = None
    scheduled_second = None
    if payload.scheduled_date is not None:
        try:
            dt = datetime.strptime(payload.scheduled_date + " " + str(payload.scheduled_hour or 0) + ":" + str(payload.scheduled_minute or 0), "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date/hour/minute")
        dt = dt.replace(second=0, microsecond=0, tzinfo=timezone.utc)
        if dt < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Cannot schedule in the past")
        scheduled_at = dt
        scheduled_second = random.randint(0, 59)
        status_value = PostStatus.scheduled
    else:
        status_value = PostStatus.draft

    if payload.status is not None:
        try:
            status_value = PostStatus(payload.status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    post = Post(owner_id=user.id, content=payload.content, status=status_value, scheduled_at=scheduled_at, scheduled_second=scheduled_second)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/", response_model=List[PostOut])
def list_posts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    owner_id: Optional[int] = None,
    time_from: Optional[datetime] = Query(default=None),
    time_to: Optional[datetime] = Query(default=None),
):
    q = db.query(Post)
    if user.role != UserRole.admin:
        q = q.filter(Post.owner_id == user.id)
    elif owner_id is not None:
        q = q.filter(Post.owner_id == owner_id)

    if time_from is not None:
        q = q.filter(Post.created_at >= time_from)
    if time_to is not None:
        q = q.filter(Post.created_at <= time_to)

    return q.order_by(Post.created_at.desc()).all()


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if user.role != UserRole.admin and post.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return post


@router.put("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if user.role != UserRole.admin and post.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    post.content = payload.content or post.content
    if payload.status:
        try:
            post.status = PostStatus(payload.status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if user.role != UserRole.admin and post.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(post)
    db.commit()
    return
