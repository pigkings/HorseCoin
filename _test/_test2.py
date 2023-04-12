import hashlib
import time
from flask import Flask, jsonify, request

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

class BlockChain:

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
            data=self.current_data)

        self.current_data = []
        self.chain.append(block)
        return block

    def new_data(self, sender, recipient, quantity):
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'quantity': quantity
        })

    @staticmethod
    def construct_proof_of_work(prev_proof):
        proof_no = 0
        while BlockChain.valid_proof(prev_proof, proof_no) is False:
            proof_no += 1

        return proof_no

    @staticmethod
    def valid_proof(prev_proof, proof_no):
        guess = f'{prev_proof}{proof_no}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def last_block(self):
        return self.chain[-1]

    def mine(self, miner_address):
        self.new_data(
            sender="0",
            recipient=miner_address,
            quantity=1
        )

        last_block = self.last_block
        last_proof_no = last_block.proof_no
        proof_no = self.construct_proof_of_work(last_proof_no)

        last_hash = last_block.calculate_hash
        block = self.construct_block(proof_no, last_hash)

        print("挖矿成功！")
        print(f"新块的哈希值：{block.calculate_hash}")

class Miner:

    def __init__(self, name, address, balance=0):
        self.name = name
        self.address = address
        self.balance = balance
        self.address_list = [address]  # 添加已存在的地址列表

    def mine_block(self):
        chain.mine(self.address)
        self.balance += 1

    def send_coin(self, recipient, quantity):
        if quantity > self.balance:
            print("余额不足，无法完成转账。")
            return False

        chain.new_data(self.address, recipient, quantity)
        self.balance -= quantity
        return True

    def display_balance(self):
        return f"{self.name}的余额为：{self.balance}"

miners = [
    Miner(name="Alice", address="miner1", balance=10),
    Miner(name="Bob", address="miner2", balance=5)
]

app = Flask(__name__)
chain = BlockChain()

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    sender = next(miner for miner in miners if miner.name == data['sender_name'])
    recipient = next(miner for miner in miners if miner.name == data['recipient_name'])
    quantity = int(data['quantity'])

    if sender.send_coin(recipient.address, quantity):
        return jsonify({'message': '转账成功'})
    else:
        return jsonify({'message':'余额不足，无法完成转账'})

@app.route('/balance/<name>')
def balance(name):
    miner = next((miner for miner in miners if miner.name == name), None)
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
@app.route('/adduser', methods=['POST'])  # 添加新接口用于添加矿工
def add_user():
    data = request.get_json()
    name = data['name']
    address = data['address']
    if address in [m.address for m in miners]:
        return jsonify({'message': '该地址已经被注册'})
    else:
        miner = Miner(name=name, address=address)
        miners.append(miner)
        return jsonify({'message': f'{name}注册成功'})
if __name__ == '__main__':
    app.run(debug=False)    
