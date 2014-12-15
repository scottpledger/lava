#!/bin/bash

rm *.txt
rm ../Known/Hamilton/*.txt
rm ../Known/Jay/*.txt
rm ../Known/Madison/*.txt

awk '/^FEDERALIST/{outfile="" ++cnt ".txt"} { print > outfile }' ../All.txt

for i in 1 2 3 4 5 6 7 8 9 ; do
	mv $i.txt 0$i.txt
done

cp `grep -l -i "HAMILTON" *.txt` ../Known/Hamilton/
cp `grep -l -i "JAY" *.txt` ../Known/Jay/
cp `grep -l -i "MADISON" *.txt` ../Known/Madison/

for i in 18 19 20 49 50 51 52 53 54 55 56 57 58 64 ; do
	rm ../Known/*/$i.txt
	cp $i.txt ../Disputed/
done
