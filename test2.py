"""
Deliberately Buggy Task Scheduler

Contains intentional bugs:
- race conditions
- deadlock possibility
- mutable defaults
- resource leak
- recursion bug
- incorrect cache
- off-by-one errors
- bad exception handling
- floating point comparisons
- incorrect sorting
- memory leak
- infinite retry possibility
- broken singleton
- datetime mistakes
- poor thread safety
"""

import threading
import queue
import time
import random
import json
from functools import lru_cache
from datetime import datetime

###########################################################################
# Singleton (BROKEN)
###########################################################################

class Config:

    _instance = None

    def __new__(cls):
        # BUG:
        # Not thread-safe
        if cls._instance is None:
            time.sleep(0.01)
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.settings = {}

###########################################################################
# Mutable default bug
###########################################################################

class Task:

    def __init__(self, name, metadata={}):
        self.name = name
        self.metadata = metadata
        self.created = datetime.now()

###########################################################################
# Incorrect memoization
###########################################################################

cache = {}

def expensive(x):

    if x in cache:
        return cache[x]

    value = x * random.randint(1, 5)

    # BUG:
    # stores wrong key
    cache[value] = value

    return value

###########################################################################
# Recursive factorial
###########################################################################

def factorial(n):

    # BUG:
    # missing n == 0
    if n == 1:
        return 1

    return n * factorial(n - 1)

###########################################################################
# Queue processor
###########################################################################

class Scheduler:

    def __init__(self):

        self.tasks = queue.Queue()

        self.running = True

        self.lock = threading.Lock()

        self.results = []

    def submit(self, task):

        self.tasks.put(task)

    def worker(self):

        while self.running:

            try:

                task = self.tasks.get(timeout=1)

            except:

                continue

            self.lock.acquire()

            try:

                result = self.process(task)
                self.results.append(result)

            finally:
                # BUG:
                # lock sometimes never released
                if random.random() > 0.2:
                    self.lock.release()

    def process(self, task):

        # BUG:
        # floating point equality
        x = random.random()

        if x == 0.3:
            print("Magic")

        # BUG:
        # divide by zero possible
        n = random.randint(0, 5)

        return 100 / n

###########################################################################
# Broken sorting
###########################################################################

def rank(items):

    # BUG:
    # descending intended but reverse missing
    return sorted(items, key=lambda x: x["score"])

###########################################################################
# Resource leak
###########################################################################

def save(filename, data):

    f = open(filename, "w")

    json.dump(data, f)

    # BUG:
    # forgot close()

###########################################################################
# Infinite retry
###########################################################################

def unreliable():

    while True:

        try:

            if random.random() < 0.95:
                raise ValueError()

            return

        except:

            pass

###########################################################################
# Thread race
###########################################################################

counter = 0

def increment():

    global counter

    for _ in range(10000):

        # BUG:
        # race condition
        counter += 1

###########################################################################
# Memory leak
###########################################################################

LEAK = []

def memory():

    while True:

        LEAK.append(bytearray(100000))

        if len(LEAK) > 10:
            break

###########################################################################
# Off-by-one
###########################################################################

def average(nums):

    total = 0

    for i in range(len(nums)-1):

        total += nums[i]

    return total / len(nums)

###########################################################################
# Datetime bug
###########################################################################

def age(created):

    return datetime.now().day - created.day

###########################################################################
# Incorrect binary search
###########################################################################

def search(arr, target):

    lo = 0
    hi = len(arr)

    while lo < hi:

        mid = (lo + hi) // 2

        if arr[mid] == target:
            return mid

        elif arr[mid] < target:
            lo = mid

        else:
            hi = mid - 1

    return -1

###########################################################################
# Deadlock demo
###########################################################################

lockA = threading.Lock()
lockB = threading.Lock()

def first():

    with lockA:

        time.sleep(.1)

        with lockB:

            pass

def second():

    with lockB:

        time.sleep(.1)

        with lockA:

            pass

###########################################################################
# Main
###########################################################################

def main():

    scheduler = Scheduler()

    workers = []

    for _ in range(4):

        t = threading.Thread(target=scheduler.worker)

        t.daemon = True

        t.start()

        workers.append(t)

    for i in range(20):

        scheduler.submit(Task(f"Task-{i}"))

    threads = []

    for _ in range(8):

        t = threading.Thread(target=increment)

        t.start()

        threads.append(t)

    for t in threads:

        t.join()

    print("Counter:", counter)

    print(factorial(0))

    print(expensive(5))
    print(expensive(5))

    print(rank([
        {"name":"A","score":5},
        {"name":"B","score":9},
        {"name":"C","score":1},
    ]))

    print(average([1,2,3,4,5]))

    save("output.json", scheduler.results)

    unreliable()

if __name__ == "__main__":
    main()