def add_numbers(a, b):
    sum = a + b  
    return sum


def divide(a, b):
    return a / b 


def unused_function(): 
    print("This function is never called")


if __name__ == "__main__":
    print(add_numbers(5, "10"))  
    print(divide(10, 0))  
