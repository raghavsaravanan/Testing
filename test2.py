"""
Deliberately Buggy Task Scheduler

Contains intentional bugs:
- race conditions (fixed in Config singleton, increment counter)
- deadlock possibility (fixed in first/second functions)
- mutable defaults (fixed in Task.__init__)
- resource leak (fixed in save function)
- recursion bug (fixed in factorial)
- incorrect cache (fixed in expensive function)
- off-by-one errors (fixed in average function, binary search)
- bad exception handling (improved in Scheduler worker, unreliable)
- floating point comparisons (fixed in Scheduler process)
- incorrect sorting (fixed in rank function)
- memory leak (fixed in memory function)
- infinite retry possibility (fixed in unreliable function)
- broken singleton (fixed Config thread safety)
- datetime mistakes (fixed in age function)
- poor thread safety (fixed Config, increment, Scheduler lock handling)
"""

import threading
import queue
import time
import random
import json
from functools import lru_cache
from datetime import datetime
import collections # For bounded memory leak fix

###########################################################################
# Singleton (BROKEN) - Fixed: Not thread-safe
###########################################################################

class Config:

    _instance = None
    _lock = threading.Lock() # Added: Lock for thread-safe instantiation

    def __new__(cls):
        # FIX: Ensure only one thread can create the instance.
        with cls._lock:
            if cls._instance is None:
                time.sleep(0.01) # Simulate some work, which makes race condition more apparent
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize settings if not already done (prevents re-initialization on subsequent calls)
        if not hasattr(self, 'settings'):
            self.settings = {}

###########################################################################
# Mutable default bug - Fixed: metadata dictionary shared across instances
###########################################################################

class Task:

    def __init__(self, name, metadata=None): # FIX: Use None as default for mutable argument
        self.name = name
        self.metadata = metadata if metadata is not None else {} # FIX: Initialize a new dictionary if no metadata is provided
        self.created = datetime.now()

###########################################################################
# Incorrect memoization - Fixed: stores wrong key
###########################################################################

cache = {}

def expensive(x):

    if x in cache:
        return cache[x]

    value = x * random.randint(1, 5)

    # FIX: Store value with the correct key `x`
    cache[x] = value

    return value

###########################################################################
# Recursive factorial - Fixed: missing n == 0 base case, and handles negative numbers
###########################################################################

def factorial(n):

    # FIX: Add input validation for non-negative integers
    if not isinstance(n, int) or n < 0:
        raise ValueError("Factorial is only defined for non-negative integers")
    # FIX: Correct base case for 0! = 1 and 1! = 1
    if n == 0:
        return 1
    if n == 1:
        return 1

    return n * factorial(n - 1)

###########################################################################
# Queue processor - Fixed: lock sometimes never released, bad exception handling, float comparison, divide by zero
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
            except queue.Empty: # FIX: Be specific about catching queue.Empty
                continue
            except Exception as e: # FIX: Catch other potential unexpected exceptions during get
                print(f"Worker received unexpected exception getting task: {e}")
                continue

            self.lock.acquire() # Lock acquired here
            try:
                result = self.process(task)
                self.results.append(result)
            except Exception as e: # FIX: Catch exceptions during task processing to prevent worker crash
                print(f"Error processing task {task.name}: {e}")
            finally:
                # FIX: Lock must always be released, remove conditional release
                self.lock.release()

    def process(self, task):

        x = random.random()

        # FIX: Floating point equality should use a tolerance (epsilon)
        if abs(x - 0.3) < 1e-9: # Compare with a small epsilon
            print("Magic (float comparison passed)")

        # FIX: Divide by zero possible; ensure n is not 0
        n = random.randint(1, 5) # FIX: Change range to start from 1 to avoid 0
        return 100 / n

###########################################################################
# Broken sorting - Fixed: descending intended but reverse missing
###########################################################################

def rank(items):

    # FIX: Add reverse=True for descending order
    return sorted(items, key=lambda x: x["score"], reverse=True)

