"""
Ground-truth correctness tests for test2.py.

The agent is allowed to edit test2.py to make these pass; it must never
edit this file. Covers the bugs that are reliably assertable - several of
the file's other intentional bugs (floating-point-equality print, the
bounded memory demo, the infinite-retry loop) are left to manual review
since they aren't cleanly testable with a simple pass/fail assertion.
"""

import threading

import test2
from test2 import Config, Task, expensive, factorial, rank, average, search, increment, first, second


def test_singleton_returns_same_instance():
    a = Config()
    b = Config()
    assert a is b


def test_singleton_is_thread_safe():
    test2.Config._instance = None
    instances = []

    def make():
        instances.append(Config())

    threads = [threading.Thread(target=make) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(set(id(i) for i in instances)) == 1


def test_task_metadata_defaults_are_isolated():
    t1 = Task("a")
    t2 = Task("b")
    t1.metadata["x"] = 1
    assert "x" not in t2.metadata


def test_expensive_is_memoized_per_input():
    assert expensive(5) == expensive(5)


def test_factorial_base_case():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120


def test_rank_is_descending():
    items = [{"name": "A", "score": 5}, {"name": "B", "score": 9}, {"name": "C", "score": 1}]
    ranked = rank(items)
    assert [i["score"] for i in ranked] == [9, 5, 1]


def test_average_includes_all_elements():
    assert average([1, 2, 3, 4, 5]) == 3.0


def test_search_finds_target():
    arr = [1, 3, 5, 7, 9, 11]
    for i, val in enumerate(arr):
        assert search(arr, val) == i
    assert search(arr, 4) == -1


def test_increment_has_no_race_condition():
    test2.counter = 0
    threads = [threading.Thread(target=increment) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert test2.counter == 200000


def test_no_deadlock_between_first_and_second():
    t1 = threading.Thread(target=first)
    t2 = threading.Thread(target=second)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()
    t1.join(timeout=3)
    t2.join(timeout=3)
    assert not t1.is_alive(), "possible deadlock: 'first' did not finish"
    assert not t2.is_alive(), "possible deadlock: 'second' did not finish"
