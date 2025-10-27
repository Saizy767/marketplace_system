from airflow.models import Variable

def test_vault_secrets():
    try:
        api_key = Variable.get("API_KEY")
        base_url = Variable.get("API_BASE_URL")
        print("✅ API_KEY:", api_key[:10] + "...")
        print("✅ API_BASE_URL:", base_url)
    except KeyError as e:
        print("❌ Секрет не найден:", e)

if __name__ == "__main__":
    test_vault_secrets()