import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "bubble_sort",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "bubble_sort.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
bubble_sort = _mod.bubble_sort


def test_bubble_sort_basic():
    assert bubble_sort([3, 1, 2]) == [1, 2, 3]


def test_bubble_sort_already_sorted():
    assert bubble_sort([1, 2, 3]) == [1, 2, 3]


def test_bubble_sort_reverse():
    assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]


def test_bubble_sort_single():
    assert bubble_sort([42]) == [42]


def test_bubble_sort_empty():
    assert bubble_sort([]) == []


def test_bubble_sort_duplicates():
    assert bubble_sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]


def test_bubble_sort_does_not_modify_input():
    original = [3, 1, 2]
    bubble_sort(original)
    assert original == [3, 1, 2]
