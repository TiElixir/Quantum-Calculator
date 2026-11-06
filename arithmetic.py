from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from gates import full_adder


def load(qc, reg, value):
    for i in range(len(reg)):
        if (value >> i) & 1:
            qc.x(reg[i])


def build_adder(x, y, n):
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n, "b")
    s = QuantumRegister(n, "s")
    c = QuantumRegister(n + 1, "c")
    out = ClassicalRegister(n + 1, "out")
    qc = QuantumCircuit(a, b, s, c, out)

    load(qc, a, x)
    load(qc, b, y)

    for i in range(n):
        full_adder(qc, a[i], b[i], c[i], s[i], c[i + 1])

    for i in range(n):
        qc.measure(s[i], out[i])
    qc.measure(c[n], out[n])

    return qc

def build_subtractor(x, y, n):
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n, "b")
    s = QuantumRegister(n, "s")
    c = QuantumRegister(n + 1, "c")
    out = ClassicalRegister(n + 1, "out")
    qc = QuantumCircuit(a, b, s, c, out)

    load(qc, a, x)
    load(qc, b, y)

    for i in range(n):
        qc.x(b[i])
    qc.x(c[0])

    for i in range(n):
        full_adder(qc, a[i], b[i], c[i], s[i], c[i + 1])

    for i in range(n):
        qc.measure(s[i], out[i])
    qc.measure(c[n], out[n])

    return qc


def build_multiplier(x, y, n):
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n, "b")
    z = QuantumRegister(1, "zero")          # stays 0, used for padding
    out = ClassicalRegister(2 * n, "out")
    qc = QuantumCircuit(a, b, z, out)

    load(qc, a, x)
    load(qc, b, y)

    
    pps = []
    for i in range(n):
        pp = QuantumRegister(n, f"pp{i}")
        qc.add_register(pp)
        for j in range(n):
            qc.ccx(a[j], b[i], pp[j])
        pps.append(list(pp))

    
    acc = pps[0]
    for i in range(1, n):
        hi = acc[i:]                         
        row = pps[i]
        m = max(len(hi), len(row))
        hi = hi + [z[0]] * (m - len(hi))     
        row = row + [z[0]] * (m - len(row))
        acc = acc[:i] + ripple_add(qc, hi, row, f"r{i}")

    for k in range(2 * n):
        qc.measure(acc[k], out[k])
    return qc


def run(qc, method="automatic"):
    counts = AerSimulator(method=method).run(qc, shots=1).result().get_counts()
    bitstring = next(iter(counts))
    return int(bitstring, 2)


def add(x, y, n=3):
    return run(build_adder(x, y, n))

def subtract(x, y, n=3):
    raw = run(build_subtractor(x, y, n))
    carry = raw >> n
    s_bits = raw & (2**n - 1)
    if carry == 1:
        return s_bits
    return s_bits - 2**n
def ripple_add(qc, xs, ys, name):
    m = len(xs)
    s = QuantumRegister(m, name + "_s")
    c = QuantumRegister(m + 1, name + "_c")
    qc.add_register(s, c)
    for i in range(m):
        full_adder(qc, xs[i], ys[i], c[i], s[i], c[i + 1])
    return list(s) + [c[m]]
def multiply(x, y, n=4):
    return run(build_multiplier(x, y, n), method="matrix_product_state")