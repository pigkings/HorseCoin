import requests
import hashlib
import time
import copy

SERVER_URL = 'http://127.0.0.1:5000'

miner_address = input("请输入矿工地址：")


def wk():
    mdata = {'miner_address': miner_address}
    response = requests.post(f'{SERVER_URL}/validate_mine', json=mdata)
    data=response.json()
    if 'proof_no' in data:
        proof_no = data['proof_no']
        start_time = time.time()
        while True:
            last_data=data.copy()
            last_proof_no = last_data['proof_no']
            proof_no+=1
            guess = f'{proof_no}{last_proof_no}'.encode()
            guess_hash = hashlib.sha256(guess).hexdigest()
            if guess_hash[:4] == "0000":
                end_time = time.time()
                print(f"挖矿成功！用时{(end_time-start_time):.2f}秒。")
                response = requests.post(f'{SERVER_URL}/mine', json={'miner_address': miner_address,'miner_proof_no': proof_no})
                break
    else:
        print(data['message'])

while 1:
    try:
        wk()
    except:
        print('挖矿失败')
