from re import match
from re import findall
from sha3 import keccak_256

ARRAY_DYNAMIC_SIZE = -1

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

def sanitize_hex(word):
  if word.startswith('0x'):
    return word[2:]
  return word

def align(word):
  word = sanitize_hex(word)
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
      ret = ret + sanitize_hex(hex(ord(ch)))
    return ret


def enc_bytes(b, fixed=False):
  '''
    Accepted datatypes:
      - bytearray including bytes
      - hexstring starting with '0x'
      - string
  '''
  if type(b).__name__ == 'bytearray' or type(b).__name__  == 'bytes':
    b = sanitize_hex(b.hex())
  elif type(b).__name__ == 'str':
    if b.startswith('0x'):
      b = sanitize_hex(b)
    else:
      b = sanitize_hex(string_to_hex(b))
  else:
    raise TypeError('enc_bytes(): expect bytearray or hexstring')

  size = len(b) // 2

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
      'type': var.group(1)
    }

    if var.group(2) is not None and var.group(2) != '':
      ret['size'] = var.group(2)

    array = [l.replace('[','').replace(']','') for l in findall('\[\d*\]',s)]
    if array != []:
      ret['array'] = ARRAY_DYNAMIC_SIZE if array[0] == '' else int(array[0])

    if var.group(1) == 'string' or (var.group(1) == 'bytes' and 'size' not in ret) or ('array' in ret and ret['array'] == ARRAY_DYNAMIC_SIZE):
      ret['dynamic'] = True
    else:
      ret['dynamic'] = False
    
    return ret   
  return None


def encode(var, value):
  var_type = get_type(var)

  if var_type['type'] == 'int' or var_type['type'] == 'uint':
    if 'array' in var_type:
      if type(value).__name__ == 'list':
        if var_type['array'] == ARRAY_DYNAMIC_SIZE:
          return enc_T(value, enc_uint)
        else:
          return enc_Tk(value,var_type['array'], enc_uint)
      else:
        raise TypeError('encode([%s]): Expect a list but %s received' % (var_type['type'],type(value).__name__))
    else:
      return enc_uint(value)
      

  elif var_type['type'] == 'bool':
    if 'array' in var_type:
      if type(value).__name__ == 'list':
        if var_type['array'] == ARRAY_DYNAMIC_SIZE:
          return enc_T(value, enc_bool)
        else:
          return enc_Tk(value,var_type['array'], enc_bool)
      else:
        raise TypeError('encode([%s]): Expect a list but %s received' % (var_type['type'],type(value).__name__))
    else:
      return enc_bool(value)
      

  elif var_type['type'] == 'address':
    if 'array' in var_type:
      if type(value).__name__ == 'list':
        if var_type['array'] == ARRAY_DYNAMIC_SIZE:
          return enc_T(value, enc_address)
        else:
          return enc_Tk(value,var_type['array'], enc_address)
      else:
        raise TypeError('encode([%s]): Expect a list but %s received' % (var_type['type'],type(value).__name__))
    else:
      return enc_address(value)
      

  elif var_type['type'] == 'string':
    if 'array' in var_type:
      raise TypeError('encode(string): Array is not valid')
    else:
      return enc_string(value)
    
  elif var_type['type'] == 'bytes':
    if 'size' in var_type:
      if 'array' in var_type:
        if type(value).__name__ == 'list':
          if var_type['array'] == ARRAY_DYNAMIC_SIZE:
            return enc_T(value,enc_bytes_fixed)
          else:
            return enc_Tk(value, var_type['array'], enc_bytes_fixed)
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
  return arg_type['dynamic']
  

class AbiEncoder:

  @classmethod
  def encode(cls,arguments,values):
    queue = []
    words = get_number_of_words(arguments)
    next_dynamic_argument_offset = words * 32
    
    data = ''

    i = 0
    for arg in arguments:
      encoded_argument = encode(arg, values[i])
      i = i + 1
      if is_dynamic(arg):
        data = data + enc_uint(next_dynamic_argument_offset)
        next_dynamic_argument_offset = next_dynamic_argument_offset + (len(encoded_argument) // 2)
        queue.append(encoded_argument)
      else:
        data = data + encoded_argument

    for to_append in queue:
      data = data + to_append
  
    return data

  @classmethod
  def decode(cls,arguments, data):
    pass

  @classmethod
  def function_signature(cls,function_name,arguments):
    signature_raw = '%s(%s)' % (function_name,','.join(arguments))
    signature_bytes = bytearray.fromhex(string_to_hex(signature_raw))
    return '0x' + keccak_256(signature_bytes).hexdigest()[:8]

  @classmethod
  def event_hash(cls, event_name,arguments):
    event_raw = '%s(%s)' % (event_name,','.join(arguments))
    event_bytes = bytearray.fromhex(string_to_hex(event_raw))
    return '0x' + keccak_256(event_bytes).hexdigest()

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
  print(AbiEncoder.function_signature('sam',['bytes','bool','uint256[]']))
  print(AbiEncoder.event_hash('tito',['uint','int']))