import hashlib
import json


class Transaction(object):
    def __init__(self, type):
        self.type = type

    @staticmethod
    def hash(transaction):
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
        transaction_string = json.dumps(
            transaction.to_dictionary(), sort_keys=True).encode()
        return hashlib.sha256(transaction_string).hexdigest()


class Vote(Transaction):
    def __init__(self, voter_id, vote, verifier):
        super(Vote, self).__init__(type='vote')
        self.voter_id = voter_id
        self.vote = vote
        self.verifier = verifier

    def to_dictionary(self):
        value = {
            'type': self.type,
            'voter_id': self.voter_id,
            'verifier': self.verifier,
            'vote': self.vote
        }
        return value

    @staticmethod
    def from_json(value):
        return Vote(value['voter_id'], value['vote'], value['verifier'])


class Voter(Transaction):
    def __init__(self, name, id, verifier):
        super(Voter, self).__init__(type='voter')
        self.name = name
        self.id = id
        self.verifier = verifier

    def to_dictionary(self):
        value = {
            'type': self.type,
            'name': self.name,
            'id': self.id,
            'verifier': self.verifier
        }
        return value

    @staticmethod
    def from_json(value):
        return Voter(value['name'], value['id'], value['verifier'])
