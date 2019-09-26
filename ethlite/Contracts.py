from Abi import AbiEncoder
from Transaction import Transaction
from Account import Account
from JsonRpc import JsonRpc



class EventLogDict:
  def __init__(self,blockHash,transactionHash,blockNumber):
    self.blockHash = blockHash
    self.transactionHash = transactionHash
    self.blockNumber = blockNumber

  def __repr__(self):
    return 'EventLogDict(%s)' % str(dict(self))

  def __iter__(self):
    yield 'blockHash', self.blockHash

  def __getitem__(self,key):
    return getattr(self,key)
  

class EventSet:
  valid_kwargs = ['fromBlock', 'toBlock', 'blockHash']

  def __init__(self,contract):
    self.contract = contract

  def commit_filter_query(self,filter_query,**kwargs):
    for kw in kwargs:
      if kw in self.valid_kwargs:
        filter_query[kw] = kwargs[kw]
    
    jsonrpc_valid = True if isinstance(self.contract.jsonrpc_provider,JsonRpc) else False

    if jsonrpc_valid:
      result = self.contract.jsonrpc_provider.eth_getLogs(filter_query)

    return result

  def all(self,**kwargs):  
    filter_query = { 
      'address': self.contract.address,
    }
    return self.commit_filter_query(filter_query,**kwargs)


class Event(EventSet):
  def __init__(self, abi=None, contract=None):

    if abi is None:
      raise ValueError('Event(): abi can not be None')

    if abi['type'] != 'event':
      raise TypeError('Event(): Invalid abi type, expected -> event')

    self.abi = abi
    self.name = abi['name']
    self.indexed = []
    self.inputs = []
    self.contract = contract

    inputs = abi['inputs']
    for i in inputs:
      if i['indexed']:
        self.indexed.append(i['type'])
      else:
        self.inputs.append(i['type'])

    self.signature = AbiEncoder.event_hash(self.name, self.indexed + self.inputs)

  def parse_data(self,data):
    pass

  def topic(self, *indexed):
    if indexed is not ():
      n = len(*indexed)
      topics = AbiEncoder.encode_event_topic(self.indexed[:n],*indexed)
    else:
      topics = []
    topics = [self.signature] + topics
    return topics

  def __call__(self,*indexed,**kwargs):

    filter_query = { 
      'address': self.contract.address,
      'topics': self.topic(*indexed),
    }
    return self.commit_filter_query(filter_query,**kwargs)
  
  def all():
    pass

'''
class EventParser:
  def __init__(self,abi=None):
    if abi is not None:
      

      self.name = abi['name']
      self.inputs = abi['inputs'] # -> with type,indexed and name
      self.signature = AbiEncoder.event_hash(self.name, [i['type'] for i in self.inputs] )

  @staticmethod
  def count_indexed(inputs):
    n = 0
    for i in inputs:
      if i['indexed']:
        n = n + 1
    return n

  def fromLog(self,log):
    if 'topics' in log and len(log['topics']) == self.count_indexed(self.inputs) + 1:
      topics = log['topics']
      if topics[0] != signature:
        pass # raise invalid Log

      event = Event()
      setattr(event,'name',self.name)

      for i in range(1,self.count_indexed()-1):
        if self.inputs[i]['type'] == 'str'or self.inputs[i]


      if 'data' in log and (log['data'] != '' or log['data'] != '0x'):

'''

class ContractFunction(object):

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
      raise TypeError('ContractFunction.from_abi(): Invalid abi, expected type -> function')

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
      if len(arguments) != 0:
        data = self.signature + AbiEncoder.encode(arguments, args)
      else:
        data = self.signature

      result = self.contract.jsonrpc_provider.eth_call({'to': self.contract.address, 'data': data},'latest')['result']

      outputs = [o['type'] for o in self.outputs ]
      return AbiEncoder.decode(outputs,result[2:])

    else:
      # raise
      pass

  def __call__(self,*args, **kwargs):
    if self.constant == False:
      return self.commit(*args,**kwargs)
    else:
      return self.call(*args,**kwargs)


class FunctionSet(object):
  pass

class Contract(object):
  def __init__(self,address,abi):
    self.address = address
    self.abi = abi
    self.events = EventSet(self)
    self.functions = FunctionSet()

    for attibute in self.abi:
      if attibute['type'] == 'function':
        setattr(self.functions,attibute['name'],ContractFunction.from_abi(attibute,self))

      if attibute['type'] == 'event':
        setattr(self.events,attibute['name'],Event(attibute,self))


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
  o = contract.functions.getValues.call()
  print(o)
  print(dir(contract.events))
  print(contract.events.all(fromBlock='0x0'))
  e = EventLogDict(1,2,3)
  print(e['blockHash'])
  print(dict(e))
