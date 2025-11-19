# follow-watch
Production-ready skeleton for celebrity follow/unfollow watcher. Includes receiver, worker, publisher, infra, CI and runbook.

## Local dev
1. Copy .env.example into each service and fill secrets.
2. Start services: `docker-compose up --build`
3. Apply schema: `psql -h localhost -U pw_user -d followwatch -f sql/schema.sql`
4. Send test webhook to `http://localhost:8000/x-events` with HMAC signature.

## Production
- Build images and push to registry
- Deploy k8s manifests in `infra/k8s/`
- Configure secrets (followwatch-secrets)
- Configure Prometheus/Grafana to scrape metrics
