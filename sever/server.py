import hashlib
import time
from flask import Flask, jsonify, request
import uuid
import json
import os
class Block:
 
    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp or time.time()
 
    @property
    def calculate_hash(self):
        block_of_string = "{}{}{}{}{}".format(self.index, self.proof_no,
                                              self.prev_hash, self.data,
                                              self.timestamp)
 
        return hashlib.sha256(block_of_string.encode()).hexdigest()

class HorseCoin:

    def __init__(self):
        self.chain = []
        self.current_data = []
        self.nodes = set()
        self.construct_genesis()

    def construct_genesis(self):
        self.construct_block(proof_no=0, prev_hash='0')

    def construct_block(self, proof_no, prev_hash):
        block = Block(
            index=len(self.chain),
            proof_no=proof_no,
            prev_hash=prev_hash,
            data=self.current_data
        )

        self.current_data = []
        self.chain.append(block)
        return block

    @staticmethod
    def check_validity(block, prev_block):
        if prev_block.index + 1 != block.index:
            return False

        elif prev_block.calculate_hash != block.prev_hash:
            return False

        elif not horsecoin.verifying_proof(block.proof_no, prev_block.proof_no):
            return False

        elif block.timestamp <= prev_block.timestamp:
            return False

        return True

    def new_data(self, sender, recipient, quantity):
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'quantity': quantity
        })
        return True

    @staticmethod
    def proof_of_work(last_proof):
        '''this simple algorithm identifies a number f' such that hash(ff') contain 4 leading zeroes
         f is the previous f'
         f' is the new proof
        '''
        proof_no = horsecoin.chain[-1].proof_no
        while horsecoin.verifying_proof(proof_no, last_proof) is False:
            proof_no += 1

        return proof_no

    @staticmethod
    def verifying_proof(last_proof, proof):
        #verifying the proof: does hash(last_proof, proof) contain 4 leading zeroes?

        guess = f'{last_proof}{proof}'.encode()
        print(f'{last_proof}{proof}')
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def latest_block(self):
        return self.chain[-1]

    def block_mining(self, details_miner):
        self.new_data(
            sender="0",  #it implies that this node has created a new block
            recipient=details_miner,
            quantity=
                1,  #creating a new block (or identifying the proof number) is awared with 1
        )

        last_block = self.latest_block

        last_proof_no = last_block.proof_no
        proof_no = self.proof_of_work(last_proof_no)

        last_hash = last_block.calculate_hash
        block = self.construct_block(proof_no, last_hash)

        return vars(block)
    def save_coins(self,path):
        with open(path, 'w') as f:
            json.dump([vars(block) for block in self.chain], f)

    def load_coins(self,path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                chain_data = json.load(f)
                self.chain = [Block(**block_data) for block_data in chain_data]

# Instantiate our Node
app = Flask(__name__)

horsecoin = HorseCoin()
horsecoin.load_coins('horsecoin.json')


miners = []


class Miner:
    def __init__(self, name, address, balance):
        self.name = name
        self.address = address
        self.balance = balance

    def display_balance(self):
        return self.balance
def miner_save(path,data):
    with open(path, 'w+') as f:
        json.dump([{'name': m.name, 'address': m.address, 'balance': m.balance} for m in data], f)
        
def miner_load(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            miner_list = json.load(f)
        if miner_list=="" or miner_list==[] or miner_list=={}:
            return False
        for i in miner_list:
            miner = Miner(name=i['name'], address=i['address'], balance=i['balance'])
            miners.append(miner) 
miner_load('miners.json')
@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    sender_address = data['sender_address']
    recipient_address = data['recipient_address']
    quantity = data['quantity']

    sender = next((miner for miner in miners if miner.address == sender_address), None)
    recipient = next((miner for miner in miners if miner.address == recipient_address), None)

    if not sender or not recipient:
        return jsonify({'message': '发送方或接收方不存在'})

    if sender.balance < quantity:
        return jsonify({'message': '余额不足，无法完成转账'})

    sender.balance -= quantity
    recipient.balance += quantity

    return jsonify({'message': '转账成功'})

@app.route('/balance/<address>')
def balance(address):
    miner = next((miner for miner in miners if miner.address == address), None)

    if miner:
        return jsonify({'balance': miner.display_balance()})
    else:
        return jsonify({'message': '未找到该用户'})

@app.route('/name/<address>')
def name(address):
    miner = next((miner for miner in miners if miner.address == address), None)
    if miner:
        return jsonify({'name': miner.name})
    else:
        return jsonify({'message': '未找到该地址对应的用户'})
@app.route('/adduser', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data['name']
    address = str(uuid.uuid4()).replace('-', '')
    if name in [m.name for m in miners]:
        return jsonify({'address': '该名字已经被注册'})
    else:
        miner = Miner(name=name, address=address, balance=0)
        miners.append(miner)
        miner_save('miners.json',miners)
        return jsonify({'address': f'{address}'})
@app.route('/miners')
def get_miners():
    miner_list = [{'name': miner.name, 'balance': miner.balance} for miner in miners]
    return jsonify({'miners': miner_list})
@app.route('/blocks')
def get_blocks():
    block_list = [{'index': block.index, 'proof_no': block.proof_no, 'prev_hash': block.prev_hash} for block in horsecoin.chain]
    return jsonify({'blocks': block_list})
@app.route('/validate_mine/<name>')
def validate_mine(name):
    miner = next((miner for miner in miners if miner.name == name), None)
    if not miner:
        return jsonify({'message': '该矿工不存在'})

    last_block = horsecoin.latest_block
    last_proof_no = last_block.proof_no
    #proof_no = horsecoin.proof_of_work(last_proof_no)
    proof_no=horsecoin.chain[-1].proof_no

    return jsonify({'proof_no': proof_no})
@app.route('/mine/<name>/<int:proof_no>')
def mine(name, proof_no):
    miner = next((miner for miner in miners if miner.name == name), None)
    if not miner:
        return jsonify({'message': '该矿工不存在'})
    
    if not horsecoin.verifying_proof(proof_no,horsecoin.chain[-1].proof_no):
        return jsonify({'message': '挖矿失败'})
    last_block = horsecoin.latest_block
    last_hash = last_block.calculate_hash

    block_data = {
        'sender': "0",
        'recipient': miner.address,
        'quantity': 1,
    }
    block = Block(
        index=len(horsecoin.chain),
        proof_no=proof_no,
        prev_hash=last_hash,
        data=[block_data],
    )

    horsecoin.chain.append(block)
    horsecoin.save_coins('horsecoin.json')
    if miner:
        for miner in miners:
            if miner.name == name:
                miner.balance=miner.balance+1
        miner_save('miners.json',miners)
    print(name,proof_no)

    
    return jsonify({'message': '挖矿成功'})
if __name__ == '__main__':
    app.run(debug=False)
