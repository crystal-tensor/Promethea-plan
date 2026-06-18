// Implementation of Deutsch algorithm with two qubits for f(x)=x
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];

h q[0];
u3(1.5707963267948966,3.1415926535897931,3.1415926535897931) q[1];
cx q[0],q[1];
h q[0];
measure q[0] -> c[0];
measure q[1] -> c[1];
