from warnings import warn
from .Abi import AbiEncoder
from .Abi import dec_uint
from .Transaction import Transaction
from .CommitedTransaction import CommitedTransaction
from .Account import Account
from .JsonRpc import JsonRpc
from .JsonRpc import JsonRpcError


class EventLogDict:
  '''
    Represents the parsed return of the logs. Each time a contract 
    is queried for logs, it returns a list of instances of objects 
    of the EvenDictLog class
  '''
  def __init__(self,event,blockHash,transactionHash,blockNumber):
    self.event_name = event
    self.blockHash = blockHash
    self.transactionHash = transactionHash
    self.blockNumber = blockNumber

  def __repr__(self):
    return 'EventLogDict(%s)' % str(dict(self))

  def __iter__(self):
    for k in self.__dict__.keys():
      yield k, self.__dict__[k]

  def __getitem__(self,key):
    return getattr(self,key)
  

class EventBase:
  '''
    A abstract class of Events
  '''
  valid_kwargs = ['fromBlock', 'toBlock', 'blockHash']

  def __init__(self,contract):
    self.contract = contract

  def commit_filter_query(self,filter_query,**kwargs):
    for kw in kwargs:
      if kw in self.valid_kwargs:
        if (kw == 'fromBlock' or kw == 'toBlock') and isinstance(kwargs[kw],int):
          filter_query[kw] = hex(kwargs[kw])
        else:
          filter_query[kw] = kwargs[kw]
    
    jsonrpc_valid = True if isinstance(self.contract.net.jsonrpc_provider,JsonRpc) else False

    if not jsonrpc_valid:
      raise AttributeError('commit_filter_query(): Unable to found a valid jsonrpc_provider')
    
    response = self.contract.net.jsonrpc_provider.eth_getLogs(filter_query)

    if 'result' in response:
      return self.parseLogData(response['result'])
    else:
      raise JsonRpcError(str(response))

  def get_event_hash_from_log(self, log):
    return log['topics'][0]

  def parseLogData(self, logs):
    raise NotImplementedError('EventBase.parseLogData()')


class EventSet(EventBase):

  def __init__(self,contract):
    EventBase.__init__(self,contract)

  def parseLogData(self, logs):
    ret = []
    for log in logs:
      for self_event in self.__dict__.keys():
        if self_event == 'contract' or self_event == 'valid_kwargs':
          continue
        if self.__dict__[self_event].event_hash == self.get_event_hash_from_log(log):
          ret = ret + self.__dict__[self_event].parseLogData([log])

    return ret

  def rawQuery(self, rawTopics, **kwargs):
    filter_query = {}

    if hasattr(self.contract,'address'):
      filter_query['address'] = self.contract.address
    else:
      if 'address' in kwargs:
        filter_query['address'] = kwargs['address']

    filter_query['topics'] = rawTopics
    return self.commit_filter_query(filter_query,**kwargs)
  

  def getAll(self,**kwargs):
    if hasattr(self.contract,'address') or 'address' in kwargs:
      filter_query = { 
        'address': self.contract.address if hasattr(self.contract,'address') else kwargs['address'],
      }
      return self.commit_filter_query(filter_query,**kwargs)
    else:
      raise AttributeError('EventSet(): There is no specific contract to query for events')
    

