
class Rlp:

  '''
    Rlp encode library
    Docs: https://ethereum.github.io/yellowpaper/paper.pdf
    ToDo:
      - Decode
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
    return

  @staticmethod
  def bigendian_tohex_padleft(value):
    v = hex(value)[2:]
    return '0' + v if len(v) % 2 == 1 else v

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

