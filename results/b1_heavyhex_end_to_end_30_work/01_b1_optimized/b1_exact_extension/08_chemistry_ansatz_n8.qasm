OPENQASM 2.0;
include "qelib1.inc";

// B1 exact-extension generated circuit: 08_chemistry_ansatz_n8
qreg q[8];
creg c[8];

ry(pi/4) q[0];
ry(pi/5) q[1];
rzz(pi/9) q[0],q[1];
ry(pi/6) q[2];
ry(pi/7) q[3];
rzz(-pi/9) q[2],q[3];
ry(pi/8) q[4];
ry(pi/9) q[5];
rzz(pi/7) q[4],q[5];
ry(pi/10) q[6];
ry(pi/11) q[7];
rzz(-pi/7) q[6],q[7];
rz(pi/11) q[0];
rz(pi/12) q[1];
rzz(pi/9) q[0],q[1];
rz(pi/13) q[2];
rz(pi/14) q[3];
rzz(-pi/9) q[2],q[3];
rz(pi/15) q[4];
rz(pi/16) q[5];
rzz(pi/7) q[4],q[5];
rz(pi/17) q[6];
rz(pi/18) q[7];
rzz(-pi/7) q[6],q[7];
rz(pi/12) q[0];
rz(pi/13) q[1];
rz(pi/14) q[2];
rz(pi/15) q[3];
rz(pi/16) q[4];
rz(pi/17) q[5];
rz(pi/18) q[6];
rz(pi/19) q[7];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
measure q[7] -> c[7];
