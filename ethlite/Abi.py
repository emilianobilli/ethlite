from re import match
from re import findall

def pad_left(word, char='0'):
  word = align(word)
  tofill = 64 - len(word) + 1
  for i in range(1,tofill):
    word = char + word
  return word

def pad_right(word):
  word = align(word)
  tofill = 64 - len(word) + 1 
  for i in range(1,tofill):
    word = word + '0'
  return word

def remove0x(word):
  if word.startswith('0x'):
    return word[2:]
  return word

def align(word):
  word = remove0x(word)
  if len(word) % 2 == 1:
    return '0' + word
  return word

def enc_bool(b):
  if type(b).__name__ == 'bool':
    if b:
      return enc_uint(1)
    return enc_uint(0)
  else:
    raise TypeError('enc_bool(): Expect a boolean and %s receive' % (type(b).__name__) )

def enc_address(address):
  if type(address).__name__ == 'str' and address.startswith('0x') and len(address) == 42:
    return pad_left(address)
  raise TypeError('enc_address(): Expect hexstring (start with 0x ) and len == 40')

def enc_uint(uint):
  if (type(uint).__name__ == 'int' or type(uint).__name__ == 'long') and uint >= 0:
    return pad_left(hex(uint))
  raise TypeError('enc_uint(): Expect positive int or long')


def enc_Tk(value, k, encfunc=None):
  if k != len(value):
    raise ValueError('enc_Tk(): k value != len(uintLst)')

  if type(value).__name__ == 'list' and encfunc is not None:
    ret = ''
    for u in value:
      ret = ret + encfunc(u)
    return ret

  raise TypeError('enc_uint_Tk(): Excpect a list')


def enc_T(value, encfunc):
  return enc_uint(len(value)) + enc_Tk(value,len(value),encfunc)


def string_to_hex(string):
    ret = ''
    for ch in string:
      ret = ret + hex(ord(ch))[2:]
    return '0x' + ret


def enc_bytes(b, fixed=False):
  '''
    Accepted datatypes:
      - bytearray
      - hexstring - starting with '0x'
      - string
  '''
  if type(b).__name__ == 'bytearray':
    b = b.hex()[2:]
  elif type(b).__name__ == 'str':
    if b.startswith('0x'):
      b = b[2:]
    else:
      b = string_to_hex(b)[2:]
  else:
    raise TypeError('enc_bytes(): expect bytearray or hexstring')

  size = len(b) // 2
  print(b)

  if fixed and len(b) > 64:
    raise ValueError('enc_bytes(): fixed value grater than bytes32')

  words = len(b) // 64

  b = b[:64*words] + pad_right(b[64*words:])
  
  return enc_uint(size) + b if not fixed else b

def enc_bytes_fixed(b):
  return enc_bytes(b,fixed=True)

def enc_string(s):
  return enc_bytes(string_to_hex(s))


def get_type(s):
  var_type_re = '(int|uint|bool|string|address|bytes)(\d{0,3})'
  var = match(var_type_re, s)
  if var is not None:
    ret = {
      'type': var.group(1),
      'bits': var.group(2)
    }
    array = [l.replace('[','').replace(']','') for l in findall('\[\d*\]',s)]
    if array != []:
      ret['array'] = 0 if array[0] == '' else int(array[0])
    return ret   
  return None


