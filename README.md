# ethlite - Ethereum Lite Client Library
A tiny web3/python alternative to interact with an ethereum compatible blockchain

## Getting started
```
ToDO
```

## Transaction 

### Create a transaction

```
from ethlite.Transaction import Transanction

tx = Transaction()
tx.nonce = 9
tx.gasLimit = 21000
tx.gasPrice = 20 * 10**9
tx.value = 10**18
tx.data = ''
tx.to = '0x3535353535353535353535353535353535353535'

```
### Methods

#### tx.to_dict(signature=True,hexstring=False)

Return a dict instance of the transaction. 

- signature: if True return the attributes/fields v, r, s
- hexstring: if True return a integer values of the transaction enconding in hexstring (starting with 0x)

```
tx.to_dict(signature=False,hexstring=T)

{
  'nonce': '0x9', 
  'gasPrice': '0x4a817c800', 
  'gas': '0x5208', 
  'to': '0x3535353535353535353535353535353535353535', 
  'value': '0xde0b6b3a7640000', 
  'data': ''
}
```

