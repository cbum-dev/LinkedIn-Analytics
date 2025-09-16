from pydantic import BaseModel
from typing import List


class PostMetric(BaseModel):
    post_id: int
    total_reactions: int
    like: int
    praise: int
    empathy: int
    interest: int
    appreciation: int
    impressions: int
    comments: int
    shares: int


class TopPostsResponse(BaseModel):
    items: List[PostMetric]
