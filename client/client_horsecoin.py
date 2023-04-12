import requests
import hashlib
import time
import copy

SERVER_URL = 'http://localhost:5000'

def add_user():
    name = input("请输入矿工姓名：")


    response = requests.post(f'{SERVER_URL}/adduser', json={'name': name})
    print("地址："+response.json()['address'])

def display_balance():
    address = input("请输入矿工地址：")

    response = requests.get(f'{SERVER_URL}/balance/{address}')
    data = response.json()

    if 'balance' in data:
        print(data['balance'])
    else:
        print(data['message'])

def transfer():
    sender_address = input("请输入发送者地址：")
    recipient_address = input("请输入接收者地址：")
    quantity = int(input("请输入转账数量："))

    data = {'sender_address': sender_address, 'recipient_address': recipient_address, 'quantity': quantity}
    response = requests.post(f'{SERVER_URL}/transfer', json=data)
    print(response.json()['message'])

def mine_block():
    miner_name = input("请输入矿工姓名：")

    response = requests.get(f'{SERVER_URL}/validate_mine/{miner_name}')
    data = response.json()

    if 'proof_no' in data:
        proof_no = data['proof_no']

        input(f"请在3秒内计算出满足以下条件的数字（以回车键结束）：\nhash(last_proof,{proof_no})的前4位为0000\n按下回车键开始计时......")
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
                print(f"挖矿成功！用时{(end_time-start_time):.2f}秒。")
                response = requests.get(f'{SERVER_URL}/mine/{miner_name}/{proof_no}')
                print(response.json()['message'])
                break

    else:
        print(data['message'])

def list_miners():
    response = requests.get(f'{SERVER_URL}/miners')
    data = response.json()

    if 'miners' in data:
        miners = data['miners']
        for miner in miners:
            print(f"{miner['name']}  - {miner['balance']}")
    else:
        print(data['message'])
def list_block():
    response = requests.get(f'{SERVER_URL}/blocks')
    data = response.json()

    if 'blocks' in data:
        blocks = data['blocks']
        for block in blocks:
            print(f"{block['index']}  -  {block['proof_no']}    -**-    {block['prev_hash']}")
    else:
        print(data['message'])
print("**马币**")
while True:
    print("=======================")
    print("请选择要执行的操作：")
    print("1. 添加新矿工")
    print("2. 查询余额")
    print("3. 转账")
    print("4. 挖矿")
    print("5. 查询所有矿工信息")
    print("6. 查询所有马币信息")
    print("7. 退出程序")

    choice = input("请输入选项编号：")

    if choice == '1':
        add_user()
    elif choice == '2':
        display_balance()
    elif choice == '3':
        transfer()
    elif choice == '4':
        mine_block()
    elif choice == '5':
        list_miners()
    elif choice == '6':
        list_block()
    elif choice == '7':
        break
    else:
        print("无效的选项，请重试。")