class Event(EventBase):

  def __init__(self, abi=None, contract=None):

    EventBase.__init__(self,contract)

    if abi is None:
      raise ValueError('Event(): abi can not be None')

    if abi['type'] != 'event':
      raise TypeError('Event(): Invalid abi type, expected -> event')

    self.abi = abi
    self.name = abi['name']
    self.indexed = []
    self.inputs = []

    inputs = abi['inputs']

    in_order = []

    for i in inputs:
      in_order.append(i['type'])
      if i['indexed']:
        self.indexed.append(i['type'])
      else:
        self.inputs.append(i['type'])

    self.event_hash = AbiEncoder.event_hash(self.name, in_order)

  def parseLogData(self,logs):
    ret = []
    for log in logs:
      if self.event_hash == self.get_event_hash_from_log(log):
        event = EventLogDict(self.name, log['blockHash'],log['transactionHash'],dec_uint(log['blockNumber']))

        if not hasattr(self.contract,'address'):
          event.address = log['address']

        topics = log['topics'][1:]  # First topic in list is the event hash/signature -> Keccak(EventName(type,...,type))
        data = log['data'][2:]      # First 2 bytes are '0x'

        attr_topics = AbiEncoder.decode_event_topic(self.indexed,topics)
        attr_data = AbiEncoder.decode(self.inputs,data)
        attr_all = []

        t = 0
        d = 0

        for abi_input in self.abi['inputs']:
          if 'name' in abi_input and abi_input['name'] != '':
            if 'indexed' in abi_input and abi_input['indexed'] == True:
              setattr(event,abi_input['name'],attr_topics[t])
              attr_all.append(attr_topics[t])
              t = t + 1
            else:
              setattr(event,abi_input['name'],attr_data[d])
              attr_all.append(attr_data[d])
              d = d + 1
          else:
            if 'indexed' in abi_input and abi_input['indexed'] == True:
              setattr(event,'param_%d' % d + t,attr_topics[t])
              attr_all.append(attr_topics[t])
              t = t + 1
            else:
              setattr(event,'param_%d' % d + t,attr_data[d])
              attr_all.append(attr_data[d])
              d = d + 1

        setattr(event,'all',attr_all)
        ret.append(event)
    return ret

  def topic(self, *indexed):
    if indexed is not ():
      n = len(indexed)
      topics = AbiEncoder.encode_event_topic(self.indexed[:n],indexed)
    else:
      topics = []
    topics = [self.event_hash] + topics
    return topics

  def __call__(self,*indexed,**kwargs):
    filter_query = {}

    if hasattr(self.contract,'address'):
      filter_query['address'] = self.contract.address
    else:
      if 'address' in kwargs:
        filter_query['address'] = kwargs['address']
    filter_query['topics'] = self.topic(*indexed)

    return self.commit_filter_query(filter_query,**kwargs)
  