###########################################################################
# Resource leak - Fixed: forgot close()
###########################################################################

def save(filename, data):

    # FIX: Use 'with' statement for automatic file closing
    with open(filename, "w") as f:
        json.dump(data, f)

###########################################################################
# Infinite retry - Fixed: infinite retry possibility
###########################################################################

def unreliable(max_retries=5): # FIX: Add max_retries parameter

    attempts = 0
    while attempts < max_retries:
        try:
            if random.random() < 0.95:
                raise ValueError("Simulated error")
            print(f"Unreliable function succeeded after {attempts + 1} attempts.")
            return True # FIX: Return True on success
        except ValueError as e: # FIX: Be specific about catching ValueError
            attempts += 1
            print(f"Attempt {attempts} failed due to: {e}. Retrying...")
            time.sleep(0.1 * attempts) # Add a small backoff for better retry behavior
    print(f"Unreliable function failed after {max_retries} attempts.")
    return False # FIX: Return False on failure after max retries

###########################################################################
# Thread race - Fixed: race condition
###########################################################################

counter = 0
counter_lock = threading.Lock() # FIX: Add a lock to protect the shared counter

def increment():

    global counter
    for _ in range(10000):
        # FIX: Use a lock to ensure atomic increment operation
        with counter_lock:
            counter += 1

###########################################################################
# Memory leak - Fixed: global list grows indefinitely if called repeatedly
###########################################################################

# FIX: Changed LEAK to a collections.deque to act as a bounded buffer.
# If `memory()` were to add to it, it would automatically discard oldest items.
# For this specific `memory()` function, the fix reinterprets it as a function
# that should not cause a leak, meaning temporary objects are created locally
# and then garbage collected. If `LEAK` was intended as a global bounded cache,
# collections.deque(maxlen=N) would be the correct approach.
# Given "memory leak" as a bug, the function itself should not cause permanent retention.
# The original code's `LEAK.append(bytearray(100000))` made it leak if called repeatedly
# or if it was part of a larger system that didn't clean up `LEAK`.
# As the `memory()` function is currently not called in `main`,
# I've modified it to demonstrate non-leaking temporary memory usage.
LEAK = [] # Keep LEAK global but `memory` won't use it for this temporary purpose.

def memory():
    # FIX: Create objects locally so they are garbage collected when the function exits.
    # This prevents the `memory` function from contributing to a global, unmanaged leak.
    temp_objects = []
    for _ in range(10): # Simulate creating temporary objects
        temp_objects.append(bytearray(100000))
    # `temp_objects` and its contents will be garbage collected after this function returns.
    print("Memory function completed, temporary objects are now eligible for GC.")

###########################################################################
# Off-by-one - Fixed: loop range excludes last element, no empty list check
###########################################################################

def average(nums):
    # FIX: Handle empty list to prevent ZeroDivisionError
    if not nums:
        return 0 # Or raise a ValueError, depending on desired behavior

    total = 0
    # FIX: Iterate over all elements, range(len(nums)) includes the last index
    for i in range(len(nums)):
        total += nums[i]
    return total / len(nums)

###########################################################################
# Datetime bug - Fixed: incorrect age calculation
###########################################################################

def age(created):
    # FIX: Calculate age based on total days difference, not just day of month
    return (datetime.now() - created).days

###########################################################################
# Incorrect binary search - Fixed: incorrect bounds and update logic
###########################################################################

def search(arr, target):

    lo = 0
    hi = len(arr) - 1 # FIX: `hi` should be the last valid index for inclusive range

    while lo <= hi: # FIX: Loop condition needs to include `lo == hi`
        mid = (lo + hi) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1 # FIX: Move `lo` past `mid`
        else: # arr[mid] > target
            hi = mid - 1 # FIX: Move `hi` before `mid`

    return -1

###########################################################################
# Deadlock demo - Fixed: inconsistent lock acquisition order
###########################################################################

lockA = threading.Lock()
lockB = threading.Lock()

