# -*- coding: utf-8 -*-
"""
Solution File для PARCS - пошук простих чисел у діапазоні
Використовується для завантаження через веб-інтерфейс PARCS
"""

from Pyro4 import expose
import math


try:
    xrange  
except NameError:
    xrange = range  


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Solver initialized")

    def solve(self):
        """Головна функція для вирішення задачі"""
        print("Job Started")
        print("Workers %d" % len(self.workers))
        
        # Читаємо вхідні дані
        start, end = self.read_input()
        print("Range: [%d, %d]" % (start, end))
        
        # Розділяємо діапазон між workers
        total_range = end - start + 1
        step = total_range / len(self.workers)
        
        # Map фаза: розподіляємо завдання
        mapped = []
        # Використовуємо xrange для сумісності з Python 2 (якщо потрібно)
        worker_range = xrange(len(self.workers))
        
        for i in worker_range:
            chunk_start = int(start + i * step)
            chunk_end = int(start + (i + 1) * step) - 1
            if i == len(self.workers) - 1:
                chunk_end = end  # Останній worker отримує залишок
            
            print("Sending to worker %d: [%d, %d]" % (i, chunk_start, chunk_end))
            mapped.append(self.workers[i].find_primes_in_range(str(chunk_start), str(chunk_end)))
        
        # Reduce фаза: збираємо результати
        all_primes = self.myreduce(mapped)
        
        # Записуємо результат (all_primes вже список рядків)
        self.write_output(all_primes)
        
        print("Computation finished. Found %d primes" % len(all_primes))
        print("Job Finished")

    @staticmethod
    @expose
    def find_primes_in_range(start_str, end_str):
        """
        Знаходить прості числа в заданому діапазоні.
        Виконується на worker node.
        Оптимізовано для великих діапазонів.
        """
        start = int(start_str)
        end = int(end_str)
        
        print("Worker processing range [%d, %d]" % (start, end))
        
        # Для малих діапазонів використовуємо простий алгоритм
        # Для великих - оптимізований з пропуском парних чисел
        primes = []
        
        # Якщо початок менше 2, додаємо 2 якщо в діапазоні
        if start <= 2 and end >= 2:
            primes.append("2")
            start = 3
        
        # Перевіряємо тільки непарні числа
        if start % 2 == 0:
            start += 1
        
        # Використовуємо xrange для сумісності з Python 2 (якщо потрібно)
        num_range = xrange(start, end + 1, 2)
        
        # Додаємо прогрес для великих діапазонів
        total = (end - start) // 2 + 1
        step_report = max(1, total // 10)  # Звітуємо кожні 10%
        count = 0
        
        for num in num_range:
            if Solver.is_prime(num):
                primes.append(str(num))
            count += 1
            if count % step_report == 0:
                progress = (count * 100) // total
                print("Worker progress: %d%% (%d/%d)" % (progress, count, total))
        
        print("Worker found %d primes" % len(primes))
        return primes

    @staticmethod
    @expose
    def is_prime(n):
        """
        Перевіряє, чи є число простим.
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        sqrt_n = int(math.sqrt(n)) + 1
        # Використовуємо xrange для сумісності з Python 2 (якщо потрібно)
        i_range = xrange(3, sqrt_n, 2)
        
        for i in i_range:
            if n % i == 0:
                return False
        return True

    @staticmethod
    @expose
    def myreduce(mapped):
        """
        Об'єднує результати з усіх workers.
        """
        print("reduce")
        output = []
        
        for primes in mapped:
            print("reduce loop")
            # Результат від Pyro4 може бути або списком, або об'єктом з атрибутом value (для async)
            if hasattr(primes, 'value'):
                output = output + primes.value
            else:
                # Якщо це вже список
                output = output + primes
        print("reduce done")
        return output

    def read_input(self):
        """
        Читає вхідні дані з файлу.
        Формат: перший рядок - початок діапазону, другий рядок - кінець діапазону
        """
        f = open(self.input_file_name, 'r')
        start = int(f.readline().strip())
        end = int(f.readline().strip())
        f.close()
        return start, end

    def write_output(self, output):
        """
        Записує результати у файл.
        """
        try:
            f = open(self.output_file_name, 'w')
            # output вже список рядків
            if output and len(output) > 0:
                f.write(', '.join(output))
            else:
                f.write('No primes found')
            f.write('\n')
            f.close()
            print("output done - file written to: %s" % self.output_file_name)
        except Exception as e:
            print("ERROR writing output: %s" % str(e))
            raise

