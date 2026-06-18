OPENQASM 2.0;
include "qelib1.inc";

// B1 exact-extension generated circuit: 05_qft_phase_ladder_n5
qreg q[5];
creg c[5];

h q[0];
h q[1];
cu1(pi/4) q[1],q[0];
h q[2];
cu1(pi/8) q[2],q[0];
h q[3];
cu1(pi/16) q[3],q[0];
h q[4];
cu1(pi/32) q[4],q[0];
cu1(pi/4) q[2],q[1];
cu1(pi/8) q[3],q[1];
cu1(pi/16) q[4],q[1];
cu1(pi/4) q[3],q[2];
cu1(pi/8) q[4],q[2];
cu1(pi/4) q[4],q[3];
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
