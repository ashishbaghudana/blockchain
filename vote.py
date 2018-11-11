import argparse
from uuid import uuid4

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
    # We run the proof of work algorithm to get the next proof
    last_block = votechain.last_block
    last_proof = last_block.proof
    proof = votechain.proof_of_work(last_proof)

    # In general, the person who mined this block should be awarded a coin
    # However, in this scheme, only government appointment nodes would allow
    # voter registration. Therefore, there is no need to award anyone a coin

    # Forge the new Block by adding it to the chain
    previous_hash = votechain.hash(last_block)
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
    while votechain.valid_proof(values['id'], values['name'],
                                current_identifier) is False:
        current_identifier += 1

    # Create a new Transaction
    index = votechain.new_transaction(
        id=values['id'], name=values['name'], verifier=current_identifier)
    response = {
        'message': f'Transaction will be added to Block {index}',
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--port',
        help='Port to run on',
        default=6   000,
        type=int,
        required=False)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port)
