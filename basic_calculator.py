"""
This module provides basic calculator functionalities such as addition,
subtraction, multiplication, and division.
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

def calculator(choice, num1, num2):
    """
    This function allows the user to perform basic arithmetic operations.
    The user is prompted to select an operation and enter two numbers.
    The function then performs the selected operation on the two numbers and displays the result.
    """

    if choice == '1':
        return add(num1, num2)

    if choice == '2':
        return subtract(num1, num2)

    if choice == '3':
        return multiply(num1, num2)

    if choice == '5':
        return divide(num1, num2)

    return "Invalid input"

# Call calculator with example arguments
calculator('1', 2, 3)
