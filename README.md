# Blockchain Voting

This project attempts to develop a e-voting solution on a blockchain to maintain transparency of votes, an immutable ledger such that votes cannot be modified, and an open system which can be audited. Blockchain enables voting to be a distributed system. Therefore, no one single node can unilaterally modify the chain and mutate voter registration or the actual ballot.

## Architecture

TODO

## File Organization

TODO

## API Documentation

TODO

## Instructions to Setup

The project was developed in Python 3.6. Support for Python 2.7 and < Python 3.5 is untested.

Setup the project using `virtualenv`.

```
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
```

## Instructions to Run

The main files in the project are `voter_registration.py`, `vote.py`, `client_voter_registration.py`, and `client_vote.py`.

These can be run as follows:

```
python voter_registration.py -p 5000
python vote.py -p 6000
python client_voter_registration.py
python client_vote.py
```

Following this, nodes will have to manually registered to each other to form the distributed network. To ease this process, the repository provides an easy way to setup a 20-node blockchain cluster, i.e. 10-node Voterchain cluster and 10-node Votechain cluster. Use the commands below to set it up:

```
./10_node_blockchain.sh
```

Following this, run `client_voter_registration.py` and `client_vote.py` to register a user as a voter and to cast votes respectively.
