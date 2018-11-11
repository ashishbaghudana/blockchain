from blockchain import Blockchain
from transactions import Vote


class VoteChain(Blockchain):
    def __init__(self):
        super(VoteChain, self).__init__()
        self.voter_nodes = set()

    def new_transaction(self, verifier, vote):
        """Short summary.

        Parameters
        ----------
        verifier : type
            Description of parameter `verifier`.
        vote : type
            Description of parameter `vote`.

        Returns
        -------
        type
            Description of returned object.

        """
        self.current_transactions.append(Vote(verifier=verifier, vote=vote))

        return self.last_block.index + 1

    def serialize_transactions(self):
        return [Vote.to_dictionary(t) for t in self.current_transactions]
