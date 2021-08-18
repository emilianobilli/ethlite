from sha3 import keccak_256
from .ecdsa import SigningKey
from .ecdsa import SECP256k1
from .ecdsa.ellipticcurve import Point
secp256k1n = 115792089237316195423570985008687907852837564279074904382605163141518161494337

def _tonelli_shanks(n, p):
  '''
      A generic algorithm for computng modular square roots.
  '''
  Q, S = p - 1, 0
  while Q % 2 == 0:
    Q, S = Q // 2, S + 1

  z = 2
  while pow(z, (p - 1) // 2, p) != (-1 % p):
    z += 1

  M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q + 1) // 2, p)
  while t != 1:
    for i in range(1, M):
      if pow(t, 2**i, p) == 1:
        break

    b = pow(c, 2**(M - i - 1), p)
    M, c, t, R = i, pow(b, 2, p), (t * b * b) % p, (R * b) % p

  return R, -R % p


def mod_sqrt(a, p):
  '''
  Compute the square root of :math:`a \pmod{p}`
  In other words, find a value :math:`x` such that :math:`x^2 \equiv a \pmod{p}`.
  Args:
      |  a (long): The value whose root to take.
      |  p (long): The prime whose field to perform the square root in.
  Returns:
      (long, long): the two values of :math:`x` satisfying :math:`x^2 \equiv a \pmod{p}`.
  '''
  if p % 4 == 3:
    k = (p - 3) // 4
    x = pow(a, k + 1, p)
    return x, (-x % p)
  else:
    return _tonelli_shanks(a, p)

def convert_point_to_addr(point):
  '''
      Concatenate the coordinates of the point -> X || Y 
  '''
  x = hex(point.x())[2:]
  y = hex(point.y())[2:]
  return '0x' + keccak_256(bytearray.fromhex(x+y)).hexdigest()[24:]


def get_y(y1, y2, v, chainId):
  if y1 % 2 == 0 and y2 % 2 != 0:
    # y1 even and y2 odd
    return y1 if v - chainId * 2 == 35 else y2
  if y1 % 2 != 0 and y2 % 2 == 0: 
    # y1 odd and y2 even
    return y1 if v - chainId * 2 == 36 else y2

def hash_to_int(h):
  if isinstance(h,int):
    return h
  elif isinstance(h,bytearray) or isinstance(h, bytes):
    return int(h.hex(),16)
  elif isinstance(h,str) and h.startswith('0x'):
    return int(h,16)
  else:
    pass
    # raise

def ecrecover(v, r, s, hash, chainId=1):
  q = SECP256k1.order
  r_inv = pow(r, q - 2, q )

  z = hash_to_int(hash)

  y_squared = (r * r * r + SECP256k1.curve.a() * r + SECP256k1.curve.b()) % SECP256k1.curve.p()
  y1, y2 = mod_sqrt(y_squared, SECP256k1.curve.p())

  y = get_y(y1,y2,v,chainId)

  R = Point(SECP256k1.curve, r, y)
  Q = r_inv * (s * R - z * SECP256k1.generator)

  return convert_point_to_addr(Q)


class Sign(object):
  def __init__(self,s,even):
    self.signature = s
    self.r = int('0x' + self.signature.hex()[:64],16)
    self.s = int('0x' + self.signature.hex()[64:],16)
    
    '''
    We declare that an ECDSA signature is invalid unless all the following conditions are true(*5):
      (280) 0 < r < secp256k1n
      (281) 0 < s < secp256k1n ÷ 2 + 1
      (282) v ∈ {27, 28}
      where:
      (283) secp256k1n = 115792089237316195423570985008687907852837564279074904382605163141518161494337
    '''

    if self.s * 2 > secp256k1n:
      self.s = secp256k1n - self.s
      self.even = not even
    else:
      self.even = even

  def __unicode__(self):
    return self.signature.hex()
  def __str__(self):
    return self.signature.hex()
  def __repr__(self):
    return self.signature.hex()

  def eth_signature_format(self):
    return self.signature.hex() + str(hex(27 if self.even else 28))[2:]

class Account(object):
  
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
      if privateKey <= secp256k1n-1 and privateKey > 0:
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
    '''
      For a given private key, pr, the Ethereum address A(pr) (a 160-bit value) to which it corresponds is defined as the
      rightmost 160-bits of the Keccak hash of the corresponding ECDSA public key:
      (284) A(pr) = B[96,255] KEC(ECDSAPUBKEY(pr))
    '''
    if self.__addr == None:
      self.__addr = '0x' + keccak_256(bytearray.fromhex(self.publicKey[2:])).hexdigest()[24:]
    return self.__addr

  def sign_digest(self, digest):
    sig, even = self.__privateKey.sign_digest_deterministic(digest, hashfunc=keccak_256)
    return Sign(sig,even)

  def sign(self, message):
    sig, even = self.__privateKey.sign_deterministic(message,hashfunc=keccak_256)
    return Sign(sig,even)

  def sign_message(self, message):
    msg = '0x' + keccak_256(message.encode('utf-8')).hexdigest()
    msg = '\x19Ethereum Signed Message:\n%d%s' % (len(msg), msg)
    msg = bytearray(msg.encode('utf-8'))
    return self.sign_digest(bytearray(keccak_256(msg).digest())).eth_signature_format()

