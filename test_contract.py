from ethlite.Contracts import Contract

import json
address = '0xE8A3AF60260c4d5226ac6fC841A0AFD65BB4B4f1'
abi = json.loads('[{"constant":false,"inputs":[{"name":"u","type":"uint256"},{"name":"i","type":"int256"}],"name":"change","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getValues","outputs":[{"name":"","type":"uint256"},{"name":"","type":"int256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"uint256"}],"name":"change_uint","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"int256"}],"name":"change_int","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"changer","type":"address"},{"indexed":false,"name":"u","type":"uint256"}],"name":"UintChange","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"changer","type":"address"},{"indexed":false,"name":"u","type":"int256"}],"name":"IntChange","type":"event"}]')
contract = Contract(address,abi)
contract.jsonrpc_provider = 'https://kovan.infura.io'
o = contract.functions.getValues.call()
print(o)
print(dir(contract.events))
print(contract.events.all(fromBlock='0x0'))

for event in contract.events.all(fromBlock='0x0'):
    print(event.event_name)
    print(event.changer)

#e = EventLogDict('Croto',1,2,3)
#print(e['blockHash'])
#print(dict(e))