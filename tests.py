from arithmetic import add, subtract, multiply

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


if __name__ == "__main__":
    test_add()
    test_sub()
    test_mult()