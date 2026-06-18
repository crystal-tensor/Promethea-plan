OPENQASM 2.0;
include "qelib1.inc";

// B1 exact-extension generated circuit: 03_qec_syndrome_phase_n7
qreg q[7];
creg c[7];

h q[0];
cx q[0],q[5];
rz(pi/8) q[5];
cx q[0],q[5];
h q[1];
cx q[1],q[5];
rz(pi/9) q[5];
cx q[1],q[5];
h q[2];
cx q[2],q[6];
rz(pi/10) q[6];
cx q[2],q[6];
cx q[3],q[6];
rz(pi/11) q[6];
cx q[3],q[6];
cx q[4],q[5];
rz(pi/12) q[5];
cx q[4],q[5];
h q[0];
h q[1];
h q[2];
h q[3];
h q[4];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
