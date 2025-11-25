#!/bin/bash
# Универсальный скрипт для запуска всех компонентов проекта

set -e  # Остановка при ошибке

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Запуск всех компонентов проекта"
echo "=========================================="
echo ""

# Активация виртуального окружения
if [ -d "venv" ]; then
    echo "Активация виртуального окружения..."
    source venv/bin/activate
else
    echo "Предупреждение: виртуальное окружение не найдено"
fi

echo ""
echo "1. Тестирование последовательного алгоритма поиска простых чисел"
echo "-------------------------------------------------------------------"
python sequential_prime_finder.py

echo ""
echo "2. Тестирование с входными файлами"
echo "-------------------------------------------------------------------"

# Тест с разными входными файлами
for input_file in prime_input_10000.txt prime_input_100000.txt prime_input_1000000.txt; do
    if [ -f "$input_file" ]; then
        echo ""
        echo "Тест с файлом: $input_file"
        start=$(head -n 1 "$input_file")
        end=$(head -n 2 "$input_file" | tail -n 1)
        echo "Диапазон: [$start, $end]"
        
        # Запускаем последовательный поиск
        python -c "
from sequential_prime_finder import find_primes_sequential
import sys
start = int('$start')
end = int('$end')
primes, time_taken = find_primes_sequential(start, end)
print(f'Найдено простых чисел: {len(primes):,}')
print(f'Время выполнения: {time_taken:.4f} секунд')
if len(primes) <= 20:
    print(f'Простые числа: {primes}')
"
    fi
done

echo ""
echo "3. Проверка синтаксиса всех Python скриптов"
echo "-------------------------------------------------------------------"
for py_file in *.py; do
    if [ -f "$py_file" ]; then
        echo "Проверка $py_file..."
        python -m py_compile "$py_file" 2>/dev/null && echo "  ✓ OK" || echo "  ✗ Ошибка"
    fi
done

echo ""
echo "4. Проверка доступности GCP инстансов (если настроено)"
echo "-------------------------------------------------------------------"
if command -v gcloud &> /dev/null; then
    echo "Проверка статуса инстансов..."
    ./list_instances.sh 2>&1 | head -n 10 || echo "  GCP не настроен или нет доступа"
else
    echo "  gcloud CLI не установлен"
fi

echo ""
echo "=========================================="
echo "Все тесты завершены!"
echo "=========================================="
echo ""
echo "Для запуска PARCS на GCP:"
echo "  1. ./start_instances.sh  - запустить инстансы"
echo "  2. Настроить PARCS на инстансах"
echo "  3. Использовать веб-интерфейс PARCS для создания jobs"
echo ""

