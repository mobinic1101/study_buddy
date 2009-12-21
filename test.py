import random

numbers = [random.randint(0, 10) for _ in range(10)]
print(numbers)


def sort(numbers):
    numbers2 = numbers.copy()
    sorted_numbers = []

    x = len(numbers2)
    for i in range(x):
        min_number = min(numbers2)
        sorted_numbers.append(min_number)
        numbers2.remove(min_number)

    return sorted_numbers


res = sort(numbers)
print(res)
