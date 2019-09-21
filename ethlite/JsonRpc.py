from json import dumps
import requests

class JsonRpc:

  headers = {'content-type': 'application/json'}
  default_timeout = 10

  def __init__(self, node):
    self.node = node

  @classmethod
  def get_body_dict(cls):
    return {
        'jsonrpc': '2.0',
        'method': '',
        'params': [],
        'id': 1
    }

  def __str__(self):
    return self.node
  
  def __repr__(self):
    return 'JsonRpc(%s)' % self.node

  def doPost(self,data,timeout=None):
    return requests.post(
      self.node,
      data=data,
      headers=headers,
      timeout=self.default_timeout if timeout is None else timeout
    ).json()


  def web3_sha3(self,hexstring):
    '''
      Returns Keccak-256 (not the standardized SHA3-256) of the given data.
    '''
    data = self.get_body_dict()
    data['method'] = 'web3_sha3'
    data['params'].append(hexstring)
    return self.doPost(dumps(data))
  
  def eth_blockNumber(self):
    '''
      Returns the number of most recent block.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_blockNumber'
    return self.doPost(dumps(data))

  def eth_getBalance(self, address, tag):
    '''
      Returns the balance of the account of given address.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_getBalance'
    data['params'].append(address)
    data['params'].append(tag)
    return self.doPost(dumps(data))

  def eth_getTransactionCount(self,address,tag):
    '''
      Returns the number of transactions sent from an address.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_getTransactionCount'
    data['params'].append(address)
    data['params'].append(tag)
    return self.doPost(dumps(data))

  def eth_sendRawTransaction(self,data):
    '''
      Creates new message call transaction or a contract creation for signed transactions.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_sendRawTransaction'
    data['params'].append(data)
    return self.doPost(dumps(data))

  def eth_call(self, obj, tag):
    '''
      Executes a new message call immediately without creating a transaction on the block chain.
    '''

    data = self.get_body_dict()
    data['method'] = 'eth_call'
    data['params'].append(obj)
    data['params'].append(tag)
    return self.doPost(dumps(data))

  def eth_estimateGas(self, obj):
    '''
      Generates and returns an estimate of how much gas is necessary to allow the transaction to complete.
      The transaction will not be added to the blockchain. Note that the estimate may be significantly
      more than the amount of gas actually used by the transaction, for a variety of reasons including 
      EVM mechanics and node performance.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_estimateGas'
    data['params'].append(obj)
    return self.doPost(dumps(data))



