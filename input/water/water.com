%mem=8GB
%nprocshared=2
%chk=water-opt.chk

#p opt B3LYP/6-31G(d) geom=connectivity 

opt

0 1
O 
H 1 B1
H 1 B2 2 A1

B1 0.941999122
B2 0.941999122
A1 105.4830361

1 2 1.0 3 1.0
2 1 1.0
3 1 1.0


--Link1--
%mem=8GB
%nprocshared=2
%oldchk=water-opt.chk
%chk=water-freq.chk

#p freq B3LYP/chkbasis geom=allcheck 

freq


--Link1--
%mem=8GB
%nprocshared=2
%oldchk=water-opt.chk
%chk=water-td.chk

#p td=(nstates=10,50-50) B3LYP/chkbasis geom=allcheck 

td



