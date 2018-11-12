import argparse
import socket
import threading
import time
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

from voterchain import VoterChain

# Instantiate the node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
voterchain = VoterChain()


@app.route('/mine', methods=['GET'])
def mine():

    voterchain.resolve_conflicts()

    if len(voterchain.current_transactions) == 0:
        response = {'message': 'No transactions to add to the block'}
        return jsonify(response), 200

    # We run the proof of work algorithm to get the next proof
    last_block = voterchain.last_block
    last_proof = last_block.proof
    proof = voterchain.proof_of_work(last_proof)

    # In general, the person who mined this block should be awarded a coin
    # However, in this scheme, only government appointment nodes would allow
    # voter registration. Therefore, there is no need to award anyone a coin

    # Forge the new Block by adding it to the chain
    previous_hash = voterchain.hash(last_block)
    replaced = voterchain.resolve_conflicts()
    if replaced:
        response = {
            'message':
            'Chain has been altered by the addition of another block.'
        }
        return jsonify(response), 500
    block = voterchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': [t.to_dictionary() for t in block.transactions],
        'transaction_hashes': list(block.transaction_hashes),
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }

    return jsonify(response), 200


@app.route('/voter/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['name', 'id']
    if not all(k in values for k in required):
        return (
            'Missing values, voter registration should have "name" and "id"',
            400)

    current_identifier = 0
    while voterchain.valid_proof(values['id'], values['name'],
                                 current_identifier) is False:
        current_identifier += 1

    # Create a new Transaction
    index = voterchain.new_transaction(
        id=values['id'], name=values['name'], verifier=current_identifier)
    response = {
        'message': f'Transaction will be added to Block {index}',
        'identifier': current_identifier
    }
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': voterchain.serialize_chain(),
        'length': len(voterchain.chain),
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
        voterchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(voterchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = voterchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': voterchain.serialize_chain()
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': voterchain.serialize_chain()
        }

    return jsonify(response), 200


@app.route('/ping', methods=['GET'])
def ping():
    response = {'healthy': True}
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = list(voterchain.nodes.union({my_addr}))
    return jsonify({'nodes': nodes}), 200


def background_mining(interval=15):
    while True:
        time.sleep(interval)
        requests.get('%s/mine' % my_addr)


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
