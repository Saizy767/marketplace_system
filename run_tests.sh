#!/usr/bin/env bash
# Утилита для запуска всех тестов в проекте (юнит + интеграционные).
# Запускать из корня workspace.

set -euo pipefail

# активируем виртуальное окружение, если есть
if [[ -f "venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "venv/bin/activate"
fi

# убедимся, что модуль pip доступен, иначе создадим окружение
if ! python -m pip --version >/dev/null 2>&1; then
    echo "pip не найден, пытаемся установить через ensurepip"
    python -m ensurepip --upgrade || {
        echo "Не удалось установить pip автоматически, прекратим" >&2
        exit 1
    }
fi

# убедимся, что зависимости установлены
if [[ -f "requirements.txt" ]]; then
    echo "Установка зависимостей из requirements.txt..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
fi

# если pytest всё ещё не доступен, попробуем установить только его
if ! python -m pytest --version >/dev/null 2>&1; then
    echo "pytest не найден, пробую установить его отдельно"
    python -m pip install pytest
fi

echo "====== Запуск unit-тестов ======"
python -m pytest tests/unit

echo "====== Запуск интеграционных тестов ======"
python -m pytest tests/integrations

echo "Все тесты выполнены."