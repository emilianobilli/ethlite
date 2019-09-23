from Abi import AbiEncoder
from Transaction import Transaction
from Account import Account
from JsonRpc import JsonRpc


class ContractFunction(object):

  valid_kwargs = ['from', 'value', 'account', 'gasPrice', 'gasLimit']

  def __init__(self,signature,inputs,ouputs,stateMutability,payable,constant,contract):
    self.contract = contract

    self.signature = signature
    self.inputs = inputs
    self.outputs = ouputs
    self.stateMutability = stateMutability
    self.payable = payable
    self.constant = constant

  @classmethod
  def from_abi(cls, abi, contract):
    if abi['type'] != 'function':
      raise TypeError('ContractFunction.from_abi(): Invalid abi, expect type function')

    signature = AbiEncoder.function_signature(abi['name'], [i['type'] for i in abi['inputs'] ])
    return cls(signature,abi['inputs'],abi['outputs'],abi['stateMutability'],abi['payable'],abi['constant'],contract)

  def rawTransaction(self,*args,**kwargs):
    if self.constant == True:
      '''
          Solamente las llamadas a funciones generan cambios de estado en el contrato pueden
          generar transacciones
      '''
      pass
        # raise

    jsonrpc_valid = True if isinstance(self.contract.jsonrpc_provider,JsonRpc) else False

    if 'value' in kwargs and self.payable == False:
      raise ValueError('rawTransaction(): value received to a non-payable function')

    if 'account' in kwargs:
      if isinstance(kwargs['account'],Account):
        account = kwargs['account']
      elif isinstance(kwargs['account'],int):
        account = Account(kwargs['account'])
      elif isinstance(kwargs['account'],str) and kwargs['account'].startswith('0x'):
        account = Account.fromhex(kwargs['account'])
      else:
        raise TypeError('rawTransaction(): Expect a private_key in one of these formats-> int, hextring or Account() instance')          
    else:
      '''
        En este punto, si no se pasa la account por parametro
        hay que revisar si el contrato tiene la variable account para firmar la 
        transaccion con ella
      '''
      if self.contract.account is not None and isinstance(self.contract.account,Account):
        account = self.contract.account
      else:
        raise Exception('rawTransaction(): Unable to found a valid way to sign() transaction')  


    if 'from' in kwargs and kwargs['from'].lower() != account.addr.lower():
      '''
        Se envio el argumento from y no concuerda con la 
        direccion de la cuenta
      '''
      raise ValueError('rawTransaction(): "Account.addr" and "from" argument are distinct')

    arguments = [i['type'] for i in self.inputs]
    data = AbiEncoder.encode(arguments, args)

    tx = Transaction()

    if 'nonce' in kwargs:
      tx.nonce = kwargs['nonce']
    else:
      if jsonrpc_valid:
        tx.nonce = self.contract.jsonrpc_provider.eth_getTransactionCount(self.contract.account.addr,'latest')['result']
      else:
        #raise
        pass

    if self.payable == True and self.stateMutability == 'payable' and 'value' in kwargs:
      tx.value = kwargs['value']
    else:
      tx.value = 0

    tx.to = self.contract.address
    tx.data = self.signature + data
  
    if 'gasPrice' in kwargs:
      tx.gasPrice = kwargs['gasPrice']
    else:
      tx.gasPrice = self.contract.default_gasPrice
    
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Only for Kovan -> Change
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    tx.chainId = 42


    if 'gasLimit' in kwargs:
      tx.gasLimit = kwargs['gasLimit']
    else:
      if jsonrpc_valid:
        tx.gasLimit = self.contract.jsonrpc_provider.eth_estimateGas(tx.to_dict(signature=False, hexstring=True))['result']
      else:
        # raise
        pass

    return tx.sign(account)

  def commit(self, *args, **kwargs):
    jsonrpc_valid = True if isinstance(self.contract.jsonrpc_provider,JsonRpc) else False
    if jsonrpc_valid:
      rawTransaction = self.rawTransaction(*args,**kwargs)
      return self.contract.jsonrpc_provider.eth_sendRawTransaction(rawTransaction)['result']
    else:
      # raise
      pass

  def call(self, *arg, **kwargs):
    jsonrpc_valid = True if isinstance(self.contract.jsonrpc_provider,JsonRpc) else False
    if jsonrpc_valid:

      arguments = [i['type'] for i in self.inputs]
      data = self.signature + AbiEncoder.encode(arguments, args)
      
      result = self.contract.jsonrpc_provider.eth_call({'to': self.contract.address, 'data': data},'latest')['result']
      print(result)
    else:
      # raise
      pass

  def __call__(self,*args, **kwargs):
    if self.constant == False:
      return self.commit(*args,**kwargs)



class Contract(object):
  def __init__(self,address,abi):
    self.address = address
    self.abi = abi
    if self.abi is not None:
      self.__load_abi()
    
  def __load_abi(self):
    for attibute in self.abi:
      if attibute['type'] == 'function':
        setattr(self,attibute['name'],ContractFunction.from_abi(attibute,self))


  @property
  def jsonrpc_provider(self):
    return self.__jsonrpc_provider
  
  @jsonrpc_provider.setter
  def jsonrpc_provider(self, jsonrpc_provider):
    self.__jsonrpc_provider = JsonRpc(jsonrpc_provider)
  
  @property
  def account(self):
    return self.__account
  
  @account.setter
  def account(self, account):
    if isinstance(account,Account):
      self.__account = account
    elif isinstance(account,int):
      self.__account = Account(account)
    elif isinstance(account,str) and account.startswith('0x'):
      self.__account = Account.fromhex(account)
    else:
      raise TypeError('account: expect a int, hexstring or Account instance')


if __name__ == '__main__':
  import json
  address = '0xE8A3AF60260c4d5226ac6fC841A0AFD65BB4B4f1'
  abi = json.loads('[{"constant":false,"inputs":[{"name":"u","type":"uint256"},{"name":"i","type":"int256"}],"name":"change","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getValues","outputs":[{"name":"","type":"uint256"},{"name":"","type":"int256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"uint256"}],"name":"change_uint","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"val","type":"int256"}],"name":"change_int","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"changer","type":"address"},{"indexed":false,"name":"u","type":"uint256"}],"name":"UintChange","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"changer","type":"address"},{"indexed":false,"name":"u","type":"int256"}],"name":"IntChange","type":"event"}]')
  contract = Contract(address,abi)
  contract.jsonrpc_provider = 'https://kovan.infura.io'
  contract.getValues()