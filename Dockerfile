# Use official Airflow image
FROM apache/airflow:2.11.0

# === 1. Установка зависимостей (как airflow, как того требует образ) ===
COPY requirements.txt .
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r requirements.txt

# === 2. Копирование исходного кода (от root, чтобы иметь права) ===
USER root
WORKDIR /opt/airflow/project
COPY src/ ./src/
COPY pyproject.toml .
# Копируем DAG-файлы и скрипты в стандартные директории Airflow
COPY dags/ /opt/airflow/dags/
COPY scripts/ /opt/airflow/scripts/

# Даём права пользователю airflow
RUN chown -R airflow:root /opt/airflow/project \
    && chown -R airflow:root /opt/airflow/dags \
    && chown -R airflow:root /opt/airflow/scripts

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

# === 3. Переключаемся обратно на airflow и настраиваем PYTHONPATH ===
USER airflow
ENV PYTHONPATH=/opt/airflow/project:$PYTHONPATH

# === 4. Airflow config ===
ENV AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False

# === 5. Secrets Backend: HashiCorp Vault ===
ENV AIRFLOW__SECRETS__BACKEND=airflow.providers.hashicorp.secrets.vault.VaultBackend
ENV AIRFLOW__SECRETS__BACKEND_KWARGS="{\"url\": \"http://host.docker.internal:8200\", \"token\": \"myroot\", \"mount_point\": \"secret\"}"
# === 6. Проверка импорта ===
RUN python -c "import src; print('✅ src imported from:', src.__file__)"