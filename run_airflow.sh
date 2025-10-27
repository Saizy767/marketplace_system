#!/bin/bash
set -e

IMAGE_NAME="marketplace_airflow"
CONTAINER_NAME="marketplace_airflow_standalone"
VAULT_CONTAINER_NAME="vault"

# === 1. Запуск Vault, если не запущен ===
if [ "$(docker ps -q -f name=^/${VAULT_CONTAINER_NAME}$)" ]; then
    echo "✅ Vault уже запущен."
else
    echo "🔍 Vault не запущен. Запускаем..."
    if [ ! -f "vault/start_vault.sh" ]; then
        echo "❌ Файл vault/start_vault.sh не найден!"
        exit 1
    fi
    chmod +x vault/start_vault.sh
    ./vault/start_vault.sh
fi

# === 2. Запись секретов, если файл существует ===
if [ -f "vault/write_secrets.sh" ]; then
    echo "🔐 Проверяем наличие секретов в Vault..."
    export VAULT_ADDR="http://localhost:8200"
    export VAULT_TOKEN="myroot"
    if ! vault kv get secret/airflow/marketplace_system >/dev/null 2>&1; then
        echo "⚠️ Секреты не найдены. Записываем из vault/write_secrets.sh..."
        chmod +x vault/write_secrets.sh
        ./vault/write_secrets.sh
    else
        echo "✅ Секреты уже записаны в Vault."
    fi
else
    echo "ℹ️ Файл vault/write_secrets.sh не найден. Убедитесь, что секреты записаны вручную!"
fi

# === 3. Сборка образа Airflow ===
echo "📦 Сборка Docker-образа Airflow..."
docker build -t "$IMAGE_NAME" .

# === 4. Очистка старого контейнера Airflow ===
echo "🛑 Остановка и удаление старого контейнера Airflow (если существует)..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# === 5. Добавление host.docker.internal для Linux ===
EXTRA_ARGS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  echo "🐧 Обнаружена Linux-система: добавляем --add-host=host.docker.internal:host-gateway"
  EXTRA_ARGS="--add-host=host.docker.internal:host-gateway"
fi

# === 6. Запуск Airflow ===
echo "🚀 Запуск Airflow контейнера..."
docker run -d \
  $EXTRA_ARGS \
  --name "$CONTAINER_NAME" \
  -p 8080:8080 \
  "$IMAGE_NAME" \
  standalone

echo "⏳ Ждём инициализации Airflow (40 секунд)..."
sleep 40

# === 7. Создание Airflow Connection к PostgreSQL ===
echo "🔗 Создание Airflow Connection 'postgres' к локальному PostgreSQL..."
docker exec "$CONTAINER_NAME" \
  airflow connections add "postgres" \
    --conn-type "postgres" \
    --conn-host "host.docker.internal" \
    --conn-port "5432" \
    --conn-schema "postgres" \
    --conn-login "saizy"
    # Раскомментируйте, если у вас есть пароль:
    # --conn-password "ваш_пароль"
echo ""
echo "✅ Airflow запущен! Откройте http://localhost:8080"