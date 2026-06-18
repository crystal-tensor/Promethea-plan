OPENQASM 2.0;
include "qelib1.inc";

// B1 exact-extension generated circuit: 02_ring_interaction_n8
qreg q[8];
creg c[8];

h q[0];
h q[1];
rzz(pi/13) q[0],q[1];
h q[2];
rzz(pi/13) q[1],q[2];
h q[3];
rzz(pi/13) q[2],q[3];
h q[4];
rzz(pi/13) q[3],q[4];
h q[5];
rzz(pi/13) q[4],q[5];
h q[6];
rzz(pi/13) q[5],q[6];
h q[7];
rzz(pi/13) q[6],q[7];
rz(pi/9) q[0];
rzz(pi/13) q[7],q[0];
rzz(pi/17) q[0],q[1];
rz(pi/11) q[2];
rzz(pi/17) q[1],q[2];
rzz(pi/17) q[2],q[3];
rz(pi/13) q[4];
rzz(pi/17) q[3],q[4];
rzz(pi/17) q[4],q[5];
rz(pi/15) q[6];
rzz(pi/17) q[5],q[6];
rzz(pi/17) q[6],q[7];
rz(pi/10) q[0];
rzz(pi/17) q[7],q[0];
rz(pi/12) q[2];
rz(pi/14) q[4];
rz(pi/16) q[6];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
measure q[7] -> c[7];
