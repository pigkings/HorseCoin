import requests
import hashlib
import time
import copy
miner_name = input("请输入矿工姓名：")
SERVER_URL = 'http://localhost:5000'
def wk():
    response = requests.get(f'{SERVER_URL}/validate_mine/{miner_name}')
    data = response.json()

    if 'proof_no' in data:
        proof_no = data['proof_no']
        start_time = time.time()
        print("挖矿中...")
        while True:
            last_data=data.copy()
            last_proof_no = last_data['proof_no']
            proof_no+=1
            guess = f'{proof_no}{last_proof_no}'.encode()
            guess_hash = hashlib.sha256(guess).hexdigest()
            if guess_hash[:4] == "0000":
                end_time = time.time()
                print(f"用时{(end_time-start_time):.2f}秒。")
                response = requests.get(f'{SERVER_URL}/mine/{miner_name}/{proof_no}')
                print(response.json()['message'])
                break

    else:
        print(data['message'])


while 1:
    try:
        wk()
    except:
        print('挖矿失败')
