# PR Prep Production Deployment & Operational Runbooks

## 1. Deployment & Rollback Runbook

### Deployment Procedure
1. Run automated test suite: `.venv/bin/pytest tests/ -v && .venv/bin/ruff check backend/ tests/ && .venv/bin/mypy backend/ tests/`.
2. Apply database migrations: `psql $DATABASE_URL -f backend/scripts/migrations/2026-06-tiger-init.sql`.
3. Build and tag release containers: `docker build -t prprep-backend:$RELEASE_VERSION -f backend/Dockerfile .`.
4. Deploy API containers to production cluster with rolling updates.
5. Verify health & readiness probes: `curl http://localhost:8000/health` and `curl http://localhost:8000/ready`.

### Emergency Rollback Procedure
1. Revert container image tag to previous stable commit: `docker service update --image prprep-backend:$PREVIOUS_STABLE prprep-api`.
2. Inspect ARQ worker queue backlog: `redis-cli llen arq:queue`.
3. Re-verify health endpoints (`/health`, `/ready`).

---

## 2. Dead-Letter Queue (DLQ) Replay Runbook

1. Query DLQ status via API: `GET /api/queue/status` or list via DLQ manager.
2. Review failure root cause in structured event logs for `event_type="error.dead_letter"`.
3. Replay failed job by invoking `DeadLetterQueue.replay_job(job_id)`.

---

## 3. Secret Rotation & Budget Emergency Stop

### Webhook Secret Rotation
1. Update `GITHUB_WEBHOOK_SECRET` in environment secret store.
2. Update Webhook Secret in GitHub App Settings dashboard.
3. Verify signature verification passes on next webhook event.

### Emergency Budget Stop
1. Set `BUDGET_GUARD_ENABLED=true` and `DAILY_BUDGET_CAP_USD=0.0` in deployment environment variables.
2. Restart API and Worker services. All subsequent LLM calls will fail closed to the Human-in-the-Loop queue (`ROUTED_TO_HITL`).
