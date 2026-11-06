# Quantum Calculator

A calculator for `+`, `-`, `*` and `/` on small integers in which **every operation runs as a quantum circuit**, built from X, CNOT and Toffoli gates with Qiskit and simulated with Qiskit Aer.

Mini project by **Yashvardhan Rai**, IIEST Shibpur.

## The idea

A qubit can be in a superposition, but it can also sit in a basis state `|0⟩` or `|1⟩`, exactly like a classical bit. The three gates used here map basis states to basis states, so a circuit made of them is a reversible logic circuit running on qubits:

| Quantum gate | Qiskit            | Effect on bits | Logic gate |
|--------------|-------------------|----------------|------------|
| X            | `qc.x(q)`         | `q ^= 1`       | NOT        |
| CNOT         | `qc.cx(a, t)`     | `t ^= a`       | XOR        |
| Toffoli      | `qc.ccx(a, b, t)` | `t ^= a & b`   | AND        |

Quantum gates are reversible, so they never overwrite a value: they XOR a result into a target qubit. Every result is therefore written into a fresh qubit (an *ancilla*) that starts in `|0⟩`, since `0 ^ f == f`. Measuring a basis state gives its value with certainty, so each circuit runs with `shots=1`.

There is no quantum speed-up here: with basis-state inputs this is reversible classical logic on a simulator. The same kind of arithmetic circuit is a building block of real quantum algorithms such as Shor's, where the inputs are in superposition.

## Project structure

```text
MiniProject/
├── gates.py                half adder and full adder
├── arithmetic.py           encoding, every circuit, simulation, the four operations
├── calculator.py           command-line calculator
├── tests.py                exhaustive tests against Python's own arithmetic
├── requirements.txt
├── README.md
├── quantum_calculator.tex  presentation slides (Beamer)
├── figures/                circuit drawings used in the slides
└── export_circuits.py      regenerates figures/ from the circuits
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The packages that matter are `qiskit` and `qiskit-aer`; `matplotlib` and `pylatexenc` are only needed for drawing circuits with `qc.draw("mpl")`. Tested with Qiskit 2.6.2 and Qiskit Aer 0.18.2. The code uses the current `AerSimulator().run()` API, so old tutorials that import `execute` from `qiskit` will not match it.

## Usage

### Command line

Interactive mode:

```text
$ python calculator.py
Quantum calculator (integers 0-7). Type e.g. 7 * 3, or q to quit.
> 7 + 5
12
> 3 - 6
-3
> 7 * 7
49
> 7 / 3
2 remainder 1
> 5 / 0
error: division by zero
> q
```

One-shot mode:

```text
$ python calculator.py 7 / 3
2 remainder 1
$ python calculator.py 7 x 7
49
```

On the command line, use `x` or a quoted `"*"` for multiplication, because the shell expands a bare `*` into file names. Inputs outside 0 to 7 are rejected with an error message.

### From Python

```python
from arithmetic import add, subtract, multiply, divide

