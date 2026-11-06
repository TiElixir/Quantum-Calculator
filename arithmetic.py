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

def build_divider(x, y, n):
    m = n + 1
    a = QuantumRegister(n, "a")        
    d = QuantumRegister(m, "d")        
    z = QuantumRegister(1, "zero")     
    qout = ClassicalRegister(n, "q")
    rout = ClassicalRegister(n, "r")
    qc = QuantumCircuit(a, d, z, qout, rout)

    load(qc, a, x)
    load(qc, d, y)

    r = [z[0]] * m
    qbits = [None] * n

    for step in range(n):
        bit = a[n - 1 - step]          
        shifted = [bit] + r[:m - 1]   
        diff, k = ripple_sub(qc, shifted, list(d), f"s{step}")
        r = mux(qc, k, diff, shifted, f"s{step}")
        qbits[n - 1 - step] = k        

    for i in range(n):
        qc.measure(qbits[i], qout[i])
        qc.measure(r[i], rout[i])
    return qc





def run(qc, method="automatic"):
    counts = AerSimulator(method=method).run(qc, shots=1).result().get_counts()
    bitstring = next(iter(counts)).replace(" ", "")
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

def ripple_sub(qc, xs, ys, name):
    m = len(xs)
    s = QuantumRegister(m, name + "_s")
    c = QuantumRegister(m + 1, name + "_c")
    qc.add_register(s, c)

    qc.x(c[0])
    for q in ys:
        qc.x(q)
    for i in range(m):
        full_adder(qc, xs[i], ys[i], c[i], s[i], c[i + 1])
    for q in ys:
        qc.x(q)

    return list(s), c[m]

def mux(qc, k, diff, old, name):
    m = len(diff)
    res = QuantumRegister(m, name + "_m")
    qc.add_register(res)
    for i in range(m):
        qc.ccx(k, diff[i], res[i])      
    qc.x(k)                             
    for i in range(m):
        qc.ccx(k, old[i], res[i])       
    qc.x(k)                             
    return list(res)


def multiply(x, y, n=4):
    return run(build_multiplier(x, y, n), method="matrix_product_state")

def divide(x, y, n=3):
    if y == 0:
        raise ZeroDivisionError("division by zero")
    qc = build_divider(x, y, n)
    raw = run(qc, method="matrix_product_state")
    r = raw >> n             
    q = raw & (2**n - 1)
    return q, r

def try_subtract(rv, dv, n=3):
    m = n + 1
    r = QuantumRegister(m, "r")
    d = QuantumRegister(m, "d")
    out = ClassicalRegister(m + 1, "out")
    qc = QuantumCircuit(r, d, out)
    load(qc, r, rv)
    load(qc, d, dv)

    diff, carry = ripple_sub(qc, list(r), list(d), "t")
    for i in range(m):
        qc.measure(diff[i], out[i])
    qc.measure(carry, out[m])

    raw = run(qc, method="matrix_product_state")
    return raw >> m, raw & (2**m - 1)      # (carry, difference bits)

def try_mux(kv, dv, ov, m=4):
    k = QuantumRegister(1, "k")
    d = QuantumRegister(m, "d")
    o = QuantumRegister(m, "o")
    out = ClassicalRegister(m, "out")
    qc = QuantumCircuit(k, d, o, out)
    if kv:
        qc.x(k[0])
    load(qc, d, dv)
    load(qc, o, ov)
    res = mux(qc, k[0], list(d), list(o), "t")
    for i in range(m):
        qc.measure(res[i], out[i])
    return run(qc, method="matrix_product_state")