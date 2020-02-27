from uuid import uuid4
from flask import Flask, jsonify, request

from blockchain import Blockchain

app = Flask(__name__)
node_id = str(uuid4()).replace('-', '')
blochain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_proof = blochain.last_block['proof']
    proof = blochain.proof_of_work(last_proof)

    blochain.new_transaction(
        sender="0",
        recipient=node_id,
        amount=1,
    )

    block = blochain.new_block(proof)

    rsp = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(rsp), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    print('xxxxxxxxxx')
    values = request.get_json()
    print('hhhhhhhhhh', values)
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'missing values', 400

    id = blochain.new_transaction(values['sender'], values['recipient'], values['amount'])
    rsp = {'message': f'Transaction will be added to Block {id}'}
    return jsonify(rsp), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    rsp = {
        'chain': blochain.chain,
        'length': len(blochain.chain)
    }
    return jsonify(rsp), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blochain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blochain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blochain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blochain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blochain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

