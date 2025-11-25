#!/bin/bash
# Главный скрипт запуска - запускает все компоненты проекта

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Запуск проекта: Поиск простых чисел в большом диапазоне ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Активация виртуального окружения
if [ -d "venv" ]; then
    echo "✓ Активация виртуального окружения..."
    source venv/bin/activate
else
    echo "⚠ Предупреждение: виртуальное окружение не найдено"
    echo "  Создайте его командой: python3 -m venv venv"
fi

echo ""
echo "Выберите действие:"
echo "  1) Запустить все тесты (run_all.sh)"
echo "  2) Тест с входными файлами (test_with_input.py)"
echo "  3) Последовательный поиск (sequential_prime_finder.py)"
echo "  4) Проверить статус GCP инстансов"
echo "  5) Запустить GCP инстансы (если настроено)"
echo "  6) Выход"
echo ""
read -p "Ваш выбор (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Запуск всех тестов..."
        ./run_all.sh
        ;;
    2)
        echo ""
        echo "Тестирование с входными файлами..."
        python test_with_input.py
        ;;
    3)
        echo ""
        echo "Последовательный поиск простых чисел..."
        python sequential_prime_finder.py
        ;;
    4)
        echo ""
        echo "Проверка статуса GCP инстансов..."
        ./list_instances.sh
        ;;
    5)
        echo ""
        echo "Запуск GCP инстансов..."
        ./start_instances.sh
        ;;
    6)
        echo "Выход..."
        exit 0
        ;;
    *)
        echo "Неверный выбор. Запуск всех тестов по умолчанию..."
        ./run_all.sh
        ;;
esac

echo ""
echo "✓ Готово!"

