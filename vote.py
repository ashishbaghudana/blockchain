import argparse
import random
import socket
import threading
import time
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

from votechain import VoteChain

# Instantiate the node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
votechain = VoteChain()


@app.route('/mine', methods=['GET'])
def mine():

    votechain.resolve_conflicts()

    if len(votechain.current_transactions) == 0:
        response = {'message': 'No transactions to add to the block'}
        return jsonify(response), 200

    # We run the proof of work algorithm to get the next proof
    last_block = votechain.last_block
    last_proof = last_block.proof
    proof = votechain.proof_of_work(last_proof)

    # In general, the person who mined this block should be awarded a coin
    # However, in this scheme, only government appointment nodes would allow
    # voter registration. Therefore, there is no need to award anyone a coin

    # Forge the new Block by adding it to the chain
    previous_hash = votechain.hash(last_block)
    replaced = votechain.resolve_conflicts()
    if replaced:
        response = {
            'message':
            'Chain has been altered by the addition of another block.'
        }
        return jsonify(response), 500
    block = votechain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': [t.to_dictionary() for t in block.transactions],
        'transaction_hashes': list(block.transaction_hashes),
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }

    return jsonify(response), 200


@app.route('/vote/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['voter_id', 'vote']
    if not all(k in values for k in required):
        return ('Missing values, voting should have "voter_id" and "vote"',
                400)

    votechain.resolve_conflicts()
    for block in votechain.chain:
        for transaction in block.transactions:
            if values['voter_id'] == transaction.voter_id:
                error_msg = 'You have already voted.'
                return jsonify({'message': error_msg}), 404

    voter_node = random.choice(list(votechain.voter_nodes))
    response = requests.get('%s/chain' % voter_node)
    if not response.ok:
        error_msg = 'Not able to communicate with voter registration nodes'
        return jsonify({'message': error_msg}), 500

    chain = response.json()
    if not identifier_in_chain(values['voter_id'], chain):
        error_msg = 'Voter with id %s is not registered' % values['voter_id']
        return jsonify({'message': error_msg}), 404

    current_identifier = 0
    while votechain.valid_proof(values['voter_id'], values['vote'],
                                current_identifier) is False:
        current_identifier += 1

    # Create a new Transaction
    index = votechain.new_transaction(
        voter_id=values['voter_id'],
        vote=values['vote'],
        verifier=current_identifier)
    response = {
        'message': f'Your vote will be recorded to Block {index}',
        'identifier': current_identifier
    }
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': votechain.serialize_chain(),
        'length': len(votechain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return jsonify({
            "error": "Error: Please supply a valid list of nodes"
        }), 400
    for node in nodes:
        votechain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(votechain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = votechain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': votechain.serialize_chain()
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': votechain.serialize_chain()
        }

    return jsonify(response), 200


@app.route('/ping', methods=['GET'])
def ping():
    response = {'healthy': True}
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = list(votechain.nodes.union({my_addr}))
    return jsonify({'nodes': nodes}), 200


@app.route('/voter_nodes/register', methods=['POST'])
def register_voter_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return jsonify({
            "error": "Error: Please supply a valid list of nodes"
        }), 400
    for node in nodes:
        votechain.register_voter_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(votechain.voter_nodes),
    }
    return jsonify(response), 201


def background_mining(interval=15):
    while True:
        time.sleep(interval)
        requests.get('%s/mine' % my_addr)


def identifier_in_chain(identifier, chain):
    for block in chain['chain']:
        for transaction in block['transactions']:
            if str(transaction['verifier']) == str(identifier):
                return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--port',
        help='Port to run on',
        default=5000,
        type=int,
        required=False)
    args = parser.parse_args()

    my_ip = socket.gethostbyname(socket.gethostname())
    port = args.port
    my_addr = f'http://{my_ip}:{port}'

    mining_thread = threading.Thread(target=background_mining)
    mining_thread.start()

    app.run(host='0.0.0.0', port=args.port, threaded=True)
