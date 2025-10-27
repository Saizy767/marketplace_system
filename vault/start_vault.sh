set -e

echo "🔍 Проверка: установлен ли Vault CLI..."
if ! command -v vault &> /dev/null; then
    echo "⚠️  Vault CLI не найден. Установите его: https://developer.hashicorp.com/vault/downloads"
    exit 1
fi

echo "🚀 Запуск Vault контейнера..."
docker run --cap-add=IPC_LOCK -d \
  --name vault \
  -p 8200:8200 \
  -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' \
  -e 'VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200' \
  --rm \
  hashicorp/vault

echo "⏳ Ждём инициализации Vault..."
sleep 3

echo "✅ Vault запущен! Адрес: http://localhost:8200"
echo "🔑 Токен: myroot"
echo ""
echo "Следующий шаг: выполните ./vault/write_secrets.sh"