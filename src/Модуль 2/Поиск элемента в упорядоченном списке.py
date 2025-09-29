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
