# ---------------------------------------------------------------------------
# Base image: python:3.12-alpine
#  - Alpine Linux is ~5 MB, so the final image stays very small (~60-70 MB)
#    compared to python:3.12 (~1 GB) or python:3.12-slim (~150 MB).
#  - Smaller image = faster pull/push, and fewer packages = smaller attack surface.
#  - All our dependencies (Flask, redis, gunicorn) are pure Python, so we do
#    not need compilers or glibc: Alpine (musl) is a perfect fit.
# ---------------------------------------------------------------------------
FROM python:3.12-alpine

# Do not write .pyc files and do not buffer stdout (logs appear immediately
# in "docker logs").
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=5000

WORKDIR /app

# Security: create an unprivileged system user/group. The app will never run
# as root, so a compromised process cannot get root access in the container.
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Docker cache optimisation: copy ONLY the dependency list first.
# This layer (and the pip install below) is rebuilt only when requirements.txt
# changes. Editing app.py does NOT re-download the dependencies.
COPY app/requirements.txt .

# --no-cache-dir: do not keep pip's download cache inside the image (smaller).
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code last: it changes most often, so it is the last layer.
# --chown gives the files to our non-root user.
COPY --chown=appuser:appgroup app/app.py .

# Switch to the non-root user for everything that follows (including CMD).
USER appuser

# Documentation: the app listens on port 5000 inside the container.
EXPOSE 5000

# Lightweight healthcheck using the Python already present (no curl needed).
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,os; urllib.request.urlopen('http://127.0.0.1:'+os.environ['APP_PORT']+'/health')" || exit 1

# CMD = the command executed when the CONTAINER STARTS (not at build time).
# gunicorn is a production WSGI server (Flask's built-in server is for dev only).
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${APP_PORT} --workers 2 app:app"]
