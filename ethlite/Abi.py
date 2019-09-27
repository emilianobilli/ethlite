from re import match
from re import findall
from sha3 import keccak_256

'''
  ToDo: 
    - dec_bytes()
    - dec_string()
'''

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


def dec_bool(word):
  b = int(word,16)
  if b == 1:
    return True
  return False

def enc_address(address):
  print(address)
  if type(address).__name__ == 'str' and address.startswith('0x') and len(address) == 42:
    return pad_left(address)
  raise TypeError('enc_address(): Expect hexstring (start with 0x ) and len == 40')

def dec_address(word):
  return '0x' + word[24:]

def enc_uint(uint):
  if (type(uint).__name__ == 'int' or type(uint).__name__ == 'long') and uint >= 0:
    return pad_left(hex(uint))
  raise TypeError('enc_uint(): Expect positive int or long')


def dec_uint(word):
  return int(word,16)

def enc_int(value,bits=256):
  if (type(value).__name__ == 'int' or type(value).__name__ == 'long'):
    if value < 0:
      return pad_left(hex((2**bits) + value ),'f')
    else:
      return pad_left(hex(value))

def dec_int(word,bits=256):
  num = int(word[64-(bits//4):],16)
  return num - 2 ** bits if num > ((2**bits)/2) - 1 else num


def enc_Tk(value, k, encfunc=None):
  if k != len(value):
    raise ValueError('enc_Tk(): k value != len(uintLst)')

  if type(value).__name__ == 'list' and encfunc is not None:
    ret = ''
    for u in value:
      ret = ret + encfunc(u)
    return ret

  raise TypeError('enc_uint_Tk(): Excpect a list')

def dec_Tk(words, offset, k, decfunc=None):
  value = []
  for i in range(offset,offset+k):
    value.append(decfunc(words[i]))
  return value

def enc_T(value, encfunc=None):
  return enc_uint(len(value)) + enc_Tk(value,len(value),encfunc)


def bytes_to_word_address(b):
  assert b % 32 == 0, 'Invalid word align (%d)' % b 
  return b // 32

def dec_T(words, offset, decfunc=None):
  offset += bytes_to_word_address(dec_uint(words[offset]))
  return dec_Tk(words, offset + 1 , dec_uint(words[offset]), decfunc)

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

def enc_list(value,size,encfunc):
  if type(value).__name__ == 'list':
    if size == ARRAY_DYNAMIC_SIZE:
      return enc_T(value, encfunc)
    else:
      return enc_Tk(value,size, encfunc)
  else:
    raise TypeError('encode([%s]): Expect a list but %s received' % (var_type['type'],type(value).__name__))

def dec_list(words,offset,size,decfunc):
  if size == ARRAY_DYNAMIC_SIZE:
    return (dec_T(words,offset,decfunc), 1)
  else:
    return (dec_Tk(words,offset,size,decfunc), size)


def get_type(s):
  var_type_re = '(int|uint|bool|string|address|bytes)(\d{0,3})'
  var = match(var_type_re, s)
  if var is not None:
    ret = {
      'type': var.group(1)
    }

    if var.group(2) is not None and var.group(2) != '':
      ret['size'] = int(var.group(2))

    array = [l.replace('[','').replace(']','') for l in findall('\[\d*\]',s)]
    if array != []:
      ret['array'] = ARRAY_DYNAMIC_SIZE if array[0] == '' else int(array[0])

    if var.group(1) == 'string' or (var.group(1) == 'bytes' and 'size' not in ret) or ('array' in ret and ret['array'] == ARRAY_DYNAMIC_SIZE):
      ret['dynamic'] = True
    else:
      ret['dynamic'] = False
    
    return ret   
  return None


def data_to_words(data):
  return [data[x:x+64] for x in range(0, len(data), 64)]


def decode(var, data, offset):
  var_type = get_type(var)
  words = data_to_words(data)

  if var_type['type'] == 'int':
    if 'array' in var_type:
      size = var_type['array']
      return dec_list(words,offset,size,dec_int)
    else:
      return (dec_int(words[offset],var_type['size']), 1)
      
  elif var_type['type'] == 'uint':
    if 'array' in var_type:
      size = var_type['array']
      return dec_list(words,offset,size,dec_uint)
    else:
      return (dec_uint(words[offset]),1)
    
  elif var_type['type'] == 'bool':
    if 'array' in var_type:
      size = var_type['array']
      return dec_list(words,offset,size, dec_bool)
    else:
      return (dec_bool(words[offset]),1)

  elif var_type['type'] == 'address':
    if 'array' in var_type:
      size = var_type['array']
      return dec_list(words,offset,size, dec_address)
    else:
      return (dec_address(words[offset]),1)

  elif var_type['type'] == 'bytes':
    raise NotImplementedError

  elif var_type['type'] == 'string':
    raise NotImplementedError


def encode_event_topic(var, value):
  var_type = get_type(var)

  if var_type['type'] == 'int' or var_type['type'] == 'uint' or var_type['type'] == 'bool' or var_type['type'] == 'address':
    if 'array' in var_type:
      pass # raise invalid indexed type    
    return encode(var,value)

  elif var_type['type'] == 'string':
    return '0x' + keccak_256(bytearray.fromhex(string_to_hex(var))).hexdigest()

  elif var_type['type'] == 'bytes':
    if 'size' in var_type:
      if 'array' in var_type:
        pass # raise invalid indexed type
      else:
        return encode(var, value)

    else:
      to_hash = var if var.startswith('0x') else string_to_hex(var)
      return '0x' + keccak_256(bytearray.fromhex(string_to_hex(var))).hexdigest()

  return None


def decode_event_topic(var, value):
  var_type = get_type(var)
  
  if var_type['type'] == 'int' or var_type['type'] == 'uint' or var_type['type'] == 'bool' or var_type['type'] == 'address':
    if 'array' in var_type:
      pass # raise invalid indexed type    
    return decode(var,value)

  elif var_type['type'] == 'string':
    return value

  elif var_type['type'] == 'bytes':
    if 'size' in var_type:
      if 'array' in var_type:
        pass # raise invalid indexed type
      else:
        return decode(var, value)

    else:
      return value


def encode(var, value):
  var_type = get_type(var)

  if var_type['type'] == 'int':
    if 'array' in var_type:
      size = var_type['array']
      return enc_list(value,size,enc_int)
    else:
      return enc_int(value)

  if var_type['type'] == 'uint':
    if 'array' in var_type:
      size = var_type['array']
      return enc_list(value,size,enc_uint)
    else:
      return enc_uint(value)
      

  elif var_type['type'] == 'bool':
    if 'array' in var_type:
      size = var_type['array']
      return enc_list(value,size,enc_bool)
    else:
      return enc_bool(value)
      

  elif var_type['type'] == 'address':
    if 'array' in var_type:
      size = var_type['array']
      return enc_list(value,size,enc_address)
    else:
      return enc_address(value)
      

  elif var_type['type'] == 'string':
    if 'array' in var_type:
      raise TypeError('encode(string): Array of strings is an invalid type')
    else:
      return enc_string(value)


  elif var_type['type'] == 'bytes':
    if 'size' in var_type:
      if 'array' in var_type:
        size = var_type['array']
        return enc_list(value,size,enc_bytes_fixed)
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
  def encode_event_topic(cls, arguments, *values):

    if len(arguments) != len(*values):
      pass # raise

    topics = []
    i = 0
    for arg in arguments:
      topics.append('0x' + encode_event_topic(arg,values[i]))
      i = i + 1

    return topics

  @classmethod
  def decode_event_topic(cls, indexed, values):
    if len(indexed) != len(*values):
      pass # raise

    v = []
    i = 0
    for arg in arguments:
      v.append(decode_event_topic(arg,values[i]))
      i = i + 1
    
    return v


  @classmethod
  def encode(cls,arguments,values):

    if len(arguments) != len(values):
      #raise
      pass 

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
    ret = []

    offset = 0
    for arg in arguments:
      decode_argument, i = decode(arg,data,offset)
      offset = offset + i
      ret.append(decode_argument)

    if len(ret) != len(arguments):
      # raise
      pass

    return ret

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


  a = AbiEncoder.encode(['uint[5]','bool'],[[1,2,3,4,5],False])
  print(AbiEncoder.decode(['uint[5]','bool'],a))

  b = AbiEncoder.encode(['uint[]','bool'],[[6,7,8,9,10],True])
  print(AbiEncoder.decode(['uint[]','bool', 'address'],b))

  i = enc_int(-2,16)
  print(i)
  print(dec_int(i,16))