from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1, 1)
qc.x(0)            # flip qubit 0 from 0 to 1
qc.measure(0, 0)   # read it into a classical bit

result = AerSimulator().run(qc, shots=100).result()
print(result.get_counts())   # expect {'1': 100}