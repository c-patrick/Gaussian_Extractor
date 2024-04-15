%mem=8GB
%nprocshared=2
%chk=pyridine-opt.chk

#p opt B3LYP/6-31G(d) geom=connectivity 

opt

0 1
C 
N 1 B1
C 2 B2 1 A1
C 3 B3 2 A2 1 D1
C 4 B4 3 A3 2 D2
C 1 B5 2 A4 3 D3
H 6 B6 1 A5 2 D4
H 5 B7 6 A6 1 D5
H 4 B8 5 A7 6 D6
H 3 B9 4 A8 5 D7
H 1 B10 2 A9 3 D8

B1 1.266621200
B2 1.266621200
B3 1.343009633
B4 1.341754102
B5 1.343009633
B6 1.103672151
B7 1.103626534
B8 1.103672151
B9 1.104182334
B10 1.104182334
A1 117.7692179
A2 123.9130670
A3 118.2161000
A4 123.9130670
A5 120.9343642
A6 121.0137759
A7 120.8495358
A8 119.8950723
A9 116.1918607
D1 -0.000001207
D2 0.000000000
D3 0.000000000
D4 180.0000000
D5 180.0000000
D6 -180.0000000
D7 -180.0000000
D8 -180.0000000

1 2 2.0 6 1.0 11 1.0
2 1 2.0 3 1.0
3 4 2.0 2 1.0 10 1.0
4 5 1.0 3 2.0 9 1.0
5 6 2.0 4 1.0 8 1.0
6 1 1.0 5 2.0 7 1.0
7 6 1.0
8 5 1.0
9 4 1.0
10 3 1.0
11 1 1.0



--Link1--
%mem=8GB
%nprocshared=2
%oldchk=pyridine-opt.chk
%chk=pyridine-freq.chk

#p freq B3LYP/chkbasis geom=allcheck 

freq


--Link1--
%mem=8GB
%nprocshared=2
%oldchk=pyridine-opt.chk
%chk=pyridine-td.chk

#p td=(nstates=10,50-50) B3LYP/chkbasis geom=allcheck 

td



