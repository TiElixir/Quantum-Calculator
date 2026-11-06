from arithmetic import add

N = 4


def test_add():
    for x in range(2**N):
        for y in range(2**N):
            expected = x + y
            got = add(x,y,N)
            assert got == expected, f"{x} + {y}: expected {expected}, got {got}"
    print("add: all tests passed")


if __name__ == "__main__":
    test_add()