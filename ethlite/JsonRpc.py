from json import dumps
from re import compile
from re import match
from re import IGNORECASE

import requests

class JsonRpcError(Exception):
  pass


valid_url_re = compile(
  r'^(?:http)s?://'  # http:// or https://
  r'(?:[^:@]*?:[^:@]*?@|)'  # basic auth
  r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
  r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
  r'localhost|'  # localhost...
  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
  r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
  r'(?::\d+)?'  # optional port
  r'(?:/?|[/?]\S+)$', IGNORECASE
)


class JsonRpc(object):

  headers = {'content-type': 'application/json'}
  default_timeout = 10

  def __init__(self, node, basic_auth=None):
    if match(valid_url_re, node) is not None:
      self.session = requests.Session()
      self.node = node
      self.basic_auth = basic_auth
      self.instance_headers = {}
    else:
      raise ValueError('JsonRpc(): %s is not a valid url' % node)

  @classmethod
  def get_body_dict(cls):
    return {
        'jsonrpc': '2.0',
        'method': '',
        'params': [],
        'id': 1
    }

  @property
  def auth(self):
    return self.basic_auth
    
  @auth.setter
  def auth(self, auth):
    if isinstance(auth,tuple):
      self.basic_auth = auth
      self.session.auth = auth
    else:
      raise TypeError('auth needs to be a tuple')


  def __str__(self):
    return self.node
  
  def __repr__(self):
    return 'JsonRpc(%s)' % self.node

  def add_header(cls, key, value):
    self.instance_headers[key] = value

  def doPost(self,data,timeout=None):
    return self.session.post(
      self.node,
      data=data,
      headers={**self.headers, **self.instance_headers},
      timeout=self.default_timeout if timeout is None else timeout
    ).json()

  def net_version(self):
    data = self.get_body_dict()
    data['method'] = 'net_version'
    return self.doPost(dumps(data))

  def web3_sha3(self,hexstring):
    '''
      Returns Keccak-256 (not the standardized SHA3-256) of the given data.
    '''
    data = self.get_body_dict()
    data['method'] = 'web3_sha3'
    data['params'].append(hexstring)
    return self.doPost(dumps(data))

  def eth_chainId(self):
    data = self.get_body_dict()
    data['method'] = 'eth_chainId'
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

  def eth_getTransactionReceipt(self,txHash):
    '''
      Returns the receipt of a transaction by transaction hash.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_getTransactionReceipt'
    data['params'].append(txHash)
    return self.doPost(dumps(data))


  def eth_sendRawTransaction(self,rawTransaction):
    '''
      Creates new message call transaction or a contract creation for signed transactions.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_sendRawTransaction'
    data['params'].append(rawTransaction)
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

  def eth_getLogs(self,obj):
    '''
      Returns an array of all logs matching a given filter object.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_getLogs'
    data['params'].append(obj)
    return self.doPost(dumps(data))

  def eth_getBlockByNumber(self,blocknumber,withtx):
    '''
      Returns information about a block by block number.
    '''
    data = self.get_body_dict()
    data['method'] = 'eth_getBlockByNumber'
    data['params'].append(blocknumber)
    data['params'].append(withtx)
    return self.doPost(dumps(data))