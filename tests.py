from arithmetic import add, subtract, multiply, divide

N = 3


def test_add():
    for x in range(2**N):
        for y in range(2**N):
            expected = x + y
            got = add(x,y,N)
            assert got == expected, f"{x} + {y}: expected {expected}, got {got}"
    print("add: all tests passed")



def test_sub():
    for x in range(2**N):
        for y in range(2**N):
            expected = x - y
            got = subtract(x, y, N)
            assert got == expected, f"{x} - {y}: expected {expected}, got {got}"
    print("sub: all tests passed")

def test_mult():
    for x in range(2**N):
        for y in range(2**N):
            expected = x * y
            got = multiply(x, y, N)
            assert got == expected, f"{x} * {y}: expected {expected}, got {got}"
    print("mult: all tests passed")

def test_div():
    for x in range(2**N):
        for y in range(1, 2**N):
            expected = (x // y, x % y)
            got = divide(x, y, N)
            assert got == expected, f"{x} / {y}: expected (q, r) = {expected}, got {got}"
    print("div: all tests passed")


if __name__ == "__main__":
    test_add()
    test_sub()
    test_mult()
    test_div()