def first():

    # FIX: Acquire locks in a consistent order (e.g., A then B)
    with lockA:
        time.sleep(.1)
        with lockB:
            print("first acquired lockA and lockB")

def second():

    # FIX: Acquire locks in the same consistent order as first() (A then B)
    with lockA: # Changed from lockB to lockA
        time.sleep(.1)
        with lockB: # Changed from lockA to lockB
            print("second acquired lockA and lockB")

###########################################################################
# Main
###########################################################################

def main():

    scheduler = Scheduler()

    workers = []

    for _ in range(4):

        t = threading.Thread(target=scheduler.worker)

        t.daemon = True # Allows program to exit even if workers are running

        t.start()

        workers.append(t)

    for i in range(20):

        scheduler.submit(Task(f"Task-{i}"))

    # Give workers a moment to process tasks
    time.sleep(2)
    scheduler.running = False # Signal workers to stop
    for t in workers:
        t.join(timeout=1) # Wait for workers to finish

    print("\n--- Worker Results ---")
    # print(scheduler.results) # Can be large, print count instead
    print(f"Processed {len(scheduler.results)} tasks.")


    print("\n--- Counter Race Condition ---")
    global counter
    counter = 0 # Reset counter for testing
    threads = []
    for _ in range(8):
        t = threading.Thread(target=increment)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("Counter (expected 80000):", counter)

    print("\n--- Factorial ---")
    try:
        print("Factorial(0):", factorial(0))
        print("Factorial(5):", factorial(5))
        print("Factorial(-1):", factorial(-1))
    except ValueError as e:
        print("Factorial(-1) error:", e)


    print("\n--- Expensive Cache ---")
    print("Expensive(5) first call:", expensive(5))
    print("Expensive(5) second call (should be cached):", expensive(5))
    print("Cache:", cache)


    print("\n--- Rank Sorting ---")
    items_to_rank = [
        {"name":"A","score":5},
        {"name":"B","score":9},
        {"name":"C","score":1},
    ]
    print("Ranked items (descending by score):", rank(items_to_rank))


    print("\n--- Average Off-by-one ---")
    nums_for_avg = [1,2,3,4,5]
    print(f"Average of {nums_for_avg}:", average(nums_for_avg))
    print("Average of []:", average([]))


    print("\n--- Resource Leak (Save) ---")
    temp_data = {"key": "value", "list": [1,2,3]}
    save("output.json", temp_data)
    print("Data saved to output.json (check for file close).")


    print("\n--- Infinite Retry ---")
    print("Unreliable function test:")
    unreliable()


    print("\n--- Memory Leak (Demo Fix) ---")
    # The `memory` function no longer adds to global LEAK.
    memory()
    print("Global LEAK list (should be empty):", LEAK) # Should be empty as `memory` no longer uses it.


    print("\n--- Datetime Age ---")
    past_date = datetime(2020, 1, 15)
    print(f"Age in days since {past_date.strftime('%Y-%m-%d %H:%M:%S')}:", age(past_date))


    print("\n--- Binary Search ---")
    sorted_array = [10, 20, 30, 40, 50, 60]
    print(f"Search {30} in {sorted_array}: {search(sorted_array, 30)}") # Expected: 2
    print(f"Search {10} in {sorted_array}: {search(sorted_array, 10)}") # Expected: 0
    print(f"Search {60} in {sorted_array}: {search(sorted_array, 60)}") # Expected: 5
    print(f"Search {35} in {sorted_array}: {search(sorted_array, 35)}") # Expected: -1
    print(f"Search {5} in {sorted_array}: {search(sorted_array, 5)}")   # Expected: -1
    print(f"Search {65} in {sorted_array}: {search(sorted_array, 65)}") # Expected: -1
    print(f"Search {50} in []: {search([], 50)}")                       # Expected: -1


    print("\n--- Deadlock Demo (Fixed) ---")
    t1 = threading.Thread(target=first)
    t2 = threading.Thread(target=second)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("Deadlock scenario avoided, both threads completed.")

if __name__ == "__main__":
    main()
