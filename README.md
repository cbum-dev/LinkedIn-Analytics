## LinkedIn Analytics Backend (FastAPI + PostgreSQL)

### Prerequisites
- Docker & Docker Compose
- Python 3.11 (optional for running locally)

### Setup (Docker)
1. Copy `.env.example` to `.env` and adjust values.
2. Build and start:
   ```bash
   docker compose up --build
   ```
3. Run migrations (in another terminal):
   ```bash
   docker compose exec api alembic upgrade head
   ```
4. Open docs: `http://localhost:8000/docs`

### Setup (Local)
1. Create and activate a venv, then:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize DB:
   ```bash
   alembic upgrade head
   ```

### Auth & Roles
- Admin can manage all posts & analytics.
- User can manage only their own posts & analytics.

### Posts
- CRUD with filters by owner and time range.
- Scheduling: provide date/hour/minute; system assigns a random second within that minute.
- Scheduler publishes due posts and marks them as `published`.

### Analytics
- Reactions: like, praise, empathy, interest, appreciation.
- Metrics: total reactions, impressions, shares, comments.
- Endpoints: per-post metrics, top N posts by engagement.

### Postman
- Import `Postman_Collection.json` and set `{{token}}` with the value from login/signup.

### Notes
- Indices added for time-based and owner/status queries.
- Error handling and validation with Pydantic and HTTP codes.
