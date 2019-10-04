# ethlite - Ethereum Lite Client Library
A tiny web3/python alternative to interact with any ethereum compatible blockchain

## Getting started

### Requiremetns

- pysha3
- six

### Install

```
  $ pip install ethlite
```


## Contents

- [Contracts](#contracts "https://github.com/emilianobilli/ethlite/blob/master/README.md#contracts")
- [Transaction](#transaction "https://github.com/emilianobilli/ethlite#transaction")
- [Account](#account "https://github.com/emilianobilli/ethlite/blob/master/README.md#account")
- [Wallet](#wallet "https://github.com/emilianobilli/ethlite/blob/master/README.md#wallet")

***

## Contracts

Class to intereact with smart contracts

### Create a new contract instance

To create a new contract instance it is necessary to know the **address** and the **ABI** contract. After initialization, you must assign the **jsonrpc_provider** attribute with the url of the node with which we will interact
```
>> from ethlite.Contracts import Contract
>> from json import loads
>> 
>> address = '0xE8A3AF60260c4d5226ac6fC841A0AFD65BB4B4f1'
>> abi = loads('[{"constant":false,"inputs":[{"name":"u","type":"uint256"},{"name":"i","type":"int256"}],"name":"change","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getValues","outputs":[{"name":"","type":"uint256"},{"name":"","type":"int256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"uint256"}],"name":"change_uint","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"int256"}],"name":"change_int","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"changer","type":"address"},{"indexed":false,"name":"u","type":"uint256"}],"name":"UintChange","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"changer","type":"address"},{"indexed":false,"name":"u","type":"int256"}],"name":"IntChange","type":"event"}]')


>> contract = Contract(address,abi)
>> contract.jsonrpc_provider = 'https://kovan.infura.io'

# Other way to init it with only one call
>> contract = Contract(address,abi,jsonrpc_provider='https://kovan.infura.io')

```
If the contract instance is created (not exception is thrown), each functions and events of the contract are created as a instance of the class **ContractFunction** and **Event** respectively as attributes of **functions** and **events**.

- In contract.events are defined all the events as Event() 
- In contract.functions are defined all the functions as ContractFunction()

### Call "View" functions

The view functions are those that do not change the status in the smart contract. For example to call the function **getValues()**

```
>> ret = contract.functions.getValues()
or
>> ret = contract.functions.getValues.call()
```

The return value **ret** is a [] with the values in same order that are returned in the smart contract

If the "view" function expect arguments, is possible do it in two ways.

```
>> contract.functions.functionName(arg_1,arg_2,arg_3,...,arg_N)
or 
>> contract.functions.functionName.call(arg_1,arg_2,arg_3,...,arg_N)
```

### Call function that modify the state of the smart contract

To proceed with call that modify the state of the smart contract, first is necessary to attach a Account

```
>> contract.account = 0x4646464646464646464646464646464646464646464646464646464646464646
or
>> contract.account = '0x4646464646464646464646464646464646464646464646464646464646464646'
or 
>> account = Account(0x4646464646464646464646464646464646464646464646464646464646464646)
>> contract.account = account
```

When account has been attached to the contract, is possible to proceed with the call.

```
>> from random import randint

>> u = randint(1,100000000)
>> i = -randint(1,100000000)
>> tx = contract.functions.change(u,i,gasPrice=21000000000)
or
>> tx = contract.functions.change.commit(u,i,gasPrice=2000000000)

```

#### Arguments/Parameters

The arguments are passed in the same way as a **view** function, but this call expect some extra arguments in the **kwargs**.

The list of valid **kwargs** are:
- **gasPrice**: If this parameter is missing, the contract do tha call with **self.default_gasPrice**
- **gasLimit**: If this parameter is missing, it is estimated automatically before the call
- **value**: If the funcions is payable
- **chainId**
- **nonce**: If this parameter is missing, it is estimated automatically before de call

#### Return Value

The return value of this kind of function (that change the status in the smart contract) is an instance of class CommittedTransaction. 
The way to know the status of the transaction is call the method **receipt()**. This method return **None** until the transaction is confirmed and then return a receipt.

```
>> from time import sleep
>>
>> tx = contract.functions.change(u,i,gasPrice=21000000000)
>> '''
>>   Waiting receipt (finish)
>> '''
>> receipt = tx.receipt()
>> while receipt == None:
>>  sleep(1)
>>  receipt = tx.receipt()
>>
>> print('Transaction Status:', receipt['status'])

```

### Query to contract's events

When the contract is initialized with the abi, all events are attributes of the contract's attribute **events**. To query a particular event you must specify the name of the event, if it has an indexed parameter or more you must provide as an argument if you want filter for that topic.


#### Query for a particular event. e.g IntChange

```
>> logs = contract.events.IntChange(fromblock=0x0)
```

#### Query for a particular event. e.g IntChange but filter with the first topic (address indexed addr)

```
>> logs = contract.events.IntChange('0x7113fFcb9c18a97DA1b9cfc43e6Cb44Ed9165509',fromblock=0x0)
```

#### Query for all events that's occurred between the block 0 and the block 100000

```
>> logs = contract.events.all(fromblock=0x0,toBlock=0x2710)
```

#### Parse logs in the receipt

```
>> receipt = tx.receipt()
>> while receipt == None:
>>  sleep(1)
>>  receipt = tx.receipt()
>>
>> logs = contract.events.parse_log_data(receipt['logs'])
```

#### Return value

The return value of any event query or parsed from the receipt is a list of **EventLogDict** objects. 
Each one has:

- **event_name**
- **blockHash**
- **transactionHash**
- **blockNumber**
- **All of the event parameters as a list**
- **All of the event parameters as a key/value and object attribute**


***


## Transaction 

Class to create transactions

### Create a transaction

```
from ethlite.Transaction import Transanction

>> tx = Transaction()
>> tx.nonce = 9
>> tx.gasLimit = 21000
>> tx.gasPrice = 20 * 10**9
>> tx.value = 10**18
>> tx.data = ''
>> tx.to = '0x3535353535353535353535353535353535353535'

# Other way to initialize the tx
>> tx = Transaction(nonce=9, gasLimit=21000, gasPrice=20*10**9, value=10**18, data='', to='0x3535353535353535353535353535353535353535')
```
### Methods

#### to_dict(signature=True,hexstring=False)

Return a dict instance of the transaction. 

**Params:**
- **signature**: if True -> return the attributes/fields v, r, s
- **hexstring**: if True -> return the integer values of the transaction enconding in hexstring (starting with 0x)

```
>> tx.to_dict(signature=False,hexstring=True)

{
  'nonce': '0x9', 
  'gasPrice': '0x4a817c800', 
  'gas': '0x5208', 
  'to': '0x3535353535353535353535353535353535353535', 
  'value': '0xde0b6b3a7640000', 
  'data': ''
}
```

#### sign(<private_key>)

Return a RLP encoded of the signed transction

**Params:**

- **private_key**: a private key, can be in one these formats: Account instance, integer in (base 10 or in base 16) or hexstring (starting with 0x) 

```
>> rlp_encoded = tx.sign('0x4646464646464646464646464646464646464646464646464646464646464646')
>> print(rlp_encoded)
'0xf86b098504a817c800825208943535353535353535353535353535353535353535880de0b6b3a7640000801ba03b5da84dcc0783a0aa7a6fb580cb47004c7621b9945befb8e397ad5e97458ea99fee048566d0ce3144fe16da44ca8fbeef6f64001c2b3b3056daff9288fd3f05'
```

*If **chainId** is setted in the transaction the signature is agrees with eip155* (https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md)

```
>> tx.chainId = 1
>> rlp_encoded = tx.sign('0x4646464646464646464646464646464646464646464646464646464646464646')

>> print(tx)
Transaction({'nonce': 9, 'gasPrice': 20000000000, 'gas': 21000, 'to': '0x3535353535353535353535353535353535353535', 'value': 1000000000000000000, 'data': '', 'v': 38, 'r': 43077613174109092491961660322778806267205871822317054604199428521941921778512, 's': 18513993392415436760536700545833252249819770065433633383952513597988743771836})

>> print(rlp_encoded)
'0xf86c098504a817c800825208943535353535353535353535353535353535353535880de0b6b3a76400008026a05f3d10a56c633f476ffffe3595353e480611dba01124fd3d5334d0faacf14b50a028ee8c85a63ae513a58871cba502f8077f79581460e76dbd272fff9a9aad76bc'
```

***

## Account

Class to manipulate private/public key

**ToDo: compliance with eip55** (https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md)

Actual work according with the yellow paper -> A(pr) = B(96..255)(KEC(ECDSAPUBKEY(pr)))


### Import private key

```
>> from ethlite.Account import Account

>> addr = Account(0x4646464646464646464646464646464646464646464646464646464646464646)
>> print(addr.addr)
'0x9d8a62f656a8d1615c1294fd71e9cfb3e4855a4f'

```

### Methods

#### sign(message)
Perform a keccak_256(message) and them sign it with the private key. Return an instance of *Sign()*  representing a signature:

**Params**
- message: The bytearray to be signed

```
>> addr.sign(bytearray.fromhex('ec098504a817c800825208943535353535353535353535353535353535353535880de0b6b3a764000080018080'))

5f3d10a56c633f476ffffe3595353e480611dba01124fd3d5334d0faacf14b5028ee8c85a63ae513a58871cba502f8077f79581460e76dbd272fff9a9aad76bc
```

#### sign_digest(digest)
Perform a signature of a digested message

**Params**
- digest: The hash to be signed

```
>> to_sign = keccak_256(bytearray.fromhex('ec098504a817c800825208943535353535353535353535353535353535353535880de0b6b3a764000080018080'))
>> to_sign.hexdigest()
'daf5a779ae972f972197303d7b574746c7ef83eadac0f2791ad23db92e4c8e53'
>> addr.sign_digest(to_sign.digest())
5f3d10a56c633f476ffffe3595353e480611dba01124fd3d5334d0faacf14b5028ee8c85a63ae513a58871cba502f8077f79581460e76dbd272fff9a9aad76bc
```
***

## Wallet

Class to check and manipulate account balance

### Create a Wallet instance

```
>> from ethlite_ebilli.Wallet import Wallet

>> wallet = Wallet('https://kovan.infura.io/')
```

To initialize the instance is necessary pass as parameter the http/s provider

### Attach / import Account

The next step is import an account

```
>> wallet.import_account(0x4646464646464646464646464646464646464646464646464646464646464646)
```

### Check balance and Send a Value

```
>> balance = wallet.balance
>> result = wallet.send(100000,to='0xa74b20233bf2cE1DfE9E66448316e61Bad78133E')
```
**The fist parameter is the amount to send in wei**

The valid **kwargs** for send() are:

- **nonce**
- **gasPrice**: If this value is omitted, the call use default_gasPrice -> 20 * 10 ** 9
- **to**

