# Golden Bun: Full-Stack Food Ordering App (Dockerized)

A fast-food ordering website with a real backend and database, packaged with Docker Compose.
Customers browse a menu, add items to a cart and place orders that are stored in MySQL.
A second page, `/devops.html`, shows live details about the running deployment.

## Architecture

```
Browser --> nginx (frontend, port 8100)
              |-- /            static site (menu, cart, checkout)
              |-- /devops.html live status dashboard
              '-- /api/*  --> Flask backend (port 5000) --> MySQL 8 (volume)
```

| Service | Image | Role |
|------------|--------------------------|----------------------------------------------------|
| `frontend` | nginx:alpine             | Serves the site and proxies `/api/` to the backend |
| `backend`  | python:3.11-slim (Flask) | Menu and order API, creates the table on startup   |
| `db`       | mysql:8.0                | Stores orders in a named volume                    |

## Features
- Menu with categories, cart and checkout
- Orders saved in MySQL (`orders` table, items stored as JSON)
- `/api/health` and `/api/info` endpoints (build version, git commit, serving pod, uptime)
- `/devops.html`: live status page that polls the API every 5 seconds
- Configuration through environment variables; secrets stay in `.env` (git-ignored)
- Backend retries the database connection until MySQL is ready

## Run it
```bash
cp .env.example .env        # set your own passwords
docker compose up -d --build
docker compose ps
```
Open `http://<host>:8100` for the site and `http://<host>:8100/devops.html` for the dashboard.

Stop and clean up:
```bash
docker compose down        # keep data
docker compose down -v     # also delete the database volume
```

## API
| Method | Path          | Description                                                      |
|--------|---------------|------------------------------------------------------------------|
| GET    | `/api/menu`   | Menu items                                                       |
| POST   | `/api/order`  | Place an order `{customer_name, items:[{price, quantity, ...}]}` |
| GET    | `/api/orders` | Last 20 orders                                                   |
| GET    | `/api/health` | Liveness check                                                   |
| GET    | `/api/info`   | Build version, git SHA, pod name, uptime                         |

## Project layout
```
app/backend/    Flask API, requirements.txt, Dockerfile (build args APP_VERSION, GIT_SHA)
app/frontend/   index.html, devops.html, nginx.conf, Dockerfile
docker-compose.yaml
.env.example
infra/          Terraform and Ansible for the cloud deployment (next phases)
```

## What I learned
- Reverse proxying `/api` through nginx so the browser needs only one origin (no CORS or port juggling)
- Passing build metadata into an image with `ARG` and `ENV`
- Waiting for a database to become ready instead of crashing at startup
- Keeping secrets out of git with `.env` and `.gitignore`
- Linux file names are case sensitive (`Devops.html` is not `devops.html`)

## Roadmap
- [x] Phase 1: Dockerized app and dashboard
- [x] Phase 2: Terraform (EC2, security group, Elastic IP)
- [ ] Phase 3: Ansible installs k3s
- [ ] Phase 4: Kubernetes manifests and Ingress
- [ ] Phase 5: Jenkins CI/CD with webhook
