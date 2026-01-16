
## Docker Management Cheat Sheet

### Managing the Application
| Action | Command |
| :--- | :--- |
| **Start** (Background) | `docker compose up -d` |
| **Stop** | `docker compose down` |
| **Restart** | `docker compose restart` |
| **Rebuild & Start** | `docker compose up -d --build` |
| **Rebuild & Start Service** | `docker compose up -d --build app` |

> **Note**: The `app` argument refers to the service name defined in `docker-compose.yml`.

### Monitoring & Status
| Action | Command |
| :--- | :--- |
| **View Running Containers** | `docker compose ps` or `docker ps` |
| **View All Containers** | `docker ps -a` |
| **View Installed Images** | `docker images` |
| **View Live Logs** | `docker compose logs -f` |
| **Check Resource Usage** | `docker stats` |
| **View Container Logs** | `docker logs fasts-app-1` |
| **Kill All Running Containers** | `docker kill $(docker ps -q)` |

### Cleanup
| Action | Command |
| :--- | :--- |
| **View Disk Usage** | `docker system df` |
| **Remove Unused Images** | `docker image prune -a` |
| **Remove All Unused Data** | `docker system prune` |