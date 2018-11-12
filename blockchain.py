import hashlib
import json
from urllib.parse import urlparse

import requests

from block import Block
from transactions import Transaction


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.last_consensus = 0
        self.nodes = set()

        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """Create a new block in the blockchain.

        Parameters
        ----------
        proof : int
            The proof given by the Proof of Work algorithm.
        previous_hash : str
            Hash of previous block.

        Returns
        -------
        dict
            New block.

        """
        block = Block(
            index=len(self.chain) + 1,
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=(previous_hash or self.hash(self.chain[-1])),
            transaction_hashes=set(
                [Transaction.hash(t) for t in self.current_transactions]))
        self.current_transactions = []
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        """Creates a SHA-256 hash of a block.

        Parameters
        ----------
        block : dict
            Block.

        Returns
        -------
        str
            SHA-256 hash of the block.

        """
        block_string = json.dumps(
            block.to_dictionary(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """Simple Proof of Work Algorithm.

            - Find a number p' such that hash(pp') contains 4 leading zeros
              where p is the previous p'
            - p is the previous proof, and p' is the new proof

        Parameters
        ----------
        last_proof : int
            The last proof value.

        Returns
        -------
        int
            The new proof value.

        """
        proof = 0
        previous_hash = self.hash(self.chain[-1])
        while self.valid_proof(last_proof, proof, previous_hash) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, hash):
        guess = f'{last_proof}{proof}{hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        parsed_url = urlparse(address)
        node = f'{parsed_url.scheme}://{parsed_url.netloc}'
        self.nodes.add(node)

    def valid_chain(self, chain):
        last_block = chain[self.last_consensus]
        current_index = self.last_consensus + 1

        while current_index < len(chain):
            block = chain[current_index]
            # Check that the hash of the block is correct
            if block.previous_hash != self.hash(last_block):
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block.proof, block.proof,
                                    block.previous_hash):
                return False
            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = Blockchain.deserialize_chain(response.json()['chain'])

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer
        # than ours
        if new_chain:
            self.chain = new_chain
            self.consensus = new_chain[-1].index
            return True

        return False

    @staticmethod
    def deserialize_chain(chain_obj):
        chain = []
        for block_obj in chain_obj:
            block = Block.from_json(block_obj)
            chain.append(block)
        return chain

    def serialize_chain(self):
        chain_obj = []
        for block in self.chain:
            chain_obj.append(block.to_dictionary())
        return chain_obj
