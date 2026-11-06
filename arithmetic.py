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





def run(qc):
    counts = AerSimulator().run(qc, shots=1).result().get_counts()
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