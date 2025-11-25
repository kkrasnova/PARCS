"""
Скрипт для тестування та порівняння продуктивності
послідовного та паралельного алгоритмів пошуку простих чисел.
"""

import time
import sys
from sequential_prime_finder import find_primes_sequential
from parallel_prime_finder import find_primes_parallel


def compare_algorithms(start, end, num_workers_list=[1, 2, 4, 8]):
    """
    Порівнює продуктивність послідовного та паралельного алгоритмів.
    
    Args:
        start: Початок діапазону
        end: Кінець діапазону
        num_workers_list: Список кількості воркерів для тестування
    """
    print("=" * 70)
    print(f"ПОРІВНЯННЯ АЛГОРИТМІВ ПОШУКУ ПРОСТИХ ЧИСЕЛ")
    print("=" * 70)
    print(f"Діапазон: [{start}, {end}]")
    print(f"Загальна кількість чисел: {end - start + 1:,}")
    print("=" * 70)
    
    results = []
    
    # Тестуємо послідовний алгоритм
    print("\n1. Послідовний алгоритм")
    print("-" * 70)
    seq_primes, seq_time = find_primes_sequential(start, end)
    results.append({
        'type': 'Послідовний',
        'workers': 1,
        'primes_count': len(seq_primes),
        'time': seq_time,
        'speedup': 1.0
    })
    print(f"   Час виконання: {seq_time:.4f} секунд")
    print(f"   Знайдено простих чисел: {len(seq_primes):,}")
    
    # Тестуємо паралельний алгоритм з різною кількістю воркерів
    print("\n2. Паралельний алгоритм")
    print("-" * 70)
    
    for num_workers in num_workers_list:
        print(f"\n   Тест з {num_workers} воркер(ами):")
        try:
            par_primes, par_time = find_primes_parallel(start, end, num_workers)
            speedup = seq_time / par_time if par_time > 0 else 0
            efficiency = speedup / num_workers
            
            results.append({
                'type': 'Паралельний',
                'workers': num_workers,
                'primes_count': len(par_primes),
                'time': par_time,
                'speedup': speedup,
                'efficiency': efficiency
            })
            
            print(f"      Час виконання: {par_time:.4f} секунд")
            print(f"      Знайдено простих чисел: {len(par_primes):,}")
            print(f"      Прискорення (speedup): {speedup:.2f}x")
            print(f"      Ефективність: {efficiency:.2%}")
            
            # Перевірка коректності результатів
            if set(seq_primes) == set(par_primes):
                print(f"      ✓ Результати коректні")
            else:
                print(f"      ✗ Помилка: результати не співпадають!")
                diff = set(seq_primes) - set(par_primes)
                if diff:
                    print(f"      Відсутні в паралельному: {list(diff)[:10]}")
                diff = set(par_primes) - set(seq_primes)
                if diff:
                    print(f"      Зайві в паралельному: {list(diff)[:10]}")
        except Exception as e:
            print(f"      ✗ Помилка: {e}")
            results.append({
                'type': 'Паралельний',
                'workers': num_workers,
                'primes_count': 0,
                'time': 0,
                'speedup': 0,
                'error': str(e)
            })
    
    # Підсумкова таблиця
    print("\n" + "=" * 70)
    print("ПІДСУМКОВА ТАБЛИЦЯ РЕЗУЛЬТАТІВ")
    print("=" * 70)
    print(f"{'Тип':<15} {'Воркери':<10} {'Час (с)':<12} {'Прискорення':<12} {'Ефективність':<12}")
    print("-" * 70)
    
    for result in results:
        if 'error' not in result:
            eff_str = f"{result.get('efficiency', 0):.2%}" if 'efficiency' in result else "N/A"
            print(f"{result['type']:<15} {result['workers']:<10} {result['time']:<12.4f} "
                  f"{result['speedup']:<12.2f} {eff_str:<12}")
        else:
            print(f"{result['type']:<15} {result['workers']:<10} {'ERROR':<12} "
                  f"{'N/A':<12} {'N/A':<12}")
    
    print("=" * 70)
    
    return results


def main():
    """Головна функція."""
    if len(sys.argv) < 3:
        print("Використання: python test_performance.py <start> <end> [workers...]")
        print("Приклад: python test_performance.py 1 1000000 2 4 8")
        sys.exit(1)
    
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    workers = [int(w) for w in sys.argv[3:]] if len(sys.argv) > 3 else [2, 4, 8]
    
    compare_algorithms(start, end, workers)


if __name__ == "__main__":
    main()

