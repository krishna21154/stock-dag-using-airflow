FROM python:3.11-slim

ARG AIRFLOW_VERSION=2.9.1
ARG AIRFLOW_UID=50000
ARG PYTHON_VERSION=3.11

ENV AIRFLOW_HOME=/opt/airflow \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    COLUMNS=120 \
    AIRFLOW__CORE__LOAD_EXAMPLES=False \
    PATH="/home/airflow/.local/bin:$PATH" \
    PYTHONPATH="/opt/airflow:/opt/airflow/app:$PYTHONPATH"

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        gcc \
        netcat-traditional \
        ca-certificates; \
    rm -rf /var/lib/apt/lists/*

# Create airflow user and dirs
RUN set -eux; \
    groupadd -g ${AIRFLOW_UID} airflow || true; \
    useradd -m -u ${AIRFLOW_UID} -g ${AIRFLOW_UID} airflow || true; \
    mkdir -p ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/plugins ${AIRFLOW_HOME}/app; \
    chown -R ${AIRFLOW_UID}:${AIRFLOW_UID} ${AIRFLOW_HOME}

WORKDIR ${AIRFLOW_HOME}

# Install Airflow using constraints for reproducibility
RUN set -eux; \
    CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"; \
    pip install "apache-airflow[celery,postgres,redis]==${AIRFLOW_VERSION}" --constraint "$CONSTRAINT_URL"

# Install project Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy application utilities (modular code imported by the DAG)
COPY app/ ${AIRFLOW_HOME}/app/

USER ${AIRFLOW_UID}

EXPOSE 8080

ENTRYPOINT ["airflow"]

