import sys
from arithmetic import add, subtract, multiply, divide

N = 3
MAX = 2**N - 1


def calculate(x, op, y):
    if not (0 <= x <= MAX and 0 <= y <= MAX):
        raise ValueError(f"inputs must be between 0 and {MAX}")
    if op == "+":
        return add(x, y, N)
    if op == "-":
        return subtract(x, y, N)
    if op in ("*", "x"):
        return multiply(x, y, N)
    if op == "/":
        q, r = divide(x, y, N)
        return f"{q} remainder {r}"
    raise ValueError(f"unknown operator '{op}' (use + - * /)")


def parse(line):
    parts = line.split()
    if len(parts) != 3:
        raise ValueError("format: <number> <op> <number>, e.g. 7 * 3")
    return int(parts[0]), parts[1], int(parts[2])


def main():
    # one-shot: python calculator.py 7 / 3
    if len(sys.argv) == 4:
        try:
            x, op, y = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
            print(calculate(x, op, y))
        except ZeroDivisionError:
            print("error: division by zero")
        except ValueError as e:
            print(f"error: {e}")
        return

    # interactive mode
    print(f"Quantum calculator (integers 0-{MAX}). Type e.g. 7 * 3, or q to quit.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.lower() in ("q", "quit", "exit"):
            break
        try:
            x, op, y = parse(line)
            print(calculate(x, op, y))
        except ZeroDivisionError:
            print("error: division by zero")
        except ValueError as e:
            print(f"error: {e}")


if __name__ == "__main__":
    main()