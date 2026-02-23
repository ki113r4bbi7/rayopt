def bubble_sort(arr):
    """Sort a list in ascending order using the bubble sort algorithm.

    Creates a sorted copy without modifying the original list.

    Args:
        arr (list): The list of comparable elements to sort.

    Returns:
        list: A new list containing the same elements in ascending order.

    Examples:
        >>> bubble_sort([3, 1, 2])
        [1, 2, 3]
        >>> bubble_sort([])
        []
    """
    result = list(arr)
    n = len(result)
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result
