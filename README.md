# ethlite - Ethereum Lite Client Library
A tiny web3/python alternative to interact with any ethereum compatible blockchain

## Getting started
```
ToDO
```

## Contents

- [Transaction](#transaction "https://github.com/emilianobilli/ethlite#transaction")
- [Account](#account "https://github.com/emilianobilli/ethlite/blob/master/README.md#account")
- [JsonRpc]
- [Contract]



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
- **hexstring**: if True -> return a integer values of the transaction enconding in hexstring (starting with 0x)

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

- **private_key**: a private key

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
Perform a sign of a digested message

**Params**
- digest: The hash to be signed

```
>> to_sign = keccak_256(bytearray.fromhex('ec098504a817c800825208943535353535353535353535353535353535353535880de0b6b3a764000080018080'))
>> to_sign.hexdigest()
'daf5a779ae972f972197303d7b574746c7ef83eadac0f2791ad23db92e4c8e53'
>> addr.sign_digest(to_sign.digest())
5f3d10a56c633f476ffffe3595353e480611dba01124fd3d5334d0faacf14b5028ee8c85a63ae513a58871cba502f8077f79581460e76dbd272fff9a9aad76bc
```
