"""
Послідовний алгоритм пошуку простих чисел у великому діапазоні.
Використовує решето Ератосфена для оптимізації.
"""

import time
import math


def is_prime(n):
    """
    Перевіряє, чи є число простим.
    
    Args:
        n: Число для перевірки
        
    Returns:
        True, якщо число просте, інакше False
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    sqrt_n = int(math.sqrt(n)) + 1
    for i in range(3, sqrt_n, 2):
        if n % i == 0:
            return False
    return True


def sieve_of_eratosthenes(limit):
    """
    Решето Ератосфена для знаходження всіх простих чисел до limit.
    
    Args:
        limit: Верхня межа діапазону
        
    Returns:
        Список простих чисел
    """
    if limit < 2:
        return []
    
    # Створюємо масив, де True означає просте число
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    # Застосовуємо решето
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    # Збираємо всі прості числа
    primes = [i for i in range(2, limit + 1) if is_prime[i]]
    return primes


def find_primes_sequential(start, end):
    """
    Знаходить всі прості числа в діапазоні [start, end] послідовним методом.
    
    Args:
        start: Початок діапазону
        end: Кінець діапазону
        
    Returns:
        Список простих чисел та час виконання
    """
    start_time = time.time()
    
    primes = []
    
    # Для малих діапазонів використовуємо решето Ератосфена
    if end - start < 1000000:
        all_primes = sieve_of_eratosthenes(end)
        primes = [p for p in all_primes if p >= start]
    else:
        # Для великих діапазонів перевіряємо кожне число
        for num in range(start, end + 1):
            if is_prime(num):
                primes.append(num)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return primes, execution_time


def main():
    """Головна функція для тестування послідовного алгоритму."""
    print("Послідовний алгоритм пошуку простих чисел")
    print("=" * 50)
    
    # Тестові діапазони
    test_ranges = [
        (1, 100),
        (1, 1000),
        (1, 10000),
        (1, 100000),
        (1, 1000000),
    ]
    
    for start, end in test_ranges:
        print(f"\nДіапазон: [{start}, {end}]")
        primes, execution_time = find_primes_sequential(start, end)
        print(f"Знайдено простих чисел: {len(primes)}")
        print(f"Час виконання: {execution_time:.4f} секунд")
        if len(primes) <= 20:
            print(f"Прості числа: {primes}")


if __name__ == "__main__":
    main()

