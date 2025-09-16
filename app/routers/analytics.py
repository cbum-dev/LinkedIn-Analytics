from collections import defaultdict
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User, UserRole
from app.models.post import Post, Reaction, ReactionType
from app.schemas.analytics import PostMetric, TopPostsResponse

router = APIRouter()


@router.post("/{post_id}/react")
def react(post_id: int, type: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if user.role != UserRole.admin and post.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        rtype = ReactionType(type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reaction type")
    reaction = Reaction(post_id=post.id, type=rtype)
    db.add(reaction)
    db.commit()
    return {"status": "ok"}


def _metrics_for_posts(db: Session, post_ids: list[int]) -> dict[int, PostMetric]:
    counts = (
        db.query(Reaction.post_id, Reaction.type, func.count(Reaction.id))
        .filter(Reaction.post_id.in_(post_ids))
        .group_by(Reaction.post_id, Reaction.type)
        .all()
    )
    by_post: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for pid, rtype, cnt in counts:
        by_post[pid][rtype.value] = cnt
    metrics: dict[int, PostMetric] = {}
    for pid in post_ids:
        like = by_post[pid].get("like", 0)
        praise = by_post[pid].get("praise", 0)
        empathy = by_post[pid].get("empathy", 0)
        interest = by_post[pid].get("interest", 0)
        appreciation = by_post[pid].get("appreciation", 0)
        total_reactions = like + praise + empathy + interest + appreciation
        impressions = total_reactions * 10
        comments = total_reactions // 3
        shares = total_reactions // 5
        metrics[pid] = PostMetric(
            post_id=pid,
            total_reactions=total_reactions,
            like=like,
            praise=praise,
            empathy=empathy,
            interest=interest,
            appreciation=appreciation,
            impressions=impressions,
            comments=comments,
            shares=shares,
        )
    return metrics


@router.get("/post/{post_id}", response_model=PostMetric)
def post_metrics(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if user.role != UserRole.admin and post.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    metrics = _metrics_for_posts(db, [post_id])
    return metrics.get(post_id, PostMetric(post_id=post_id, total_reactions=0, like=0, praise=0, empathy=0, interest=0, appreciation=0, impressions=0, comments=0, shares=0))


@router.get("/top", response_model=TopPostsResponse)
def top_posts(limit: int = 5, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Post.id)
    if user.role != UserRole.admin:
        q = q.filter(Post.owner_id == user.id)
    post_ids = [pid for (pid,) in q.all()]
    metrics = _metrics_for_posts(db, post_ids)
    top = sorted(metrics.values(), key=lambda m: (m.total_reactions, m.impressions, m.shares, m.comments), reverse=True)[:limit]
    return {"items": top}
