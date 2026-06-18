OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[1];
// B3 observable-estimation proxy for h2_bond_stretch
// Coordinate: H-H bond length
// q[0] is the Hadamard-test ancilla; q[1:] are Jordan-Wigner spin-orbital proxy qubits.
x q[1];
x q[2];
h q[0];
crz(0.0645462315945) q[0],q[1];
h q[0];
measure q[0] -> c[0];
