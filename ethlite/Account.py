from sha3     import keccak_256
from ecdsa    import SigningKey
from ecdsa    import SECP256k1

class Sign:
  def __init__(self,s,parity):
    self.signature = s
    self.r = self.signature.hex()[:64]
    self.s = self.signature.hex()[64:]
    self.parity = parity

  def __unicode__(self):
    return self.signature.hex()
  def __str__(self):
    return self.signature.hex()
  def __repr__(self):
    return self.signature.hex()

  def eth_signature_format(self):
    return self.signature.hex() + str(hex(27 if self.parity else 28))[2:]

class Account:
  MAX = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140
  MIN = 0x1

  def __init__(self,pk=None):
    if pk is not None:
      self.privateKey = pk
      self.__addr = None

  @classmethod
  def fromhex(cls,pk):
    if type(pk).__name__ == 'str' and pk.startswith('0x'):
      return cls(int(pk,16))
    raise TypeError('fromhex(): expect hextring starting with 0x')

  @property
  def privateKey(self):
    return '0x' + self.__privateKey.to_string().hex()
  
  @privateKey.setter
  def privateKey(self, privateKey):
    if type(privateKey).__name__ == 'int' or type(privateKey).__name__ == 'long': 
      if privateKey < self.MAX and privateKey >= self.MIN:
        self.__privateKey = SigningKey.from_secret_exponent(privateKey,SECP256k1)
      else:
        raise ValueError('privateKey: Invalid range')
    else:
      raise TypeError('privateKey: expect int or long')

  @property
  def publicKey(self):
    return '0x' + self.__privateKey.verifying_key.to_string().hex()

  @property
  def addr(self):
    if self.__addr == None:
      self.__addr = '0x' + keccak_256(bytearray.fromhex(self.publicKey[2:])).hexdigest()[24:]
    return self.__addr

  def sign_digest(self, digest):
    sig = self.__privateKey.sign_digest_deterministic(digest, hashfunc=keccak_256)
    return Sign(sig,1)

  def sign(self, message):
    sig = self.__privateKey.sign_deterministic(message,hashfunc=keccak_256)
    return Sign(sig,1)