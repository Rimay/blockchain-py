import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transanctions = []
        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        """
        create a block
        :param proof: <int> the proof given by POW algorithm
        :param previous_hash: <str> hash of the previous block
        :return: <dict> new block
        """
        block = {
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transanctions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transanctions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        create a transaction and append it to a list
        :param sender: <str> address of the sender
        :param recipient: <str> address of the recipient
        :param amount: <int>
        :return: the index of the block that will hold this transaction
        """
        self.current_transanctions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1

    def valid_proof(self, lp, p):
        guess = f'{lp}{p}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def proof_of_work(self, last_proof):
        """
        find a p' satisfy hash(pp') starts with 0000
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def register_node(self, address):
        """
        append a new node to self.nodes
        :param address: <str> address of node eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        validate hash and proof of every block
        :param chain: <list> a blockchain
        :return: <bool>
        """
        last_block = chain[0]
        cur_id = 1
        while cur_id < len(chain):
            block = chain[cur_id]
            print(f'{last_block}')
            print(f'{block}')
            print('\n------------\n')

            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            cur_id += 1
        return True

    def resolve_conflicts(self):
        """
        longest length chain
        :return: <bool> True if replaced, else False
        """

        neighbours = self.nodes
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False

    @staticmethod
    def hash(block):
        """
        SHA-256 hash of a block
        :param block: <dict>
        :return: <str>
        """
        # must make sure the block dict is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha3_256(block_string).hexdigest()

    @property
    def last_block(self):
        # return the last block of a chain
        return self.chain[-1]

