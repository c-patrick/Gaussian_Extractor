%mem=8GB
%nprocshared=2
%chk=ethanol-opt.chk

#p opt B3LYP/6-31G(d) geom=connectivity 

opt

0 1
C 
C 1 B1
H 2 B2 1 A1
H 2 B3 1 A2 3 D1
H 2 B4 1 A3 3 D2
O 1 B5 2 A4 3 D3
H 6 B6 1 A5 2 D4
H 1 B7 2 A6 3 D5
H 1 B8 2 A7 3 D6

B1 1.531810614
B2 1.114466625
B3 1.114466625
B4 1.114558151
B5 1.408442816
B6 0.942290000
B7 1.116690349
B8 1.116690349
A1 111.0625820
A2 111.0625820
A3 110.8269561
A4 109.4404901
A5 107.4828037
A6 111.2797899
A7 111.2797899
D1 120.1071210
D2 -119.9464395
D3 -60.05356052
D4 -180.0000000
D5 59.15400593
D6 -179.2611270

1 2 1.0 6 1.0 8 1.0 9 1.0
2 1 1.0 3 1.0 4 1.0 5 1.0
3 2 1.0
4 2 1.0
5 2 1.0
6 1 1.0 7 1.0
7 6 1.0
8 1 1.0
9 1 1.0


--Link1--
%mem=8GB
%nprocshared=2
%oldchk=ethanol-opt.chk
%chk=ethanol-freq.chk

#p freq B3LYP/chkbasis geom=allcheck 

freq


--Link1--
%mem=8GB
%nprocshared=2
%oldchk=ethanol-opt.chk
%chk=ethanol-td.chk

#p td=(nstates=10,50-50) B3LYP/chkbasis geom=allcheck 

td



