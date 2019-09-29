from ethlite.Contracts import Contract
from json import loads
from random import randint
from time import sleep

'''
  Abi and address
'''
address = '0xE8A3AF60260c4d5226ac6fC841A0AFD65BB4B4f1'
abi = loads('[{"constant":false,"inputs":[{"name":"u","type":"uint256"},{"name":"i","type":"int256"}],"name":"change","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getValues","outputs":[{"name":"","type":"uint256"},{"name":"","type":"int256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"uint256"}],"name":"change_uint","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"int256"}],"name":"change_int","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"changer","type":"address"},{"indexed":false,"name":"u","type":"uint256"}],"name":"UintChange","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"changer","type":"address"},{"indexed":false,"name":"u","type":"int256"}],"name":"IntChange","type":"event"}]')

''' 
  Contract
'''
contract = Contract(address,abi,jsonrpc_provider='https://kovan.infura.io')
#contract.jsonrpc_provider = 'https://kovan.infura.io'
#contract.account = 0x7a75b6b7d87cf3f0d9da5868c7c9dfb53b32175f09563b75159391c071d07bae

'''
  Start Interact
'''
values = contract.functions.getValues.call()

print('Values:', values)

'''
  Other way to call a view function:
'''
values = contract.functions.getValues()

print('Values without call():', values)

'''
  Change Value
'''
u = randint(1,100000000)
i = -randint(1,100000000)

print('New values to set:', u,i)

try:
  txComited = contract.functions.change(u,i,gasPrice=21000000000)
  print('Tx:',txComited)
  '''
    Waiting receipt (finish)
  '''
  receipt = txComited.receipt()
  while receipt == None:
    sleep(1)
    receipt = txComited.receipt()

  print('Receipt', receipt)

  '''
    Get events from receipt
  '''
  events = contract.events.parse_log_data(receipt['logs'])
  print('Events', events)
except Exception as e:
  print(str(e))





'''
  Query for a particular event
'''
event = contract.events.UintChange(fromBlock='0x0')

'''
  Print historical values
'''
print('Get all UintChange Events')
i = 0
for e in event:
  print('Value', i, e.u, 'Changer:', e.changer)
  i = i + 1


'''
  Query for a particular event
'''
event = contract.events.IntChange(fromBlock='0x0')

'''
  Print historical values
'''
print('Get all IntChange Events')
i = 0
for e in event:
  print('Value', i, e.u, 'Changer:', e.changer)
  i = i + 1


