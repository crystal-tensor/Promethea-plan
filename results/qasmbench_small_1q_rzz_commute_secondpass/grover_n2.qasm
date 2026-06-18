// Name of Experiment: Grover N=2 A=10 v1

OPENQASM 2.0;
include "qelib1.inc";


qreg q[2];
creg c[2];

h q[0];
h q[1];

h q[1];
cx q[0],q[1];
h q[1];

u3(1.5707963267948966,0,0) q[0];
u3(0,0,3.1415926535897931) q[1];
cx q[0],q[1];
u3(1.5707963267948966,0,0) q[1];
x q[0];

h q[0];
measure q[0] -> c[0];
h q[1];
measure q[1] -> c[1];
