from warnings import warn
from .Abi import dec_uint
from .JsonRpc import JsonRpc
from .JsonRpc import JsonRpcError

class NetworkUtil:
  '''
    A class to contain all network attributes and contract's methods/functions
  '''
  def __init__(self,provider=None,basicauth=()):
    if provider is not None:
      self.jsonrpc_provider = provider
      if basicauth is not ():
        self.jsonrpc_provider.auth = basicauth

    self.__chainId = None

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
