
class Rlp:

  '''
    Rlp encode library
    Docs: https://ethereum.github.io/yellowpaper/paper.pdf
  '''
  @classmethod
  def encode(cls,value, encoding='hex'):
    if encoding == 'hex':
      return '0x' + cls.encode_data(value)
    elif encoding == 'bytearray':
      return bytearray.fromhex(cls.encode_data(value))
    else:
      raise ValueError('encode(): Invalid argument value, encoding=<bytearray|hex>')


  @classmethod
  def decode(cls,value):
    if isinstance(value,str) and value.startswith('0x'):
      decoded, length = cls.decode_data(value[2:])
      if length == len(value[2:]):
        return decoded
      else:
        raise ValueError('Rlp.decode(): The value is not a RLP encode data ')
    else:
      raise TypeError('Rlp.decode(): expect a hexstring')


  @classmethod
  def decode_data(cls,data):
    prefix = int(data[:2],16)
    if prefix < 0xc0: # String
      if prefix <= 0x7f:
        return (cls.tohex(prefix), 2)
      elif prefix <= 0xb7:
        data_len = prefix - 0x80
        if data_len == 0:
          return ('',2)
        return ('0x' + data[2:2+(data_len*2)],2+data_len*2)
      else:
        len_of_data_len = prefix - 0xb7
        data_len = int(data[2:2+(len_of_data_len*2)],16)
        return ('0x' + data[2+(len_of_data_len*2):2+(len_of_data_len*2)+(data_len*2)],1*2+len_of_data_len*2+data_len*2)
    else: # List
      ret = []
      if prefix < 0xf8:
        payload_len = (prefix - 0xc0) * 2
        offset = 2
      else:
        payload_len = int(data[2:2+(prefix - 0xf7) * 2],16) * 2
        offset = 2 + (prefix - 0xf7) * 2
      bytes_to_decode = payload_len 
      while bytes_to_decode > 0:
        value, shift = cls.decode_data(data[offset:])
        ret.append(value)
        bytes_to_decode = bytes_to_decode - shift
        offset = offset + shift
      return ret, offset


  @staticmethod
  def bigendian_tohex_padleft(value):
    v = hex(value)[2:]
    return '0' + v if len(v) % 2 == 1 else v

  @staticmethod
  def tohex(i):
    s = hex(i)
    if len(s[2:]) % 2 == 1:
      return '0x0' + s[2:]
    return s 

  @staticmethod
  def string_tohex(value):
    ret = ''
    for ch in value:
      ret = ret + hex(ord(ch))[2:]
    return '0x' + ret

  @classmethod
  def from_bigendian_int(cls, value):
    if value < 0:
      raise ValueError('from_bigendian_int(): Invalid value, expect positive values.')
    
    if value == 0:
      return '80'
    elif value <= 127:
      return cls.bigendian_tohex_padleft(value)
    else:
      data = cls.bigendian_tohex_padleft(value)
      size = len(data) // 2
      if size >= 1 and size <= 55:
        return hex(128 + size)[2:] + data
      else:
        size_data = cls.bigendian_tohex_padleft(size)
        return hex(183 + len(size_data)//2)[2:] + size_data + data

  @classmethod
  def encode_bytes(cls,value):
    if type(value).__name__ == 'int' or type(value).__name__ == 'long':
      return cls.from_bigendian_int(value)
    elif type(value).__name__ == 'str' or type(value).__name__ == 'bytearray':
      if type(value).__name__ == 'bytearray':
        value = '0x' + value.hex()
      if value.startswith('0x'):
        return cls.from_bigendian_int(int(value,16))
      elif value == '':
        return '80'
      else:
        return cls.from_bigendian_int(int(cls.string_tohex(value),16))
    else:
      raise TypeError('encode_bytes(): Invalid type, expect integer(int|long), hexstring or bytearray')

  @classmethod
  def encode_data(cls,value):
    if type(value).__name__ == 'list':
      ret = ''
      for data in value:
        ret = ret + cls.encode_data(data)
      size = len(ret) // 2
      if size <= 55: 
        return hex(192 + size)[2:] + ret
      else:
        size_data = cls.bigendian_tohex_padleft(size)
        return hex(247 + len(size_data)//2)[2:] + size_data + ret
    else:
      return cls.encode_bytes(value)

