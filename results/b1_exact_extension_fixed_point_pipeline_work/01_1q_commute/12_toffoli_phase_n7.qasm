OPENQASM 2.0;
include "qelib1.inc";

// B1 exact-extension generated circuit: 12_toffoli_phase_n7
qreg q[7];
creg c[7];

x q[0];
x q[1];
ccx q[0],q[1],q[3];
h q[2];
ccx q[2],q[3],q[4];
cx q[4],q[5];
rz(pi/9) q[5];
cx q[4],q[5];
cx q[5],q[6];
rz(-pi/7) q[6];
cx q[5],q[6];
t q[3];
tdg q[4];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
