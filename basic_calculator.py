"""
This module provides basic calculator functionalities such as addition, subtraction, multiplication, and division.
"""

def add(x, y):
    """
    Adds two numbers together.

    Parameters:
    x (int): The first number.
    y (int): The second number.

    Returns:
    int: The sum of x and y.
    """
    return x + y

def subtract(x, y):
    """
    Subtracts two numbers.

    Parameters:
    x (int): The first number.
    y (int): The second number.

    Returns:
    int: The difference between x and y.
    """
    return x - y

def multiply(x, y):
    """
    Multiply two numbers.

    Args:
        x (int): The first number.
        y (int): The second number.

    Returns:
        int: The product of x and y.
    """
    return x * y

def divide(x, y):
    """
    Divides two numbers.

    Args:
        x (float): The dividend.
        y (float): The divisor.

    Returns:
        float: The quotient of x divided by y.

    Raises:
        ZeroDivisionError: If y is equal to zero.

    """
    if y == 0:
        return "Error: Division by zero is not allowed"
    return x / y

def calculator():
    """
    This function allows the user to perform basic arithmetic operations.
    The user is prompted to select an operation and enter two numbers.
    The function then performs the selected operation on the two numbers and displays the result.
    """

    print("Select operation:")
    print("1.Add")
    print("2.Subtract")
    print("3.Multiply")
    print("4.Divide")

    choice = input("Enter choice(1/2/3/4): ")

    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    if choice == '1':
        print(num1, "+", num2, "=", add(num1, num2))

    elif choice == '2':
        print(num1, "-", num2, "=", subtract(num1, num2))

    elif choice == '3':
        print(num1, "*", num2, "=", multiply(num1, num2))

    elif choice == '5':
        print(num1, "/", num2, "=", divide(num1, num2))

    else:
        print("Invalid input")

calculator()
