"""Visit-Counter web app.

Every visit increments the Redis key "hits" and the page shows the total count
plus the ID (hostname) of the container that answered the request.
"""
import os
import socket

from flask import Flask
from redis import Redis, RedisError

app = Flask(__name__)

# The Redis host defaults to "db-service": on a Docker network, the container
# name is resolved by Docker's internal DNS, so we never hard-code an IP.
redis = Redis(
    host=os.getenv("REDIS_HOST", "db-service"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    socket_connect_timeout=2,
    socket_timeout=2,
)

#testing jenkins

def get_hit_count():
    """Atomically increment and return the 'hits' counter."""
    return redis.incr("hits")


@app.route("/")
def index():
    container_id = socket.gethostname()  # Docker sets hostname = short container ID
    try:
        count = get_hit_count()
    except RedisError:
        return (
            f"Erreur : impossible de joindre Redis. Je suis le conteneur {container_id}\n",
            503,
        )
    return f"Bonjour ! Cette page a été vue {count} fois. Je suis le conteneur {container_id}\n"


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("APP_PORT", "5000")))
