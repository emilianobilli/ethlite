from Abi import AbiEncoder
from Transaction import Transaction
from Account import Account


class ContractFunction(object):

  valid_kwargs = ['from', 'value', 'account', 'gasPrice']

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

    if 'value' in kwargs and self.payable == False:
        # raise
      pass

    if self.payable == True and self.stateMutability == 'payable':
      '''
        Hay que enviar fondos
      '''  
      value = kwargs['value']
    else:
      value = 0
      
    if 'account' in kwargs:
      '''
          Verificamos que la cuenta sea pasada como parametro
      '''

      if isinstance(kwargs['account'],Account):
          account = kwargs['account']
      elif isinstance(kwargs['account'],int):
          account = Account(kwargs['account'])
      elif isinstance(kwargs['account'],str) and kwargs['account'].startswith('0x'):
          account = Account.fromhex(kwargs['account'])
      else:
          pass
          #raise
    else:
      '''
          En este punto, si no se pasa la account por parametro
          hay que revisar si el contrato tiene la variable account para firmar la 
          transaccion con ella
      '''
      if self.contract.account is not None and isinstance(self.contract.account,Account):
          account = self.contract.account
      else:
          # raise
          pass


    if 'from' in kwargs and kwargs['from'].lower() != account.addr.lower():
      '''
          Se envio el argumento from y no concuerda con la 
          direccion de la cuenta
      '''
      pass
      #raise






    def __call__(self, *args, **kwargs):
        print(self.obj.name, ":", self.name)




    

class Contract(object):
    def __init__(self, name, functions):
        self.name = name
        for f in functions:
            setattr(self,f,ContractFunction(f,self))


c = Contract('Victor', ['hola', 'chau'])
c.hola()
c.chau()

contrato.closeBet.rawTransaction(1,2,3)