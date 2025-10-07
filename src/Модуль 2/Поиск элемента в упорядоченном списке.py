from typing import List


def search_in_sorted_list(sorted_list: List[int], number: int) -> bool:
    left, right = 0, len(sorted_list) - 1

    while left <= right:
        mid = (left + right) // 2
        if sorted_list[mid] == number:
            return True
        elif sorted_list[mid] < number:
            left = mid + 1
        else:
            right = mid - 1

    return False


sorted_list = [1, 2, 3, 45, 356, 569, 600, 705, 923]

print(search_in_sorted_list(sorted_list, 45))  # True
print(search_in_sorted_list(sorted_list, 100))  # False

print(search_in_sorted_list([], 10))  # False
print(search_in_sorted_list(sorted_list, 1))  # True
print(search_in_sorted_list(sorted_list, 923))  # True
print(search_in_sorted_list(sorted_list, 0))  # False
print(search_in_sorted_list(sorted_list, 1000))  # False

duplicates = [1, 2, 2, 2, 3, 4, 5]
print(search_in_sorted_list(duplicates, 2))  # True
print(search_in_sorted_list(duplicates, 6))  # False
