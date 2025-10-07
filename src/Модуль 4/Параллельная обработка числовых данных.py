import concurrent.futures
import json
import multiprocessing
import random
import time


def generate_data(n: int) -> list[int]:
    return [random.randint(1, 1000) for _ in range(n)]


def process_number(n: int) -> int:
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res


# Вариант А: Ипользование пула потоков с concurrent.futures.
def thread_pool_executor(nums: list[int]) -> None:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_number, nums)


# Вариант Б: Использование multiprocessing.Pool с пулом процессов, равным количеству CPU.
def multiprocessing_pool(nums: list[int]) -> None:
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(process_number, nums)


# Вариант В: Создание отдельных процессов с использованием multiprocessing.Process
# и очередей (multiprocessing.Queue) для передачи данных.
def worker_with_queue(
    input_q: multiprocessing.Queue, output_q: multiprocessing.Queue
) -> None:
    while True:
        num = input_q.get()
        if num is None:  # sentinel — сигнал завершения
            break
        result = process_number(num)
        output_q.put(result)


def multiprocessing_processes(nums: list[int]) -> None:
    cpu_count = multiprocessing.cpu_count()
    input_q = multiprocessing.Queue()
    output_q = multiprocessing.Queue()

    # Создаем и запускаем процессы
    processes = []
    for _ in range(cpu_count):
        p = multiprocessing.Process(target=worker_with_queue, args=(input_q, output_q))
        p.start()
        processes.append(p)

    # Кладем все данные в очередь
    for num in nums:
        input_q.put(num)

    # Кладем sentinel для каждого процесса
    for _ in range(cpu_count):
        input_q.put(None)

    # Собираем результаты
    results = []
    for _ in nums:
        results.append(output_q.get())

    # Дожидаемся завершения всех процессов
    for p in processes:
        p.join()


# Однопоточный (однопроцессный) вариант.
def single_thread(nums: list[int]) -> None:
    for num in nums:
        process_number(num)


def main():
    sizes = [100, 1000, 5000, 10000, 20000]
    methods = [
        ("SingleThread", single_thread),
        ("ThreadPoolExecutor", thread_pool_executor),
        ("MultiprocessingPool", multiprocessing_pool),
        ("MultiprocessingProcesses", multiprocessing_processes),
    ]

    results = []
    for n in sizes:
        nums = generate_data(n)
        for method_name, func in methods:
            start = time.perf_counter()
            func(nums)
            end = time.perf_counter() - start
            results.append({"n": n, "method": method_name, "time": end})

    with open("./results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)


if __name__ == "__main__":
    main()
