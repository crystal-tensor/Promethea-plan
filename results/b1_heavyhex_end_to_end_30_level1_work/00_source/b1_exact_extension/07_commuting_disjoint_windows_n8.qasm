OPENQASM 2.0;
include "qelib1.inc";

// B1 exact-extension generated circuit: 07_commuting_disjoint_windows_n8
qreg q[8];
creg c[8];

h q[0];
h q[3];
h q[6];
cx q[0],q[1];
rx(pi/7) q[5];
ry(pi/9) q[6];
rz(pi/5) q[1];
cx q[0],q[1];
cx q[2],q[3];
rz(pi/11) q[7];
rx(pi/13) q[0];
rz(-pi/6) q[3];
cx q[2],q[3];
cx q[4],q[5];
h q[0];
h q[2];
rz(pi/8) q[5];
cx q[4],q[5];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
measure q[7] -> c[7];