class ContractFunction(object):
  '''
    This class represents a function of the contract. 
    Its behavior varies depending on its state of mutability. 
    The functions that modify the blockchain are executed generating a transaction, 
    signing and send it with a eth_sendRawTransaction(), in the other hand 
    the query functions calling the rpc method: eth_Call()
  '''

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
      TypeError('rawTransaction(): This function is constant')


    jsonrpc_valid = True if isinstance(self.contract.net.jsonrpc_provider,JsonRpc) else False

    if not jsonrpc_valid:
      raise AttributeError('commit_filter_query(): Unable to found a valid jsonrpc_provider')

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
        At this point, if the account is not passed by parameter
        you have to check if the contract has the account variable to sign the
        transaction with her
      '''
      if self.contract.account is not None and isinstance(self.contract.account,Account):
        account = self.contract.account
      else:
        raise AttributeError('rawTransaction(): Unable to found a valid way to sign() transaction, you MUST import an account')  

    if 'from' in kwargs and kwargs['from'].lower() != account.addr.lower():
      raise ValueError('rawTransaction(): "Account.addr" and "from" argument are different')

    arguments = [i['type'] for i in self.inputs]
    data = AbiEncoder.encode(arguments, args)

    tx = Transaction()

    if 'nonce' in kwargs:
      tx.nonce = kwargs['nonce']
    else:
      response = self.contract.net.jsonrpc_provider.eth_getTransactionCount(self.contract.account.addr,'latest')
      if 'result' in response:
        tx.nonce = response['result']
      else:
        raise JsonRpcError(str(response))
  
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
    
    if self.contract.net.chainId is not None:
      tx.chainId = self.contract.net.chainId
    else:
      if 'chainId' in kwargs:
        tx.chainId = kwargs['chainId']

    if 'gasLimit' in kwargs:
      tx.gasLimit = kwargs['gasLimit']
    else:
      response = self.contract.net.jsonrpc_provider.eth_estimateGas(tx.to_dict(signature=False, hexstring=True))
      if 'result' in response:
        tx.gasLimit = response['result']
      else:
        raise JsonRpcError(str(response))

    return tx.sign(account)


  def commit(self, *args, **kwargs):
    jsonrpc_valid = True if isinstance(self.contract.net.jsonrpc_provider,JsonRpc) else False
    if not jsonrpc_valid:
      raise AttributeError('commit(): Unable to found a valid jsonrpc_provider')
    
    rawTransaction = self.rawTransaction(*args,**kwargs)
    response = self.contract.net.jsonrpc_provider.eth_sendRawTransaction(rawTransaction)

    if 'result' in response:
      return CommitedTransaction(response['result'],self.contract.net.jsonrpc_provider)
    else:
      raise JsonRpcError(str(response))


  def call(self, *arg, **kwargs):
    jsonrpc_valid = True if isinstance(self.contract.net.jsonrpc_provider,JsonRpc) else False
    if not jsonrpc_valid:
      raise AttributeError('call(): Unable to found a valid jsonrpc_provider')

    arguments = [i['type'] for i in self.inputs]
    if len(arguments) != 0:
      data = self.signature + AbiEncoder.encode(arguments, arg)
    else:
      data = self.signature

    if 'blockNumber' in kwargs:
      if isinstance(kwargs['blockNumber'],int):
        blockNumber = hex(kwargs['blockNumber'])
      else:
        blockNumber = kwargs['blockNumber']
    else:
      blockNumber = 'latest'

    response = self.contract.net.jsonrpc_provider.eth_call({'to': self.contract.address, 'data': data},blockNumber)
    if 'result' in response:
      result = response['result']
    else:
      raise JsonRpcError(str(response))

    outputs = [ouput['type'] for ouput in self.outputs ]
    return tuple(AbiEncoder.decode(outputs,result[2:]))


  def __call__(self,*args, **kwargs):
    if self.constant == False:
      return self.commit(*args,**kwargs)
    else:
      return self.call(*args,**kwargs)


class FunctionSet:
  '''
    A abstract class to contain all contract's methods/functions
  '''
  pass

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


class ContractBase(object):

  def __init__(self,**kwargs):

    if 'jsonrpc_provider' in kwargs:
      provider = kwargs['jsonrpc_provider']
      basicauth = ()
      if 'jsonrpc_basicauth' in kwargs and isinstance(kwargs['jsonrpc_basicauth'],tuple):
        basicauth = kwargs['jsonrpc_basicauth']

      self.__net = NetworkUtil(provider,basicauth)
    else:
      self.__net = NetworkUtil()


  @property
  def net(self):
    return self.__net


  @net.setter
  def net(self,net):
    if isinstance(net,NetworkUtil):
      self.__net = net
    else:
      raise TypeError('net must be a NetworkUtil instance')


class ContractVoid(ContractBase):
  def __init__(self,abi,**kwargs):
    self.abi = abi
    self.events = EventSet(self)

    ContractBase.__init__(self,**kwargs)

    for attibute in self.abi:
      if attibute['type'] == 'event':
        setattr(self.events,attibute['name'],Event(attibute,self))


class Contract(ContractBase):
  def __init__(self,address,abi,**kwargs):
    self.address = address
    self.abi = abi
    self.events = EventSet(self)
    self.functions = FunctionSet()
    self.__account = None

    ContractBase.__init__(self, **kwargs)

    for attibute in self.abi:
      if attibute['type'] == 'function':
        setattr(self.functions,attibute['name'],ContractFunction.from_abi(attibute,self))

      if attibute['type'] == 'event':
        setattr(self.events,attibute['name'],Event(attibute,self))

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

  def import_account(self,account):
    self.account = account


