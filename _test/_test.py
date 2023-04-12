import hashlib
import time

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

    def mine_block(self, chain):
        chain.mine(self.address)
        self.balance += 1

    def send_coin(self, recipient, quantity, chain):
        if quantity > self.balance:
            print("余额不足，无法完成转账。")
            return False

        chain.new_data(self.address, recipient, quantity)
        self.balance -= quantity
        return True

    def display_balance(self):
        print(f"{self.name}的余额为：{self.balance}")

chain = BlockChain()
miner1 = Miner(name="矿工1", address="矿工1地址", balance=10)
miner2 = Miner(name="矿工2", address="矿工2地址", balance=5)

miner1.display_balance()  # 输出初始余额

miner1.mine_block(chain)  # 矿工1挖矿

miner1.send_coin(miner2.address, 3, chain)  # 矿工1向矿工2转账

miner1.display_balance()  # 输出余额
miner2.display_balance()  # 输出余额
