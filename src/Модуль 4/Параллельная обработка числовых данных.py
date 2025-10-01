import concurrent.futures
import json
import math
import multiprocessing
import random
import time


def generate_data(n: int) -> list[int]:
    return [random.randint(1, 1000) for _ in range(n)]


def process_number(n: int) -> int:
    return math.factorial(n)


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
def worker(nums: list[int], output: multiprocessing.Queue) -> None:
    for num in nums:
        output.put(num)


def multiprocessing_processes(nums: list[int]) -> None:
    output = multiprocessing.Queue()
    chunk_size = len(nums) // multiprocessing.cpu_count()
    processes = []

    for i in range(multiprocessing.cpu_count()):
        chunk = nums[i * chunk_size : (i + 1) * chunk_size]
        process = multiprocessing.Process(target=worker, args=(chunk, output))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


# Однопоточный (однопроцессный) вариант.
def single_thread(nums: list[int]) -> None:
    for num in nums:
        process_number(num)


def main():
    nums = generate_data(300)
    results = []

    for method_name, func in [
        ("SingleThread", single_thread),
        ("ThreadPoolExecutor", thread_pool_executor),
        ("MultiprocessingPool", multiprocessing_pool),
        ("MultiprocessingProcesses", multiprocessing_processes),
    ]:
        start_time = time.time()
        func(nums)
        end_time = time.time() - start_time
        results.append({"method": method_name, "time": end_time})

    with open("./results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)


if __name__ == "__main__":
    main()