add(5, 3)        # 8
subtract(2, 6)   # -4
multiply(7, 7)   # 49
divide(7, 3)     # (2, 1): quotient and remainder
```

Each function takes an optional bit width `n` (default 3, so inputs 0 to 7), builds the circuit, simulates it once and returns a plain Python integer, or a `(quotient, remainder)` tuple for `divide`.

## How each operation works

### Encoding and readout

`load(qc, reg, value)` applies X to qubit `i` whenever bit `i` of `value` is 1: for example `5 = 101₂` puts X on `a₀` and `a₂`. Qubit 0 holds the least significant bit.

`run(qc)` simulates the circuit and converts the measured bitstring with `int(bits, 2)`. Qiskit prints classical bit 0 on the right, which is already the usual way to write binary, so no reversing is needed. When a circuit has several classical registers, Qiskit separates them with spaces and puts the last-added register on the left, so `run()` strips the spaces first.

### Addition: ripple-carry adder

- **Half adder** (`half_adder`): sum `s = a ⊕ b` (two CNOTs) and carry `c = a·b` (one Toffoli).
- **Full adder** (`full_adder`): `s = a ⊕ b ⊕ c_in` (three CNOTs) and `c_out = ab ⊕ a·c_in ⊕ b·c_in` (three Toffolis). This is the majority function written with XOR instead of OR, which works because exactly two of the three products are never true at once.
- **Ripple-carry adder** (`build_adder`): `n` full adders in a chain. The carry out of column `i` is the carry in of column `i+1`, and `c₀ = 0`. Registers `a`, `b`, `s` (n qubits each) and `c` (n+1) give `4n+1` qubits. The answer is `c_n s_{n−1} … s₀`, which has n+1 bits.

### Subtraction: two's complement

`build_subtractor` reuses the adder, using `x − y = x + NOT(y) + 1 (mod 2ⁿ)`. It applies X to every qubit of `b` (giving NOT y) and X to `c₀` (the +1). The final carry gives the sign:

- `c_n = 1`: `x ≥ y`, and the answer is `s`
- `c_n = 0`: `x < y`, and the answer is `s − 2ⁿ`

`subtract()` decodes this into a signed Python integer, so `subtract(2, 6)` returns `-4`.

### Multiplication: array multiplier

`build_multiplier` does binary long multiplication (shift and add):

1. **Partial products:** `p_ij = a_j · b_i`, one Toffoli each, `n²` in total. Row `i` is a copy of `a` if `b_i = 1` and zero otherwise.
2. **Accumulation:** the rows are added with `ripple_add`, row `i` shifted left by `i`. Bits below the shift are already final, so only the overlapping bits go through each adder.
3. **Padding:** short operands are padded with a shared `zero` qubit. It is only ever used as a control, so it never changes.

The product has `2n` bits.

### Division: restoring division

`build_divider` runs binary long division, one step per quotient bit, most significant bit first:

1. **Shift:** shift the remainder left and bring in the next dividend bit, `r' = 2r + a_j`. This costs no gates; it is a re-ordering of the qubit list in Python.
2. **Compare and subtract:** `ripple_sub` computes `r' − d` with the two's-complement trick. Its final carry `k` is 1 exactly when `r' ≥ d`, and `k` becomes the quotient bit. The X gates on `d` are undone afterwards, so the divisor survives for the next step.
3. **Choose:** `mux` picks the new remainder without an `if`: `r_new = (k AND diff) ⊕ (NOT k AND r')`, built from Toffolis and an X on `k` that is flipped back afterwards.

The remainder uses n+1 bits. That is always enough, because `r < d ≤ 2ⁿ − 1` gives `2r + 1 < 2ⁿ⁺¹`. Division by zero is rejected in Python before any circuit is built. `try_subtract` and `try_mux` are standalone checks for the two building blocks.

## Resources (n = 3)

| Operation | Qubits | CNOT | Toffoli | X* | Depth |
|-----------|-------:|-----:|--------:|---:|------:|
| add       |     13 |    9 |       9 |  0 |    12 |
| subtract  |     13 |    9 |       9 |  4 |    12 |
| multiply  |     30 |   18 |      27 |  0 |    20 |
| divide    |     47 |   36 |      60 | 33 |    61 |

\*Not counting the X gates that load the inputs.

A statevector simulation of N qubits stores 2^N complex amplitudes at 16 bytes each: 128 KiB for the adder, but 16 GiB for the multiplier and about 2 PiB for the divider. These circuits never create superposition or entanglement, so `multiply` and `divide` use `AerSimulator(method="matrix_product_state")`, whose cost grows with entanglement rather than with the number of qubits. Even the 47-qubit divider runs in milliseconds. `add` and `subtract` use Aer's default method.

## Testing

```bash
python tests.py
```

This checks every input pair for n = 3 against Python's `+`, `-`, `*`, `//` and `%`: 64 pairs per operation and 56 for division (y = 0 is skipped). That is 248 cases in total. Expected output:

```text
add: all tests passed
sub: all tests passed
mult: all tests passed
div: all tests passed
```

## Changing the bit width

Every function takes `n`, and `tests.py` and `calculator.py` each set `N` at the top. The adder and subtractor stay small (`4n+1` qubits), but the multiplier and divider grow quickly:

| n | add / subtract | multiply | divide |
|---|---------------:|---------:|-------:|
| 3 |             13 |       30 |     47 |
| 4 |             17 |       52 |     74 |
| 5 |             21 |       80 |    107 |

## Presentation

- **`quantum_calculator.tex`**: Beamer slides (Madrid theme) that explain the project, using the drawings in `figures/`. Compile with `pdflatex` (run it twice so the outline fills in) or upload the slides zip to Overleaf. Only standard packages are needed: beamer, TikZ, booktabs and amsmath.
- **`export_circuits.py`**: regenerates `figures/` by converting the circuits in `gates.py` and `arithmetic.py` into quantikz drawings, so the figures always match the code. Run it from this folder. It needs `pdflatex` with the quantikz package, `pdftoppm` (poppler), `pypdf` and `Pillow`.

## Limitations and future work

- Only non-negative integer inputs, 0 to 7 by default.
- Ancillas are left holding intermediate values ("garbage"). To use these circuits inside a superposition-based algorithm, they would have to be uncomputed (Bennett's trick).
- Possible extensions: a QFT-based Draper adder, which adds with phase rotations and no carry qubits; the Cuccaro in-place adder, which needs `2n+2` qubits instead of `4n+1`; running small instances on real IBM hardware; negative and fixed-point numbers.

## References

- M. A. Nielsen and I. L. Chuang, *Quantum Computation and Quantum Information*, Cambridge University Press, 2010.
- V. Vedral, A. Barenco and A. Ekert, "Quantum networks for elementary arithmetic operations," *Phys. Rev. A* 54, 147 (1996).
- S. A. Cuccaro, T. G. Draper, S. A. Kutin and D. P. Moulton, "A new quantum ripple-carry addition circuit," arXiv:quant-ph/0410184 (2004).
- T. G. Draper, "Addition on a quantum computer," arXiv:quant-ph/0008033 (2000).
- C. H. Bennett, "Logical reversibility of computation," *IBM J. Res. Dev.* 17, 525 (1973).
