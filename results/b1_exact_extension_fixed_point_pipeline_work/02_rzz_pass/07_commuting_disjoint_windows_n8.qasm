OPENQASM 2.0;
include "qelib1.inc";

// B1 exact-extension generated circuit: 07_commuting_disjoint_windows_n8
qreg q[8];
creg c[8];

h q[0];
rzz(pi/5) q[0],q[1];
h q[3];
rzz(-pi/6) q[2],q[3];
rx(pi/7) q[5];
rzz(pi/8) q[4],q[5];
u3(1.9198621771937625,0,3.1415926535897931) q[6];
rz(pi/11) q[7];
u3(1.5707963267948968,0.241660973353061,3.1415926535897931) q[0];
h q[2];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
measure q[7] -> c[7];
