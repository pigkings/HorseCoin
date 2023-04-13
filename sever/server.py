import json
import os
import uuid
import hashlib
import time
from wsgiref.simple_server import make_server

class Block:

    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp or time.time()

    def hash(self):
        block_of_string = "{}{}{}{}{}".format(
            self.index,
            self.proof_no,
            self.prev_hash,
            self.data,
            self.timestamp
        )
        return hashlib.sha256(block_of_string.encode()).hexdigest()

class HorseCoin:

    def __init__(self):
        self.current_data = []
        self.chain = [self.genesis_block()]
        self.nodes = set()

    def genesis_block(self):
        self.current_data.append({
            'sender': "0",
            'recipient': "686f727365636f696e",
            'amount': 100000000
        })
        return Block(0, 0, '0', self.current_data)

    def add_block(self,index, proof_no, prev_hash):
        block = Block(
            index+1,
            proof_no,
            prev_hash,
            self.current_data
        )
        self.current_data = []
        self.chain.append(block)
        return block

    @staticmethod
    def is_valid_block(block, prev_block):
        return (
            prev_block.index + 1 == block.index and
            prev_block.hash() == block.prev_hash and
            HorseCoin.is_valid_proof(prev_block.proof_no, block.proof_no) and
            block.timestamp > prev_block.timestamp
        )

    def add_transaction(self, sender, recipient, amount):
        if amount <= 0:
            return False
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return True

    @staticmethod
    def is_valid_proof(proof, prev_proof):
        guess = f'{prev_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def latest_block(self):
        return self.chain[-1]

    def mine_block(self, miner_address,proof):
        
        # 收取 1% 的费用到指定地址
        fee = 1 * 0.01
        
        self.add_transaction(
            sender="686f727365636f696e",
            recipient=miner_address,
            amount=1
        )
        self.add_transaction(
            sender=miner_address,
            recipient="686f727365636f696e",
            amount=fee
        )
        transaction("686f727365636f696e",miner_address,1)
        transaction(miner_address,"686f727365636f696e",fee)
        prev_block = self.latest_block
        prev_proof = prev_block.proof_no
        prev_hash = prev_block.hash()
        block = self.add_block(prev_block.index,proof, prev_hash)  

        return block

    def save_blocks(self, path):
        if os.path.exists(path):
            if os.path.getsize(path) >= 3000000 :
                return False
        with open(path, 'w') as f:
            json.dump([vars(block) for block in self.chain], f)
        return True

    def load_blocks(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                chain_data = json.load(f)
            self.chain = [Block(
                index=block_data['index'],
                proof_no=block_data['proof_no'],
                prev_hash=block_data['prev_hash'],
                data=block_data['data'],
                timestamp=block_data.get('timestamp', None)
            ) for block_data in chain_data]
            #self.chain = [Block(**block_data) for block_data in chain_data]
            #block_data['index'], block_data['proof_no'], block_data['prev_hash'], block_data['data'], timestamp = block_data['timestamp']

class Miner:

    def __init__(self, name, address, balance):
        self.name = name
        self.address = address
        self.balance = balance

    def display_balance(self):
        return self.balance
    def forgot_address(self):
        return self.address

def transaction(sender_address,recipient_address,amount):
    sender = next((miner for miner in miners if miner.address == sender_address), None)
    recipient = next((miner for miner in miners if miner.address == recipient_address), None)
    sender.balance -= amount
    sender.balance=round(sender.balance, 2)
    recipient.balance += amount
    recipient.balance=round(recipient.balance,2)

def save_miners(path, miners):
    with open(path, 'w+') as f:
        json.dump([
            {'name': m.name, 'address': m.address, 'balance': m.balance}
            for m in miners
        ], f)

def load_miners(path):
    miners = []
    if os.path.exists(path):
        with open(path, 'r') as f:
            miners_data = json.load(f)
        if miners_data:
            miners = [
                Miner(name=m['name'], address=m['address'], balance=m['balance'])
                for m in miners_data
                ]
    else:
        miner = Miner("", "686f727365636f696e", 100000000)
        miners.append(miner)
        save_miners('miners.json',miners)
        
            
    return miners

horsecoin = HorseCoin()
horsecoin.load_blocks('horsecoin.json')

miners = load_miners('miners.json')

def application(environ, start_response):
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']

    if method == 'POST' and path=='/balance':
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(content_length)
        data = json.loads(body)

        
        address = data['address']
        miner = next((m for m in miners if m.address == address), None)
        if not miner:
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [b"Miners do not exist"]
        balance = miner.display_balance()
        status = '200 OK'
        headers = [('Content-type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [json.dumps({'balance': balance}).encode()]
    elif method == 'POST' and path == '/transfer':
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(content_length)
        data = json.loads(body)

        sender_address = data['sender_address']
        recipient_address = data['recipient_address']
        amount = data['amount']
        sender_name=data['sender_name']

        if sender_name=="":
            status = '403 Error'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Special Name NOT Empty',

            }).encode()]
        sender = next((m for m in miners if m.address == sender_address), None)
        recipient = next((m for m in miners if m.address == recipient_address), None)

        senderd = next((m for m in miners if m.name == sender_name), None)
        if not senderd:
            status = '403 Error'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Special Name Error',

            }).encode()]
        
        if not sender or not recipient:
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Miners do not exist',
            }).encode()]

        if not isinstance(amount, int) or amount <= 0 or amount > sender.balance:
            status = '400 Bad Request'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Not enough money',
            }).encode()]

        

        # 收取 1% 的费用到指定地址
        fee = amount * 0.01
        horsecoin.add_transaction(
            sender=sender_address,
            recipient="686f727365636f696e",
            amount=fee
        )
        horsecoin.add_transaction(
            sender=sender_address,
            recipient=recipient_address,
            amount= round(amount-fee, 2)
        )
        transaction(sender_address,"686f727365636f696e",fee)
        transaction(sender_address,recipient_address,amount-fee)

        save_miners('miners.json', miners)
        horsecoin.save_blocks('horsecoin.json')

        status = '200 OK'
        headers = [('Content-type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [json.dumps({'message': '转账成功'}).encode()]

    elif method == 'POST' and path == '/mine':
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(content_length)
        data = json.loads(body)

        miner_address = data['miner_address']
        miner_proof = data['miner_proof_no']

        

        block = horsecoin.mine_block(miner_address,miner_proof)
        
        if not horsecoin.is_valid_block( horsecoin.chain[-1] , horsecoin.chain[-2]):
            status = '200 OK'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Failed' ,
            }).encode()]

        save_result = horsecoin.save_blocks('horsecoin.json')
        if not save_result:
            status = '500 Internal Server Error'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Failed',
            }).encode()]

        save_miners('miners.json', miners)

        status = '200 OK'
        headers = [('Content-type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [json.dumps({
            'message': '挖矿成功',
            'block': vars(block),
        }).encode()]

    elif method == 'POST' and path == '/validate_mine':
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(content_length)
        data = json.loads(body)

        miner_address = data['miner_address']
        if not next((m for m in miners if m.address == miner_address), None):
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Miners do not exist',
            }).encode()]

        
        status = '200 OK'
        headers = [('Content-type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [json.dumps({
            'proof_no': horsecoin.latest_block.proof_no
            
        }).encode()]
    elif method == 'GET' and path == '/miners':



        _miners=[{'address': "****"+miner.address[-8:], 'balance': miner.balance} for miner in miners]


        status = '200 OK'
        headers = [('Content-type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [json.dumps({
            'miners': _miners
        }).encode()]
    elif method == 'POST' and path == '/register':
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(content_length)
        data = json.loads(body)

        name = data['name']
        if len(name)<10:
            status = '200 OK'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Special Name Length too short',
                'address': ''
            }).encode()]
        address = str(uuid.uuid4()).replace('-', '')
        balance = 0

        miner = Miner(name, address, balance)
        miners.append(miner)

        save_miners('miners.json', miners)

        status = '200 OK'
        headers = [('Content-type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [json.dumps({
            'message': '注册成功',
            'address': miner.address,
        }).encode()]
    elif method == 'POST' and path == '/forgot':
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(content_length)
        data = json.loads(body)

        name = data['name']
        miner = next((m for m in miners if m.name == name), None)
        if not miner:
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [json.dumps({
                'message': 'Miners do not exist',
            }).encode()]
        address = miner.forgot_address()

        status = '200 OK'
        headers = [('Content-type', 'application/json; charset=utf-8')]
        start_response(status, headers)
        return [json.dumps({
            'address': address,
        }).encode()]
    else:
        status = '404 Not Found'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [json.dumps({
                'message': '404',
            }).encode()]
if __name__ == '__main__':
    httpd = make_server('', 5000, application)
    print("Serving on port 5000...")
    httpd.serve_forever()
