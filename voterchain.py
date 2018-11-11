from blockchain import Blockchain
from transactions import Voter


class VoterChain(Blockchain):
    def __init__(self):
        super(VoterChain, self).__init__()

    def new_transaction(self, name, id, verifier):
        """Short summary.

        Parameters
        ----------
        name : type
            Description of parameter `name`.
        id : type
            Description of parameter `id`.
        verifier : type
            Description of parameter `verifier`.
        voted : type
            Description of parameter `voted`.

        Returns
        -------
        type
            Description of returned object.

        """
        voter = Voter(name=name, id=id, verifier=verifier)
        self.current_transactions.append(voter)

        return self.last_block.index + 1

    @staticmethod
    def serialize_transactions(block):
        return [Voter.to_dictionary(t) for t in block.transactions]
