OPENQASM 2.0;
include "qelib1.inc";

// B1 exact-extension generated circuit: 04_arithmetic_phase_n6
qreg q[6];
creg c[6];

x q[0];
x q[2];
h q[4];
cx q[0],q[3];
rz(pi/5) q[3];
cx q[0],q[3];
cx q[1],q[4];
rz(-pi/6) q[4];
cx q[1],q[4];
cx q[2],q[5];
rz(pi/8) q[5];
cx q[2],q[5];
cx q[3],q[5];
rz(pi/10) q[5];
cx q[3],q[5];
ccx q[0],q[1],q[3];
ccx q[2],q[3],q[5];
t q[0];
tdg q[5];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
