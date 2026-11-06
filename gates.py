def half_adder(qc, a, b, s, cout):
    qc.cx(a, s)
    qc.cx(b, s)
    qc.ccx(a, b, cout)


def full_adder(qc, a, b, cin, s, cout):
    # sum = A xor B xor C
    qc.cx(a, s)
    qc.cx(b, s)
    qc.cx(cin, s)
    # carry-out = majority(a, b, cin) = AB xor AC xor BC
    qc.ccx(a, b, cout)
    qc.ccx(a, cin, cout)
    qc.ccx(b, cin, cout)