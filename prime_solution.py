# -*- coding: utf-8 -*-
"""
Solution File для PARCS - пошук простих чисел у діапазоні
Використовується для завантаження через веб-інтерфейс PARCS
"""

from Pyro4 import expose
import math
import time
import threading


try:
    xrange  
except NameError:
    xrange = range  


def format_time(elapsed_ms):
    """
    Форматує час у детальному форматі: завжди показує секунди та мілісекунди.
    """
    if elapsed_ms < 1000:
        # Для малих значень показуємо мілісекунди з секундами
        return "0 s %.3f ms (%.3f ms total)" % (elapsed_ms, elapsed_ms)
    else:
        seconds = int(elapsed_ms // 1000)
        milliseconds = elapsed_ms % 1000
        return "%d s %.3f ms (%.3f ms total)" % (seconds, milliseconds, elapsed_ms)


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        self.execution_mode = None  # "SEQUENTIAL" або "PARALLEL"
        self.algorithm_used = None  # "Sieve of Eratosthenes" або "Prime Checking"
        self.num_workers_used = 0
        print("Solver initialized")

    def solve(self):
        """Головна функція для вирішення задачі"""
        try:
            print("Job Started")
            workers_count = len(self.workers) if self.workers else 0
            print("Total workers available: %d" % workers_count)
            
            # Читаємо вхідні дані
            start, end, max_workers = self.read_input()
            print("Range: [%d, %d]" % (start, end))
        except Exception as e:
            print("ERROR in solve initialization: %s" % str(e))
            import traceback
            traceback.print_exc()
            raise
        
        # Послідовний алгоритм: якщо немає воркерів або max_workers = 0
        if not self.workers or workers_count == 0 or (max_workers is not None and max_workers == 0):
            try:
                self.execution_mode = "SEQUENTIAL"
                self.num_workers_used = 0
                print("=" * 60)
                print("MODE: SEQUENTIAL ALGORITHM")
                print("Reason: No workers available or max_workers = 0")
                print("=" * 60)
                # Визначаємо алгоритм на основі діапазону ПЕРЕД виконанням
                SIEVE_LIMIT = 10000000
                if end <= SIEVE_LIMIT:
                    self.algorithm_used = "Sieve of Eratosthenes"
                else:
                    self.algorithm_used = "Prime Checking (trial division)"
                start_time = time.time()
                all_primes = self.find_primes_in_range(str(start), str(end))
                end_time = time.time()
                elapsed_ms = (end_time - start_time) * 1000
                self.write_output(all_primes, elapsed_ms)
                print("")
                print("=" * 70)
                print("PERFORMANCE SUMMARY")
                print("=" * 70)
                print("Range: [%d, %d]" % (start, end))
                print("Total range size: %d" % (end - start + 1))
                print("Execution mode: SEQUENTIAL")
                print("Algorithm: %s" % self.algorithm_used)
                print("Execution time: %s" % format_time(elapsed_ms))
                print("=" * 70)
                print("")
                print("Computation finished. Found %d primes" % len(all_primes))
                print("Sequential algorithm execution time: %s" % format_time(elapsed_ms))
                print("Job Finished")
                return
            except Exception as e:
                print("ERROR in sequential algorithm: %s" % str(e))
                import traceback
                traceback.print_exc()
                # Забезпечуємо, що змінні встановлені навіть при помилці
                if not self.execution_mode:
                    self.execution_mode = "SEQUENTIAL"
                if not self.algorithm_used:
                    self.algorithm_used = "UNKNOWN (error occurred)"
                raise
        
        # Обмежуємо кількість workers, якщо вказано
        try:
            self.execution_mode = "PARALLEL"
            print("=" * 60)
            print("MODE: PARALLEL ALGORITHM")
            if max_workers and max_workers > 0 and max_workers < len(self.workers):
                workers_to_use = self.workers[:max_workers]
                self.num_workers_used = len(workers_to_use)
                print("Using %d workers (requested: %d, available: %d)" % (len(workers_to_use), max_workers, len(self.workers)))
            else:
                workers_to_use = self.workers
                self.num_workers_used = len(workers_to_use)
                print("Using all %d workers" % len(workers_to_use))
            print("=" * 60)
            
            # Розділяємо діапазон між workers
            total_range = end - start + 1
            chunk_size = total_range // len(workers_to_use)
            remainder = total_range % len(workers_to_use)
            
            # Визначаємо алгоритм на основі загального діапазону ПЕРЕД виконанням
            SIEVE_LIMIT = 10000000
            if end <= SIEVE_LIMIT:
                self.algorithm_used = "Sieve of Eratosthenes"
            else:
                self.algorithm_used = "Prime Checking (trial division)"
            
            # Map фаза: розподіляємо завдання ПАРАЛЕЛЬНО
            parallel_start_time = time.time()
            mapped = [None] * len(workers_to_use)  # Попередньо виділяємо місце
            worker_times = [0.0] * len(workers_to_use)  # Зберігаємо час виконання кожного воркера
            worker_results = [None] * len(workers_to_use)
            worker_primes_count = [0] * len(workers_to_use)
            current_start = start
            
            # Структури для синхронізації потоків
            threads = []
            lock = threading.Lock()
            
            print("")
            print("=" * 70)
            print("PARALLEL EXECUTION - DETAILED TIMING")
            print("=" * 70)
            print("Starting %d workers in PARALLEL mode..." % len(workers_to_use))
            print("")
            
            def worker_thread(worker_idx, chunk_start, chunk_end):
                """Функція для виконання в окремому потоці"""
                thread_start_time = time.time()
                try:
                    print(">>> Worker %d STARTED at %.3f: Processing range [%d, %d] (size: %d)" % 
                          (worker_idx, thread_start_time, chunk_start, chunk_end, chunk_end - chunk_start + 1))
                    
                    # Час перед викликом воркера
                    call_start_time = time.time()
                    
                    # Викликаємо воркера (це блокує потік до отримання результату)
                    worker_result = workers_to_use[worker_idx].find_primes_in_range(str(chunk_start), str(chunk_end))
                    
                    # Час після отримання результату
                    call_end_time = time.time()
                    worker_elapsed_ms = (call_end_time - call_start_time) * 1000
                    
                    # Отримуємо реальне значення з FutureResult (якщо це Pyro4 async результат)
                    if hasattr(worker_result, 'value'):
                        actual_result = worker_result.value
                    else:
                        actual_result = worker_result
                    
                    # Зберігаємо результат
                    with lock:
                        worker_results[worker_idx] = actual_result
                        worker_times[worker_idx] = worker_elapsed_ms
                        worker_primes_count[worker_idx] = len(actual_result) if isinstance(actual_result, list) else 0
                    
                    thread_end_time = time.time()
                    total_thread_time = (thread_end_time - thread_start_time) * 1000
                    print("<<< Worker %d FINISHED at %.3f: Computation time %s, Total thread time %s (found %d primes)" % 
                          (worker_idx, thread_end_time, format_time(worker_elapsed_ms), format_time(total_thread_time), worker_primes_count[worker_idx]))
                except Exception as e:
                    print("ERROR in worker %d: %s" % (worker_idx, str(e)))
                    import traceback
                    traceback.print_exc()
                    with lock:
                        worker_results[worker_idx] = []
                        worker_times[worker_idx] = 0.0
            
            # Створюємо потоки для кожного воркера
            print("Creating and starting %d worker threads..." % len(workers_to_use))
            thread_creation_start = time.time()
            for i in range(len(workers_to_use)):
                # Розподіляємо залишок рівномірно між першими workers
                current_chunk_size = chunk_size + (1 if i < remainder else 0)
                chunk_start = current_start
                chunk_end = current_start + current_chunk_size - 1
                
                # Переконуємося, що не виходимо за межі
                if chunk_end > end:
                    chunk_end = end
                if chunk_start > end:
                    # Якщо початок вже за межами, пропускаємо цей воркер
                    break
                
                # Створюємо і запускаємо потік
                thread = threading.Thread(target=worker_thread, args=(i, chunk_start, chunk_end))
                thread.start()
                threads.append(thread)
                print("  Thread for Worker %d created and started" % i)
                
                current_start = chunk_end + 1
                
                # Якщо досягли кінця діапазону, зупиняємося
                if chunk_end >= end:
                    break
            
            thread_creation_end = time.time()
            print("All %d threads started in %s" % (len(threads), format_time((thread_creation_end - thread_creation_start) * 1000)))
            
            # Чекаємо завершення всіх потоків
            print("")
            print("Waiting for all workers to complete...")
            join_start_time = time.time()
            for i, thread in enumerate(threads):
                thread.join()
                join_end_time = time.time()
                print("  Worker %d thread joined (waited %s)" % (i, format_time((join_end_time - join_start_time) * 1000)))
                join_start_time = join_end_time
            
            # Збираємо результати
            for i in range(len(workers_to_use)):
                mapped[i] = worker_results[i] if worker_results[i] is not None else []
            
            # Reduce фаза: збираємо результати
            reduce_start_time = time.time()
            all_primes = self.myreduce(mapped)
            reduce_end_time = time.time()
            reduce_elapsed_ms = (reduce_end_time - reduce_start_time) * 1000
            
            parallel_end_time = time.time()
            parallel_elapsed_ms = (parallel_end_time - parallel_start_time) * 1000
            
            # Виводимо детальну статистику
            print("")
            print("=" * 70)
            print("PERFORMANCE SUMMARY - PARALLEL EXECUTION")
            print("=" * 70)
            print("Range: [%d, %d]" % (start, end))
            print("Total range size: %d" % (end - start + 1))
            print("Number of workers: %d" % self.num_workers_used)
            print("Algorithm: %s" % self.algorithm_used)
            print("Execution mode: PARALLEL (all workers run simultaneously)")
            print("")
            print("Individual worker execution times:")
            total_sequential_time = 0.0
            for i, wt in enumerate(worker_times):
                primes_found = worker_primes_count[i] if i < len(worker_primes_count) else 0
                print("  Worker %d: %s (found %d primes)" % (i, format_time(wt), primes_found))
                total_sequential_time += wt
            print("")
            print("Timing breakdown:")
            print("  Longest worker time: %s" % format_time(max(worker_times)))
            print("  Average worker time: %s" % format_time(sum(worker_times) / len(worker_times)))
            print("  Total sequential time (if run one by one): %s" % format_time(total_sequential_time))
            print("  Reduce phase time: %s" % format_time(reduce_elapsed_ms))
            print("  Total parallel execution time: %s" % format_time(parallel_elapsed_ms))
            print("")
            if len(worker_times) > 1:
                speedup = total_sequential_time / max(worker_times) if max(worker_times) > 0 else 1.0
                efficiency = speedup / len(worker_times) * 100
                time_saved = total_sequential_time - parallel_elapsed_ms
                percent_saved = (time_saved / total_sequential_time * 100) if total_sequential_time > 0 else 0
                
                print("Performance metrics:")
                print("  Speedup: %.3fx (sequential time / parallel time)" % speedup)
                print("  Efficiency: %.2f%% (speedup / number of workers)" % efficiency)
                print("")
                print("COMPARISON:")
                print("  If run sequentially (1 worker): ~%s" % format_time(total_sequential_time))
                print("  With %d workers in parallel: %s" % (len(worker_times), format_time(parallel_elapsed_ms)))
                print("  Time saved: %s (%.2f%%)" % (format_time(time_saved), percent_saved))
                print("")
                
                # Пояснення для малих діапазонів
                if parallel_elapsed_ms > total_sequential_time * 0.8:
                    print("NOTE: For small ranges, parallelization overhead (network communication,")
                    print("      thread synchronization) may outweigh computation benefits.")
                    print("      Try testing with larger ranges (10M+, 100M+) to see better speedup.")
                elif speedup < 1.5:
                    print("NOTE: Limited speedup observed. This may be due to:")
                    print("      - Small computation time relative to network overhead")
                    print("      - Workers competing for shared resources")
                    print("      - Try larger ranges for more significant speedup")
                else:
                    print("✓ Good parallelization achieved!")
            print("=" * 70)
            
            # Записуємо результат (all_primes вже список рядків)
            self.write_output(all_primes, parallel_elapsed_ms, worker_times)
            
            print("")
            print("Computation finished. Found %d primes" % len(all_primes))
            print("Total execution time: %s" % format_time(parallel_elapsed_ms))
            print("Job Finished")
        except Exception as e:
            print("ERROR in parallel algorithm: %s" % str(e))
            import traceback
            traceback.print_exc()
            # Забезпечуємо, що змінні встановлені навіть при помилці
            if not self.execution_mode:
                self.execution_mode = "PARALLEL"
            if not self.algorithm_used:
                self.algorithm_used = "UNKNOWN (error occurred)"
            raise

    @staticmethod
    @expose
    def find_primes_in_range(start_str, end_str):
        """
        Знаходить прості числа в заданому діапазоні.
        Виконується на worker node або послідовно.
        Використовує решето Ератосфена для малих діапазонів,
        перевірку кожного числа для великих діапазонів.
        Повертає кортеж: (список простих чисел, назва алгоритму)
        """
        start = int(start_str)
        end = int(end_str)
        
        print("Processing range [%d, %d]" % (start, end))
        
        # Межа для використання решета Ератосфена (10 мільйонів)
        # Решето ефективне для малих діапазонів через O(n) пам'яті
        SIEVE_LIMIT = 10000000
        
        # Визначаємо розмір діапазону
        range_size = end - start + 1
        
        # Для малих діапазонів використовуємо решето Ератосфена
        if end <= SIEVE_LIMIT:
            algorithm_name = "Sieve of Eratosthenes"
            print("-" * 60)
            print("ALGORITHM: Sieve of Eratosthenes")
            print("Reason: end (%d) <= SIEVE_LIMIT (%d)" % (end, SIEVE_LIMIT))
            print("Range size: %d" % range_size)
            print("Complexity: O(n log log n) time, O(n) memory")
            print("-" * 60)
            start_time = time.time()
            primes = Solver.sieve_of_eratosthenes(start, end)
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000
            print("Sieve of Eratosthenes execution time: %s" % format_time(elapsed_ms))
        else:
            # Для великих діапазонів використовуємо перевірку кожного числа
            algorithm_name = "Prime Checking (trial division)"
            print("-" * 60)
            print("ALGORITHM: Prime Checking (trial division)")
            print("Reason: end (%d) > SIEVE_LIMIT (%d)" % (end, SIEVE_LIMIT))
            print("Range size: %d" % range_size)
            print("Complexity: O(n√n) time, O(k) memory (k = number of primes)")
            print("-" * 60)
            start_time = time.time()
            primes = Solver.find_primes_by_checking(start, end)
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000
            print("Prime checking algorithm execution time: %s" % format_time(elapsed_ms))
        
        print("Found %d primes" % len(primes))
        # Зберігаємо назву алгоритму в першому елементі списку (якщо це воркер)
        # Для послідовного режиму це буде збережено в self.algorithm_used
        return primes

    @staticmethod
    @expose
    def sieve_of_eratosthenes(start, end):
        """
        Решето Ератосфена для пошуку простих чисел у діапазоні [start, end].
        Складність: O(n log log n) за часом, O(n) за пам'яттю.
        Ефективне для малих діапазонів.
        """
        if end < 2:
            return []
        if start > end:
            return []
        
        # Створюємо масив булевих значень розміром end + 1
        # is_prime[i] = True означає, що i є простим числом
        limit = end
        is_prime = [True] * (limit + 1)
        is_prime[0] = False
        is_prime[1] = False
        
        # Для кожного числа i від 2 до √limit
        sqrt_limit = int(math.sqrt(limit)) + 1
        for i in xrange(2, sqrt_limit):
            if is_prime[i]:
                # Позначаємо всі кратні i як непрості
                for j in xrange(i * i, limit + 1, i):
                    is_prime[j] = False
        
        # Збираємо всі прості числа у діапазоні [start, end]
        primes = []
        for num in xrange(max(2, start), end + 1):
            if is_prime[num]:
                primes.append(str(num))
        
        return primes
    
    @staticmethod
    def find_primes_by_checking(start, end):
        """
        Знаходить прості числа перевіркою кожного числа.
        Використовується для великих діапазонів.
        Складність: O(n√n) за часом, O(k) за пам'яттю (де k - кількість простих чисел).
        """
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
                print("Progress: %d%% (%d/%d)" % (progress, count, total))
        
        return primes
    
    @staticmethod
    @expose
    def is_prime(n):
        """
        Перевіряє, чи є число простим.
        Перевіряє ділення на числа від 2 до √n.
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
        Формат: 
        - перший рядок - початок діапазону
        - другий рядок - кінець діапазону
        - третій рядок (опціонально) - максимальна кількість workers (1, 2, або 3)
        """
        try:
            f = open(self.input_file_name, 'r')
            start = int(f.readline().strip())
            end = int(f.readline().strip())
            
            # Читаємо третій рядок (кількість workers), якщо він є
            third_line = f.readline().strip()
            max_workers = None
            if third_line:
                try:
                    max_workers = int(third_line)
                    if max_workers < 1:
                        max_workers = None
                    elif max_workers > 3:
                        max_workers = 3  # Обмежуємо максимум 3 workers
                    print("Requested workers: %d" % max_workers)
                except ValueError:
                    max_workers = None
            
            f.close()
            return start, end, max_workers
        except Exception as e:
            print("ERROR reading input file: %s" % str(e))
            import traceback
            traceback.print_exc()
            raise

    def write_output(self, output, execution_time_ms=None, worker_times=None):
        """
        Записує результати у файл з інформацією про використаний алгоритм та детальну статистику.
        """
        try:
            f = open(self.output_file_name, 'w')
            
            # Додаємо заголовок з інформацією про алгоритм
            f.write("=" * 70 + "\n")
            f.write("INFORMATION ABOUT COMPUTATION\n")
            f.write("=" * 70 + "\n")
            f.write("Execution Mode: %s\n" % (self.execution_mode if self.execution_mode else "UNKNOWN"))
            if self.execution_mode == "PARALLEL":
                f.write("Number of Workers Used: %d\n" % self.num_workers_used)
            f.write("Algorithm Used: %s\n" % (self.algorithm_used if self.algorithm_used else "UNKNOWN"))
            if execution_time_ms is not None:
                f.write("Total Execution Time: %s\n" % format_time(execution_time_ms))
            
            # Детальна інформація про воркерів (для паралельного режиму)
            if self.execution_mode == "PARALLEL" and worker_times:
                f.write("\n")
                f.write("PARALLEL EXECUTION DETAILS:\n")
                f.write("-" * 70 + "\n")
                total_sequential_time = sum(worker_times)
                f.write("Individual Worker Execution Times:\n")
                for i, wt in enumerate(worker_times):
                    f.write("  Worker %d: %s\n" % (i, format_time(wt)))
                f.write("\n")
                f.write("Performance Metrics:\n")
                f.write("  Longest worker time: %s\n" % format_time(max(worker_times)))
                f.write("  Average worker time: %s\n" % format_time(sum(worker_times) / len(worker_times)))
                f.write("  Total sequential time (if run one by one): %s\n" % format_time(total_sequential_time))
                f.write("  Total parallel execution time: %s\n" % format_time(execution_time_ms if execution_time_ms else 0))
                if len(worker_times) > 1:
                    speedup = total_sequential_time / max(worker_times) if max(worker_times) > 0 else 1.0
                    efficiency = speedup / len(worker_times) * 100
                    f.write("  Speedup: %.3fx\n" % speedup)
                    f.write("  Efficiency: %.2f%%\n" % efficiency)
                    f.write("\n")
                    f.write("COMPARISON:\n")
                    f.write("  Sequential execution (1 worker): ~%s\n" % format_time(total_sequential_time))
                    f.write("  Parallel execution (%d workers): %s\n" % (len(worker_times), format_time(execution_time_ms if execution_time_ms else 0)))
                    if execution_time_ms and total_sequential_time > 0:
                        time_saved = total_sequential_time - execution_time_ms
                        percent_saved = (time_saved / total_sequential_time) * 100
                        f.write("  Time saved: %s (%.2f%%)\n" % (format_time(time_saved), percent_saved))
            
            f.write("=" * 70 + "\n")
            f.write("\n")
            f.write("PRIME NUMBERS FOUND:\n")
            f.write("-" * 70 + "\n")
            
            # output вже список рядків
            if output and len(output) > 0:
                f.write(', '.join(output))
                f.write('\n')
                f.write("\n" + "-" * 70 + "\n")
                f.write("Total primes found: %d\n" % len(output))
            else:
                f.write('No primes found\n')
            f.write("=" * 70 + "\n")
            f.close()
            print("output done - file written to: %s" % self.output_file_name)
        except Exception as e:
            print("ERROR writing output: %s" % str(e))
            raise

