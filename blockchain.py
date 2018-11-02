class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        pass

    def new_transaction(self, sender, recipient, amount):
        """Record a new transaction on the blockchain.

        Parameters
        ----------
        sender : str
            Address of the sender.
        recipient : str
            Address of the recipient.
        amount : float
            Amount.

        Returns
        -------
        int
            Index of the block that will hold this transaction.

        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        pass

    @property
    def last_block(self):
        pass
