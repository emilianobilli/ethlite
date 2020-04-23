from warnings import warn
from .Abi import dec_uint
from .JsonRpc import JsonRpc
from .JsonRpc import JsonRpcError

class BlockDataDict(object):
  '''
    Represents the parsed return of the Block data. 
  '''
  integer_fields = ["nonce", "number", "difficulty", "totalDifficulty", "size", "gasLimit", "gasUsed", "timestamp"]

  def __init__(self, data):
    for key in data.keys():
      if key in self.integer_fields:
        setattr(self,key,dec_uint(data[key]))
      else:
        setattr(self,key,data[key])

  def __repr__(self):
    return 'BlockLogDict(%s)' % str(dict(self))

  def __iter__(self):
    for k in self.__dict__.keys():
      if k == "integer_fields":
        continue
      yield k, self.__dict__[k]

  def __getitem__(self,key):
    return getattr(self,key)

class TransactionDict(object):
  '''
    Represent the transction
  '''
  integer_fields = ["blockNumber", "gas", "gasPrice", "value", "nonce"]
  def __init__(self, data):
    for key in data.keys():
      if key in self.integer_fields:
        setattr(self,key,dec_uint(data[key]))
      else:
        setattr(self,key,data[key])

  def __repr__(self):
    return 'TransactionDict(%s)' % str(dict(self))

  def __iter__(self):
    for k in self.__dict__.keys():
      if k == "integer_fields":
        continue
      yield k, self.__dict__[k]

  def __getitem__(self,key):
    return getattr(self,key)

class CommittedTransaction(object):
  def __init__(self, transactionHash, jsonrpc_provider):
    self.transactionHash = transactionHash
    self.jsonrpc_provider = jsonrpc_provider
    self.receipt_returned = None

  def __str__(self):
    return 'CommittedTransaction(%s)' % self.transactionHash

  def receipt(self):
    uint_keys = ['blockNumber', 'cumulativeGasUsed', 'gasUsed', 'status', 'transactionIndex']

    if self.receipt_returned != None:
      return self.receipt_returned

    response = self.jsonrpc_provider.eth_getTransactionReceipt(self.transactionHash)
    if 'result' in response:
      if response['result'] == None:
        return None

      receipt = response['result']
      for key in uint_keys:
        receipt[key] = dec_uint(receipt[key])
    
      self.receipt_returned = receipt
      return receipt
    else:
      raise JsonRpcError(str(response)) 



class NetworkUtil(object):
  '''
    A class to contain all network attributes and contract's methods/functions
  '''
  def __init__(self,provider=None,basicauth=()):
    if provider is not None:
      self.jsonrpc_provider = provider
      if basicauth != ():
        self.jsonrpc_provider.auth = basicauth

    self.__chainId = None

  def getTransactionByHash(self, txHash):
    if isinstance(self.__jsonrpc_provider, JsonRpc):
      if isinstance(txHash, str):
        if not txHash.startswith('0x'):
          txHash = '0x' + txHash
        response = self.jsonrpc_provider.eth_getTransactionByHash(txHash)
      else:
        raise TypeError('getTransactionByHash(): txHash must be a hexstring')
      if 'result' in response:
        return TransactionDict(response['result'])
    else:
      raise TypeError('getTransactionByHash(): unable to found a valid JsonRpc Provider')

  def getBlockByNumber(self, blockNumber, withTx=False):
    if isinstance(self.__jsonrpc_provider, JsonRpc):
      if isinstance(blockNumber, str):
        if blockNumber.startswith('0x') or blockNumber in ["earliest","latest","pending"]:
          response = self.jsonrpc_provider.eth_getBlockByNumber(blockNumber, withTx)
        else:
          raise TypeError('getBlockByNumber(): blockNumber must be a hexstring or an integer')
      elif isinstance(blockNumber, int):
        response = self.jsonrpc_provider.eth_getBlockByNumber(hex(blockNumber), withTx)
      else:
        raise TypeError('getBlockByNumber(): blockNumber must be a hexstring or an integer')

      if 'result' in response:
        return BlockDataDict(response['result'])

  @property
  def chainId(self):
    if self.__chainId != None:
      return self.__chainId
    else:
      try:
        response = self.jsonrpc_provider.eth_chainId()
        if 'result' in response:
          self.__chainId = response['result']
        else:
          warn('jsonrpc_provider: No support eth_chainId() method -> ' + str(response))
          self.__chainId = None
      except Exception as e:
        warn('jsonrpc_provider: throw ->' + str(e))
        self.__chainId = None
      return self.__chainId
    
  @property
  def blockNumber(self):
    if isinstance(self.__jsonrpc_provider, JsonRpc):
      response = self.jsonrpc_provider.eth_blockNumber()
      if 'result' in response:
        return dec_uint(response['result'])
      else:
        raise JsonRpcError(str(response))
    else:
      return None
      
  @blockNumber.setter
  def blockNumber(self, blockNumber):
    raise AttributeError('Only the network can set a blockNumer')

  @property
  def jsonrpc_provider(self):
    return self.__jsonrpc_provider

  @jsonrpc_provider.setter
  def jsonrpc_provider(self, jsonrpc_provider):
    if isinstance(jsonrpc_provider, JsonRpc):
      self.__jsonrpc_provider = jsonrpc_provider
    else:
      self.__jsonrpc_provider = JsonRpc(jsonrpc_provider)

