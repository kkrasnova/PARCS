"""
Паралельний алгоритм пошуку простих чисел з використанням PARCS-Python (Pyro4).
Ця версія використовує правильний API PARCS-Python з Pyro4.
"""

import sys
import os
import math
import time

# Додаємо parcs-python до шляху
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'parcs-python'))

from Pyro4 import expose


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


class PrimeSolver:
    """
    Клас для паралельного пошуку простих чисел з використанням PARCS.
    """
    
    def __init__(self, workers=None, start=None, end=None):
        """
        Ініціалізація Solver.
        
        Args:
            workers: Список воркерів (отримується від PARCS)
            start: Початок діапазону
            end: Кінець діапазону
        """
        self.workers = workers
        self.start = start
        self.end = end
        print("PrimeSolver ініціалізовано")
        print(f"Воркерів: {len(workers) if workers else 0}")
        print(f"Діапазон: [{start}, {end}]")
    
    def solve(self):
        """
        Головна функція для вирішення задачі.
        """
        print("Початок обчислення...")
        start_time = time.time()
        
        if not self.workers:
            print("Помилка: немає воркерів!")
            return []
        
        # Розділяємо діапазон між воркерами
        total_range = self.end - self.start + 1
        chunk_size = total_range // len(self.workers)
        remaining = total_range % len(self.workers)
        
        # Map фаза: розподіляємо завдання
        mapped = []
        current_start = self.start
        
        for i in range(len(self.workers)):
            chunk_end = current_start + chunk_size - 1
            if i < remaining:
                chunk_end += 1
            
            if chunk_end > self.end:
                chunk_end = self.end
            
            if current_start <= self.end:
                print(f"Відправка завдання воркеру {i}: [{current_start}, {chunk_end}]")
                mapped.append(self.workers[i].find_primes_in_range(str(current_start), str(chunk_end)))
            
            current_start = chunk_end + 1
        
        # Reduce фаза: збираємо результати
        all_primes = self.reduce_results(mapped)
        
        # Сортуємо
        all_primes.sort()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Обчислення завершено за {execution_time:.4f} секунд")
        print(f"Знайдено простих чисел: {len(all_primes)}")
        
        return all_primes, execution_time
    
    @staticmethod
    def reduce_results(mapped):
        """
        Об'єднує результати з усіх воркерів.
        
        Args:
            mapped: Список результатів від воркерів
            
        Returns:
            Об'єднаний список простих чисел
        """
        print("Збір результатів...")
        all_primes = []
        
        for result in mapped:
            # Результат від Pyro4 може бути об'єктом з атрибутом value
            if hasattr(result, 'value'):
                primes = result.value
            else:
                primes = result
            
            # Перетворюємо на список чисел
            if isinstance(primes, list):
                all_primes.extend([int(p) for p in primes if p])
            elif isinstance(primes, str):
                # Якщо рядок, розділяємо
                primes_list = [int(p.strip()) for p in primes.split(',') if p.strip()]
                all_primes.extend(primes_list)
        
        print(f"Зібрано {len(all_primes)} простих чисел")
        return all_primes
    
    @staticmethod
    @expose
    def find_primes_in_range(start_str, end_str):
        """
        Знаходить прості числа в заданому діапазоні.
        Ця функція виконується на воркері.
        
        Args:
            start_str: Початок діапазону (рядок)
            end_str: Кінець діапазону (рядок)
            
        Returns:
            Список простих чисел у діапазоні
        """
        start = int(start_str)
        end = int(end_str)
        
        print(f"Воркер обробляє діапазон [{start}, {end}]")
        
        primes = []
        for num in range(start, end + 1):
            if is_prime(num):
                primes.append(str(num))
        
        print(f"Воркер знайшов {len(primes)} простих чисел")
        return primes


def main():
    """
    Головна функція для тестування.
    Примітка: Для повної роботи потрібен запущений PARCS coordinator та workers.
    """
    if len(sys.argv) < 3:
        print("Використання: python parallel_prime_finder_pyro4.py <start> <end>")
        print("Приклад: python parallel_prime_finder_pyro4.py 1 100000")
        print("")
        print("Примітка: Для роботи потрібен запущений PARCS coordinator та workers.")
        print("Дивіться інструкції в QUICK_START_GCP.md")
        sys.exit(1)
    
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    
    print("=" * 60)
    print("Паралельний алгоритм пошуку простих чисел (PARCS-Python)")
    print("=" * 60)
    print(f"Діапазон: [{start}, {end}]")
    print("")
    print("Примітка: Цей скрипт потребує налаштованого PARCS.")
    print("Для тестування без PARCS використайте sequential_prime_finder.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

