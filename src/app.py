import json
from web3 import Web3,HTTPProvider

blockchain_address="http://127.0.0.1:7545"

web3=Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount=web3.eth.accounts[0]

artifact_path='../build/contracts/register.json'
contract_address="0x1d999643d3614BCf46111792d5751a0A2A614581"

with open(artifact_path) as f:
    contract_json=json.load(f)
    contract_abi=contract_json['abi']

contract=web3.eth.contract(address=contract_address,abi=contract_abi)
print('connected with blockchain')

# msg=input('Enter message: ')
# tx_hash=contract.functions.storeMessage(msg).transact()
# web3.eth.waitForTransactionReceipt(tx_hash)
# print('Msg stored in Blockchain')

data=contract.functions.viewUsers().call()
print(data)

data=contract.functions.loginUser('0x66cD55bd400d9Bff38eE7C6f5f8E06D782973489',1234).call()
print(data)