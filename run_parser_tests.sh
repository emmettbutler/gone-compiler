#!/bin/bash
for i in `seq 1 6`; do TESTFILE=tests/parser/parsetest$i.g && cat $TESTFILE && py goneparse.py $TESTFILE; done