def encode(var_type, value):
  t = get_type(var_type)

  if t['type'] == 'int' or t['type'] == 'uint':
    if 'array' not in t:
      return enc_uint(value)
    else:
      if type(value).__name__ == 'list':
        if t['array'] == 0:
          return enc_T(value, enc_uint)
        else:
          return enc_Tk(value,t['array'], enc_uint)
      else:
        raise TypeError('encode([%s]): Expect a list but %s received' % (t['type'],type(value).__name__))

  elif t['type'] == 'bool':
    if 'array' not in t:
      return enc_bool(value)
    else:
      if type(value).__name__ == 'list':
        if t['array'] == 0:
          return enc_T(value, enc_bool)
        else:
          return enc_Tk(value,t['array'], enc_bool)
      else:
        raise TypeError('encode([%s]): Expect a list but %s received' % (t['type'],type(value).__name__))

  elif t['type'] == 'address':
    if 'array' not in t:
      return enc_address(value)
    else:
      if type(value).__name__ == 'list':
        if t['array'] == 0:
          return enc_T(value, enc_address)
        else:
          return enc_Tk(value,t['array'], enc_address)
      else:
        raise TypeError('encode([%s]): Expect a list but %s received' % (t['type'],type(value).__name__))

  elif t['type'] == 'string':
    if 'array' in t:
      raise TypeError('encode(string): Array is not valid')
    else:
      return enc_string(value)
    
  elif t['type'] == 'bytes':
    if t['bits'] != '':
      if 'array' in t:
        if type(value).__name__ == 'list':
          if t['array'] == 0:
            return enc_T(value,enc_bytes_fixed)
          else:
            return enc_Tk(value, t['array'], enc_bytes_fixed)
      else:
        return enc_bytes_fixed(value)
    else:
      return enc_bytes(value)


def get_number_of_words(args):
  '''
    Return the real number of words (256bits) in the argument
  '''
  words = 0
  for a in args:
    arg_type = get_type(a)
    if 'array' in arg_type and arg_type['array'] > 0:
      words = words + arg_type['array']
    else:
      words += 1
  return words

def is_dynamic(arg):
  arg_type = get_type(arg)
  if ( 'array' in arg_type and arg_type['array'] == 0 ) or arg_type['type'] == 'string' or (arg_type['type'] == 'bytes' and arg_type['bits'] == ''):
    return True
  return False


class AbiEncoder:

  @classmethod
  def encode(cls,arguments,values):
    queue = []
    words = get_number_of_words(arguments)
    next_dynamic_argument = words * 32
    
    data = ''

    i = 0
    for arg in arguments:
      encoded_argument = encode(arg, values[i])
      i = i + 1
      if is_dynamic(arg):
        data = data + enc_uint(next_dynamic_argument)
        next_dynamic_argument = next_dynamic_argument + (len(encoded_argument) // 2)
        queue.append(encoded_argument)
      else:
        data = data + encoded_argument

    for to_append in queue:
      data = data + to_append
  
    return data

  @classmethod
  def decode(cls,arguments, data):
    pass

if __name__ == '__main__':
  print(encode('uint256', 3))
  print(encode('uint[]', [3,3,2,1,2]))
  print(encode('uint[5]', [3,3,2,1,2]))
  print(encode('bool[3]', [True, False, True]))
  print(encode('bool', True))
  print(encode('address', '0x7113fFcb9c18a97DA1b9cfc43e6Cb44Ed9165509'))
  print(encode('address[1]', ['0x7113fFcb9c18a97DA1b9cfc43e6Cb44Ed9165509']))
  print(encode('address[]', ['0x7113fFcb9c18a97DA1b9cfc43e6Cb44Ed9165509'] ))
  print(encode('string', 'que decis amigo'))
  print(encode('bytes32', 'sos re trolo'))
  print(encode('bytes32[2]', ['sos trolo', 'y puto'] ))
  print(encode('bytes32[]', ['pedazo de ', 'puto de mierda']))
  print(encode('bytes', '0x1111'))
  print(get_number_of_words(['uint32', 'uint[5]', 'address', 'uint[]']))
  print(AbiEncoder.encode(['uint','uint'],[1,2]))
  print(AbiEncoder.encode(['uint','uint32[]','bytes10','bytes'],[0x123, [0x456, 0x789], "1234567890", "Hello, world!"]))
  print(AbiEncoder.encode(['bytes','bool','uint256[]'],["dave",True,[1,2,3]]))