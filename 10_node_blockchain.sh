#!/bin/bash

source venv/bin/activate

function ctrl_c() {
    kill -9 $RPID0 $RPID1 $RPID2 $RPID3 $RPID4 $RPID5 $RPID6 $RPID7 $RPID8 $RPID9
    kill -9 $VPID0 $VPID1 $VPID2 $VPID3 $VPID4 $VPID5 $VPID6 $VPID7 $VPID8 $VPID9
    exit 0
}

python voter_registration.py -p 5000 &> /dev/null &
RPID0=$!
python voter_registration.py -p 5001 &> /dev/null &
RPID1=$!
python voter_registration.py -p 5002 &> /dev/null &
RPID2=$!
python voter_registration.py -p 5003 &> /dev/null &
RPID3=$!
python voter_registration.py -p 5004 &> /dev/null &
RPID4=$!
python voter_registration.py -p 5005 &> /dev/null &
RPID5=$!
python voter_registration.py -p 5006 &> /dev/null &
RPID6=$!
python voter_registration.py -p 5007 &> /dev/null &
RPID7=$!
python voter_registration.py -p 5008 &> /dev/null &
RPID8=$!
python voter_registration.py -p 5009 &> /dev/null &
RPID9=$!


python vote.py -p 6000 &> /dev/null &
VPID0=$!
python vote.py -p 6001 &> /dev/null &
VPID1=$!
python vote.py -p 6002 &> /dev/null &
VPID2=$!
python vote.py -p 6003 &> /dev/null &
VPID3=$!
python vote.py -p 6004 &> /dev/null &
VPID4=$!
python vote.py -p 6005 &> /dev/null &
VPID5=$!
python vote.py -p 6006 &> /dev/null &
VPID6=$!
python vote.py -p 6007 &> /dev/null &
VPID7=$!
python vote.py -p 6008 &> /dev/null &
VPID8=$!
python vote.py -p 6009 &> /dev/null &
VPID9=$!

python 10_node_register.py 5000 5010 6000 6010

trap ctrl_c INT

read -r -d '' _ </dev/tty
