FROM apache/airflow:2.10.3-python3.14

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /opt/airflow/marketplace_system
WORKDIR /opt/airflow/marketplace_system
RUN pip install -e .

ENV AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/marketplace_system/dags
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False

COPY .env /opt/airflow/.env