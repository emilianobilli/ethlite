from sha3 import keccak_256
from Account import Account
from Rlp import Rlp

class Transaction(object):
  rlp = Rlp()
  keccak = keccak_256

  def __init__(self,**kargs):
    if 'nonce' in kargs.keys():
      self.nonce = kargs['nonce']
    else:
      self.__nonce = None

    if 'gasPrice' in kargs.keys():
      self.gasPrice = kargs['gasPrice']
    else:
      self.__gasPrice = None

    if 'gasLimit' in kargs.keys():
      self.gasLimit = kargs['gasLimit']
    else:
      self.__gasLimit = None

    if 'to' in kargs.keys():
      self.to = kargs['to']
    else:
      self.to = ''

    if 'value' in kargs.keys():
      self.value = kargs['value']
    else:
      self.value = 0

    if 'data' in kargs.keys():
      self.data = kargs['data']  
    else:
      self.data = ''
    
    if 'v' in kargs.keys():
      self.v = kargs['v']
    else:
      self.v = 0

    if 'r' in kargs.keys():
      self.r = kargs['r']
    else:
      self.r = 0
    
    if 's' in kargs.keys():
      self.s = kargs['s']
    else:
      self.s = 0

    self.keys = list(self.__dict__.keys())

    if 'chainId' in kargs.keys():
      self.chainId = kargs['chainId']
    else:
      self.__chainId = None


  def __iter__(self):
    self.i = 0
    return self

  def __next__(self):
    if self.i == len(self.keys):
      raise StopIteration
    value = self.__dict__[self.keys[self.i]]
    self.i += 1
    return value

  def to_list(self):
    return list(self)

  def to_tuple(self):
    return tuple(self)
  
  def to_dict(self):
    return {
      'nonce': self.nonce,
      'gasPrice': self.gasPrice,
      'gasLimit': self.gasLimit,
      'to': self.to,
      'value': self.value,
      'data': self.data,
      'v': self.v,
      'r': self.r,
      's': self.s
    }

  def __str__(self):
    return str(self.to_dict())

  def __repr__(self):
    return 'Transaction(%s)' %  str(self)

  @staticmethod
  def integer_type(value):
    if type(value).__name__ == 'int' or type(value).__name__ == 'long': 
      if value >= 0:
        return value
      else:
        raise ValueError('Expect positive values')
    else:
      if type(value).__name__ == 'str' and value.startswith('0x'):
        return int(value,16)
      else:
        raise TypeError('Expect <int>, <long> or 0x<str>')

  @staticmethod
  def byte_type(value):
    if (type(value).__name__ == 'str' and (value.startswith('0x') or value == '')) or type(value).__name__ == 'bytearray':
      if type(value).__name__ == 'bytearray':
        return '0x' + value.hex()
      else:
        return value
    else:
      raise TypeError('Expect 0x<str> or bytearray')

  ##
  # Nonce
  #
  @property
  def nonce(self):
    return self.__nonce

  @nonce.setter
  def nonce(self,nonce):
    self.__nonce = self.integer_type(nonce)

  ##
  # GasPrice
  #
  @property
  def gasPrice(self):
    return self.__gasPrice
  
  @gasPrice.setter
  def gasPrice(self, gasPrice):
    self.__gasPrice = self.integer_type(gasPrice)

  ##
  # GasLimit
  #
  @property
  def gasLimit(self):
    return self.__gasLimit
  
  @gasLimit.setter
  def gasLimit(self, gasLimit):
    self.__gasLimit = self.integer_type(gasLimit)

  ##
  # To
  #
  @property
  def to(self):
    return self.__to
  
  @to.setter
  def to(self, to):
    if type(to).__name__ == 'str' and ( (to.startswith('0x') and len(to) == 42) or to == ''):
      self.__to = to
    else:
      if to is None or to == 0:
        self.__to = 0
      else:
        raise ValueError('Invalid value')

  ##
  # value
  #
  @property
  def value(self):
    return self.__value

  @value.setter
  def value(self,value):
    self.__value = self.integer_type(value)

  ##
  # data
  #
  @property
  def data(self):
    return self.__data
  
  @data.setter
  def data(self,data):
    self.__data = self.byte_type(data)

  ##
  # chainId
  #
  @property
  def chainId(self):
    return self.__chainId

  @chainId.setter
  def chainId(self,chainId):
    self.__chainId = self.integer_type(chainId)

  ##
  # v
  #
  @property
  def v(self):
    return self.__v
  
  @v.setter
  def v(self,v):
    self.__v = self.integer_type(v)

  ##
  # r
  #
  @property
  def r(self):
    return self.__r
  
  @r.setter
  def r(self,r):
    self.__r = self.integer_type(r)

  ##
  # s
  #
  @property
  def s(self):
    return self.__s
  
  @s.setter
  def s(self,s):
    self.__s = self.integer_type(s)

  @staticmethod
  def sign_hash(h,private_key):
    if not isinstance(private_key,Account):
      if type(pk).__name__ == 'str' and pk.startswith('0x'):
    	  private_key = Account.fromhex(private_key)
      else:
        private_key = Account(private_key)

    return private_key.sign_digest(h)

  def sign(self,private_key):

    if self.chainId is not None:
      self.v = self.chainId
      self.r = 0
      self.s = 0
      to_hash = self.rlp.encode(list(self),encoding='bytearray')
    else:
      to_hash = self.rlp.encode(list(self)[:6],encoding='bytearray')
    
    to_sign = keccak_256(to_hash).digest()
    signature = self.sign_hash(to_sign,private_key)

    self.r = signature.r
    self.s = signature.s
    '''
      Check: https://github.com/ethereum/eth-keys/blob/a95532d5b9fc0116c5fdae6dfa29ce2636dc44e7/eth_keys/backends/native/ecdsa.py#L108
    '''
    if self.s > Account.secp256k1n // 2:
      self.s = Account.secp256k1n - self.s
      signature.even = not signature.even
    
    if self.chainId is not None:
      self.v = self.chainId * 2 + (35 if signature.even else 36)
    else:
      self.v = 27 if signature.even else 28 

    print(list(self))
    return self.rlp.encode(list(self))

if __name__ == '__main__':
  tx = Transaction()
  tx.nonce = 2327
  tx.gasPrice = 81 * 10 ** 9
  tx.gasLimit = 21000
  tx.to = '0x3535353535353535353535353535353535353536'
  tx.value = 10 ** 16
  tx.chainId = 42
  pk = int('7a75b6b7d87cf3f0d9da5868c7c9dfb53b32175f09563b75159391c071d07bae',16)
  print (tx.sign(pk))
  

  n = Account.fromhex('0x7a75b6b7d87cf3f0d9da5868c7c9dfb53b32175f09563b75159391c071d07bae')
  print(n.addr)