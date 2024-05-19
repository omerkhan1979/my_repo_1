from basic_calculator import add, subtract, multiply, divide

def test_calculator():
    """
    This function tests the basic arithmetic operations of a calculator.

    It includes tests for addition, subtraction, multiplication, division,
    and division by zero.

    Returns:
        None
    """
    # Test addition
    assert add(2, 3) == 5
    assert add(-5, 10) == 5
    assert add(0, 0) == 0

    # Test subtraction
    assert subtract(5, 2) == 3
    assert subtract(10, -5) == 15
    assert subtract(0, 0) == 0

    # Test multiplication
    assert multiply(2, 3) == 6
    assert multiply(-5, 10) == -50
    assert multiply(0, 5) == 0

    # Test division
    assert divide(10, 2) == 5
    assert divide(-50, 10) == -5
    assert divide(0, 5) == 0

    # Test division by zero
    assert divide(10, 0) == "Error: Division by zero is not allowed"

test_calculator()
