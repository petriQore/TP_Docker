# Jenkins + Docker CLI + Python, so the pipeline can run tests and docker builds.
FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends docker.io python3 python3-venv python3-pip \
 && rm -rf /var/lib/apt/lists/*
# Pre-install the plugins the pipeline needs
RUN jenkins-plugin-cli --plugins workflow-aggregator git github credentials-binding timestamper
USER jenkins
