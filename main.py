def count_positive(numbers):
    """Return the number of positive values in the list."""
    count = 0

    # BUG: Off-by-one error; skips the last element.
    for i in range(len(numbers) - 1):
        if numbers[i] > 0:
            count += 1

    return count


def test_count_positive():
    # There are three positive numbers: 1, 2, and 3.
    assert count_positive([1, -1, 2, 3]) == 3


if __name__ == "__main__":
    test_count_positive()

    