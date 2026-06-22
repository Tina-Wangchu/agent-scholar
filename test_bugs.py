def divide(a, b):
    return a / b


def process_list(items):
    result = []
    for i in range(len(items)):
        item = items[i]
        if len(item) > 5:
            result.append(item)
    return result   

print (divide(10, 0))
print(process_list(["hello", "world", "hi", "python"]))
