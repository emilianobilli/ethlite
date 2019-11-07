from warnings import warn
from .Abi import dec_uint
from .Account import Account
from .JsonRpc import JsonRpc
from .JsonRpc import JsonRpcError
from .Transaction import Transaction
from .NetworkUtil import CommittedTransaction

class Wallet:
  def __init__(self, http_provider):
    self.account = None
    self.jsonrpc_provider = JsonRpc(http_provider)
    self.default_gasPrice = 20 * 10**9
    try:
      response = self.jsonrpc_provider.eth_chainId()
      if 'result' in response:
        self.chainId = response['result']
      else:
        warn('jsonrcp_provider: No support eth_chainId() method')
        self.chainId = None

    except Exception as e:
      warn('jsonrpc_provider: throw ->' + str(e))
      self.chainId = None

  def import_account(self,account):
    if isinstance(account,Account):
      self.account = account
    elif isinstance(account,int):
      self.account = Account(account)
    elif isinstance(account,str) and account.startswith('0x'):
      self.account = Account.fromhex(account)
    else:
      raise TypeError('import_account(): Expect a private_key in one of these formats-> int, hextring or Account() instance')          

  def from_paraphrase(self,paraphrase):
    raise NotImplementedError()

  def new_random(self, seed=None):
    raise NotImplementedError()

  @property
  def balance(self):
    if self.account is None:
      raise AttributeError('Impossible to get balance, please first import an account')
    
    response = self.jsonrpc_provider.eth_getBalance(self.account.addr,'latest')
    if 'result' in response:
      return dec_uint(response['result'])
    else:
      raise JsonRpcError(str(response))
  
  @property
  def blockNumber(self):
    if isinstance(self.__jsonrpc_provider,JsonRpc):
      response = self.jsonrpc_provider.eth_blockNumber()
      if 'result' in response:
        return dec_uint(response['result'])
      else:
        raise JsonRpcError(str(response))
    else:
      return None

  @balance.setter
  def balance(self,balance):
    raise AttributeError('Impossible to set balance, please buy or ask someone to send you a little')
  
  def send(self,value, **kwargs):
    if self.account is None:
      raise AttributeError('Impossible to send founds, please first import an account')

    tx = Transaction()

    if 'nonce' in kwargs:
      tx.nonce = kwargs['nonce']
    else:
      response = self.jsonrpc_provider.eth_getTransactionCount(self.account.addr,'latest')
      if 'result' in response:
        tx.nonce = response['result']
      else:
        raise JsonRpcError(str(response))
    
    tx.gasLimit = 21000

    if 'gasPrice' in kwargs:
      tx.gasPrice = kwargs['gasPrice']
    else:
      tx.gasPrice = self.default_gasPrice

    if 'to' in kwargs:
      tx.to = kwargs['to']
    else:
      raise ValueError('send(): Mandatory parameter is missing -> to')

    tx.value = value

    rawTransaction = tx.sign(self.account)

    response = self.jsonrpc_provider.eth_sendRawTransaction(rawTransaction)

    if 'result' not in response:
      raise JsonRpcError(str(response))
    
    return CommittedTransaction(response['result'],self.jsonrpc_provider)

      
