#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования поиска простых чисел с использованием входных файлов
"""

import sys
import os
from sequential_prime_finder import find_primes_sequential

def test_with_input_file(input_file):
    """
    Тестирует поиск простых чисел с использованием входного файла
    
    Args:
        input_file: Путь к входному файлу
    """
    if not os.path.exists(input_file):
        print(f"Ошибка: файл {input_file} не найден")
        return
    
    print(f"\n{'='*60}")
    print(f"Тест с файлом: {input_file}")
    print(f"{'='*60}")
    
    # Читаем входные данные
    with open(input_file, 'r') as f:
        start = int(f.readline().strip())
        end = int(f.readline().strip())
    
    print(f"Диапазон: [{start:,}, {end:,}]")
    print(f"Всего чисел для проверки: {end - start + 1:,}")
    print()
    
    # Запускаем поиск
    print("Запуск поиска простых чисел...")
    primes, execution_time = find_primes_sequential(start, end)
    
    # Выводим результаты
    print(f"\nРезультаты:")
    print(f"  Найдено простых чисел: {len(primes):,}")
    print(f"  Время выполнения: {execution_time:.4f} секунд")
    
    if execution_time > 0:
        numbers_per_second = (end - start + 1) / execution_time
        print(f"  Скорость: {numbers_per_second:,.0f} чисел/сек")
    
    # Показываем первые и последние простые числа
    if len(primes) > 0:
        print(f"\n  Первые 10 простых чисел: {primes[:10]}")
        if len(primes) > 10:
            print(f"  Последние 10 простых чисел: {primes[-10:]}")
    
    print(f"{'='*60}\n")


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        # Если аргументы не указаны, тестируем все доступные входные файлы
        input_files = [
            'prime_input_10000.txt',
            'prime_input_100000.txt',
            'prime_input_1000000.txt'
        ]
        
        print("Тестирование со всеми доступными входными файлами")
        print("="*60)
        
        for input_file in input_files:
            if os.path.exists(input_file):
                test_with_input_file(input_file)
            else:
                print(f"Файл {input_file} не найден, пропускаем...")
    else:
        # Тестируем указанный файл
        test_with_input_file(sys.argv[1])


if __name__ == "__main__":
    main()

