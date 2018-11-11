from time import time

from transactions import Vote, Voter

TRANSACTION_TYPES = {'vote': Vote, 'voter': Voter}


class Block(object):
    def __init__(self,
                 index,
                 transactions,
                 proof,
                 previous_hash,
                 timestamp=time(),
                 transaction_hashes=None):
        self.index = index
        self.proof = proof
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transaction_hashes = transaction_hashes
        if not self.transaction_hashes:
            self.transaction_hashes = set()

    def to_dictionary(self):
        transactions = [
            transaction.to_dictionary() for transaction in self.transactions
        ]
        value = {
            'index': self.index,
            'proof': self.proof,
            'transactions': transactions,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'transaction_hashes': list(self.transaction_hashes)
        }
        return value

    @staticmethod
    def from_json(json_value):
        return Block(json_value['index'],
                     Block.transactions_from_json(json_value['transactions']),
                     json_value['proof'], json_value['previous_hash'],
                     json_value['timestamp'],
                     set(json_value['transaction_hashes']))

    @staticmethod
    def transactions_from_json(json_value):
        transactions = []
        for transaction in json_value:
            transactions.append(
                TRANSACTION_TYPES[transaction['type']].from_json(transaction))
        return transactions
