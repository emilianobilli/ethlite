from re import match
from re import findall
from sha3 import keccak_256

'''
  ToDo: 
    - dec_bytes()
    - dec_string()
'''

class TupleComponents(object):
  reg = r'tuple(\[(\d*)\])?'
  def __init__(self, type, components):
    r = match(self.reg,type)
    if r is None:
      return None

    self.array = r.group(1)
    self.components = []
    for c in components:
      if match(self.reg,c['type']):
        self.components.append(TupleComponents(c['type'],c['components']))
      else:
        self.components.append(c['type'])

  def __str__(self):
    ret = []
    for c in self.components:
      if isinstance(c,TupleComponents):
        ret.append(str(c))
      else:
        ret.append(c)
    ret_string = '(%s)%s' % (','.join(ret), self.array if self.array is not None else '')

    return ret_string

  def __repr__(self):
    return str(self)

  def __iter__(self):
    self.i = 0
    return self

  def __next__(self):
    if self.i == len(self.components):
      raise StopIteration
    value = self.components[self.i]
    self.i += 1
    return value

  @property
  def is_dynamic(self):
    for c in self.components:
      component = VarType(c)
      if component.is_dynamic:
        return True
  
    return False



class VarType(object):
  regex_type = r'(int\d{0,3}|uint\d{0,3}|bool|string|address|bytes\d{0,2}|\(.+\))(\[(\d*)\])?'
  regex_tuple = r'\(.+\)' 
  regex_size = r'(int|uint|bytes)(\d{0,3})'
  
  ARRAY_DYNAMIC_SIZE = None

  def __repr__(self):
    return '(type=%s,base_type=%s,word_size=%s,is_array=%s,is_dynamic=%s,is_dynamic_array=%s)' % (self.type, self.base_type, str(self.word_size), str(self.is_array), str(self.is_dynamic), str(self.is_dynamic_array))

  def __init__(self, s):
    self.type = None
    self.base_type = None
    self.word_size = None
    self.is_array = False
    self.array_size = None

    var = match(self.regex_type,str(s))
    if var is not None:
      self.type = var.group(1)

      '''
        Comprueba el tipo base
      '''
      sized_type = match(self.regex_size,self.type)
      if sized_type is not None and sized_type.group(2) != '':
        self.base_type = sized_type.group(1)
        self.word_size = int(sized_type.group(2))
      else:
        if match(self.regex_tuple, self.type):
          self.base_type = 'tuple'
          self.type = s
        else:
          self.base_type = self.type

      '''
        Comprueba se es un array
      '''
      if var.group(2) is not None:
        self.is_array = True
        if var.group(3) != '':
          self.array_size = int(var.group(3))

    else:
      return None

  @property
  def is_dynamic(self):
    if self.base_type == 'string' or (self.base_type == 'tuple' and self.type.is_dynamic) or (self.base_type == 'bytes' and self.word_size == None) or (self.is_array and self.array_size == None):
      return True
    return False

  @property
  def is_dynamic_array(self):
    return self.is_array and self.array_size == self.ARRAY_DYNAMIC_SIZE

class AbiDecodeError(Exception):
  pass


'''
  Functions to sanitize and pad left/right 
'''
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

'''
  Encode and decode boolean type

'''
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

'''
  Encode and decode address type
'''
def enc_address(address):
  if type(address).__name__ == 'str' and address.startswith('0x') and len(address) == 42:
    return pad_left(address)
  raise TypeError('enc_address(): Expect hexstring (start with 0x ) and len == 40')

def dec_address(word):
  return '0x' + word[24:]

'''
  Encode and decode unsigned integer type
'''
def enc_uint(uint):
  if (type(uint).__name__ == 'int' or type(uint).__name__ == 'long') and uint >= 0:
    return pad_left(hex(uint))
  raise TypeError('enc_uint(): Expect positive int or long')

def dec_uint(word):
  return int(word,16)

'''
  Encode and decode signed integer type
'''
def enc_int(value,bits=256):
  if (type(value).__name__ == 'int' or type(value).__name__ == 'long'):
    if value < 0:
      return pad_left(hex((2**bits) + value ),'f')
    else:
      return pad_left(hex(value))

def dec_int(word,bits=256):
  num = int(word[64-(bits//4):],16)
  return num - 2 ** bits if num > ((2**bits)/2) - 1 else num


'''
  Encode and decode k elements of any valid type using de parameter 
  encfunc/decfunc to encode and decode the specific type
'''
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
  offset = bytes_to_word_address(dec_uint(words[offset]))
  return dec_Tk(words, offset + 1 , dec_uint(words[offset]), decfunc)

def dec_bytesN(word,size=32):
  if size < 32 and size % 8 == 0:
    return '0x' + word[:size*2]
  pass # raise

def dec_bytes(words, offset):
  b = '0x'
  offset = bytes_to_word_address(dec_uint(words[offset]))
  length = dec_uint(words[offset]) * 2
  if length == 0:
    return b
  offset = offset + 1
  w = length // 64
  m = length % 64
  while w > 0:
    b = b + words[offset]
    w = w - 1
    offset = offset + 1
  b = b + words[offset][:m]
  return b

def dec_string(words, offset):
  b = dec_bytes(words,offset)
  return bytes.fromhex(b[2:]).decode('utf-8')

def string_to_hex(string):
  ret = ''
  for ch in string:
    ret = ret + sanitize_hex(hex(ord(ch)))
  return ret

'''
  Decode Tuples
'''
def dec_tuple_list(tuple_struct, words, offset, size):
  ret = []

  array_dinamic = False
  if tuple_struct.is_dynamic or size == VarType.ARRAY_DYNAMIC_SIZE:
    offset = bytes_to_word_address(dec_uint(words[offset]))
    if size == VarType.ARRAY_DYNAMIC_SIZE:
      array_dinamic = True
      size = dec_uint(words[offset])
      offset = offset + 1

  total_words = 0
  
  for i in range(0, size):
    encoded_tuple, n = dec_tuple(tuple_struct,words[offset:],total_words)
    total_words += n
    i = i + n
    ret.append(encoded_tuple)

  return ret, 1 if array_dinamic or tuple_struct.is_dynamic else total_words

def dec_tuple(tuple_struct, words, offset):
  ret = []

  if tuple_struct.is_dynamic:  
    offset = bytes_to_word_address(dec_uint(words[offset]))
  
  data = words_to_data(words[offset:])
  offset = 0

  for arg in tuple_struct:
    try:
      decode_argument, i = decode(arg,data,offset)
    except Exception as e:
      raise AbiDecodeError(str(e))
    else:
      offset = offset + i
      ret.append(decode_argument)

  if len(ret) != len(list(tuple_struct)):
    raise AbiDecodeError("Invalid argument count, expected %d and %d received" % (len(list(tuple_struct)), len(ret))) 

  return tuple(ret), 1 if tuple_struct.is_dynamic else offset

'''
  Encode Tuples
'''
def enc_tuple_list(tuple_struct, values, size):

  data = ''

  if not isinstance(values,list):
    raise ValueError('Error')

  words = len(values)

  if size == VarType.ARRAY_DYNAMIC_SIZE:
    data = enc_uint(len(values))
  else:
    if len(values) != size:
      raise ValueError('Error')

  if tuple_struct.is_dynamic:
    queue = []
    next_tuple_offset = words * 32

    for value in values:
      encoded_tuple = enc_tuple(tuple_struct,value)
      data = data + enc_uint(next_tuple_offset)
      next_tuple_offset = next_tuple_offset + (len(encoded_tuple) // 2)
      queue.append(encoded_tuple)

    for to_append in queue:
      data = data + to_append
  else:
    for value in values:
      data = data + enc_tuple(tuple_struct,value)
  
  return data

def enc_tuple(tuple_struct,values):
  if isinstance(tuple_struct,TupleComponents) and isinstance(values,tuple):
    queue = []

    words = get_number_of_words(tuple_struct)
    next_dynamic_argument_offset = words * 32
    
    data = ''

    i = 0
    for component in tuple_struct:
      encoded_argument = encode(component, values[i])
      i = i + 1
      if is_dynamic(component):
        data = data + enc_uint(next_dynamic_argument_offset)
        next_dynamic_argument_offset = next_dynamic_argument_offset + (len(encoded_argument) // 2)
        queue.append(encoded_argument)
      else:
        data = data + encoded_argument

    for to_append in queue:
      data = data + to_append
  
    return data



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

  if b == '':
    return enc_uint(0)

  size = len(b) // 2

  if fixed and len(b) > 64:
    raise ValueError('enc_bytes(): fixed value grater than bytes32')

  words = len(b) // 64

  b = b[:64*words] + pad_right(b[64*words:])
  
  return enc_uint(size) + b if not fixed else b

def enc_bytes_fixed(b):
  return enc_bytes(b,fixed=True)

def enc_string(s):
  return enc_bytes(s)

def enc_list(value,size,encfunc):
  if type(value).__name__ == 'list':
    if size == VarType.ARRAY_DYNAMIC_SIZE:
      return enc_T(value, encfunc)
    else:
      return enc_Tk(value,size, encfunc)
  else:
    raise TypeError('encode([%s]): Expect a list but %s received' % ('enc_list',type(value).__name__))

def dec_list(words,offset,size,decfunc):
  if size == VarType.ARRAY_DYNAMIC_SIZE:
    return (dec_T(words,offset,decfunc), 1)
  else:
    return (dec_Tk(words,offset,size,decfunc), size)

def data_to_words(data):
  return [data[x:x+64] for x in range(0, len(data), 64)]

def words_to_data(words):
  return ''.join(words)

def decode(var, data, offset):
  var_type = VarType(var)

  words = data_to_words(data)

  if var_type.base_type == 'tuple':
    if var_type.is_array:
      size = var_type.array_size
      return dec_tuple_list(var_type.type,words,offset,size)
    else:
      return dec_tuple(var_type.type,words,offset)

  elif var_type.base_type == 'int':
    if var_type.is_array:
      size = var_type.array_size
      return dec_list(words,offset,size,dec_int)
    else:
      return (dec_int(words[offset],var_type.word_size), 1)
      
  elif var_type.base_type == 'uint':
    if var_type.is_array:
      size = var_type.array_size
      return dec_list(words,offset,size,dec_uint)
    else:
      return (dec_uint(words[offset]),1)
    
  elif var_type.base_type == 'bool':
    if var_type.is_array:
      size = var_type.array_size
      return dec_list(words,offset,size, dec_bool)
    else:
      return (dec_bool(words[offset]),1)

  elif var_type.base_type == 'address':
    if var_type.is_array:
      size = var_type.array_size
      return dec_list(words,offset,size, dec_address)
    else:
      return (dec_address(words[offset]),1)

  elif var_type.base_type == 'bytes':
    if var_type.word_size is not None:
      if var_type.is_array:
        size = var_type.array_size
        (listbyes,n) = dec_list(words,offset,size, dec_bytesN)
        return ([dec_bytesN(lb,var_type.word_size) for lb in listbytes],n)
      else:
        return(dec_bytesN(words[offset],var_type.word_size),1)
    else:
      return(dec_bytes(words,offset),1)

  elif var_type.base_type == 'string':
    return (dec_string(words,offset),1)

def encode_event_topic(var, value):
  var_type = VarType(var)

  if var_type.base_type == 'int' or var_type.base_type == 'uint' or var_type.base_type == 'bool' or var_type.base_type == 'address':
    if var_type.is_array:
      pass # raise invalid indexed type    
    return encode(var,value)

  elif var_type.base_type == 'string':
    return '0x' + keccak_256(bytearray.fromhex(string_to_hex(var))).hexdigest()

  elif var_type.base_type == 'bytes':
    if var_type.word_size is not None:
      if var_type.is_array:
        pass # raise invalid indexed type
      else:
        return encode(var, value)

    else:
      to_hash = var if var.startswith('0x') else string_to_hex(var)
      return '0x' + keccak_256(bytearray.fromhex(string_to_hex(var))).hexdigest()

  return None

def decode_event_topic(var, value):
  var_type = VarType(var)
  
  if var_type.base_type == 'int' or var_type.base_type == 'uint' or var_type.base_type == 'bool' or var_type.base_type == 'address':
    if var_type.is_array:
      pass # raise invalid indexed type
    ret, _ = decode(var,value[2:],0)
    return ret

  elif var_type.base_type == 'string':
    return value

  elif var_type.base_type == 'bytes':
    if var_type.word_size is not None:
      if var_type.is_array:
        pass # raise invalid indexed type
      else:
        ret, _ = decode(var, value,0)
        return ret

    else:
      return value

def encode(var, value):
  var_type = VarType(var)

  if var_type.base_type == 'tuple':
    if var_type.is_array:
      size = var_type.array_size
      return enc_tuple_list(var_type.type, value, size)
    else:
      return enc_tuple(var_type.type, value)

  elif var_type.base_type == 'int':
    if var_type.is_array:
      size = var_type.array_size
      return enc_list(value,size,enc_int)
    else:
      return enc_int(value)

  elif var_type.base_type == 'uint':
    if var_type.is_array:
      size = var_type.array_size
      return enc_list(value,size,enc_uint)
    else:
      return enc_uint(value)
      

  elif var_type.base_type == 'bool':
    if var_type.is_array:
      size = var_type.array_size
      return enc_list(value,size,enc_bool)
    else:
      return enc_bool(value)
      

  elif var_type.base_type == 'address':
    if var_type.is_array:
      size = var_type.array_size
      return enc_list(value,size,enc_address)
    else:
      return enc_address(value)
      

  elif var_type.base_type == 'string':
    if var_type.is_array:
      raise TypeError('encode(string): Array of strings is an invalid type')
    else:
      return enc_string(value)


  elif var_type.base_type == 'bytes':
    if var_type.word_size is not None:
      if var_type.is_array:
        size = var_type.array_size
        return enc_list(value,size,enc_bytes_fixed)
      else:
        return enc_bytes_fixed(value)
    else:
      return enc_bytes(value)
'''
  Return the real number of words (256bits) in the argument
'''
'''

def get_number_of_words(args):
  words = 0
  for a in args:
    arg_type = VarType(a)
    if arg_type.is_array and not arg_type.is_dynamic_array and arg_type.base_type != 'tuple':
      words = words + arg_type.array_size
    else:
      if arg_type.base_type == 'tuple':
        words += get_number_of_words(arg_type.type)
      else:
        words += 1
  return words
'''
def get_number_of_words(args):
  words = 0
  for a in args:
    arg_type = VarType(a)
    if arg_type.is_dynamic:
      words += 1
    else:
      if arg_type.is_array:
        if arg_type.base_type == 'tuple':
          words += (get_number_of_words(arg_type.type) * arg_type.array_size)
        else:
          words += arg_type.array_size
      else:
        if arg_type.base_type == 'tuple':
          words += get_number_of_words(arg_type.type)
        else:
          words += 1
  return words

def is_dynamic(arg):
  arg_type = VarType(arg)
  return arg_type.is_dynamic
  
class AbiEncoder:

  @classmethod
  def encode_event_topic(cls, arguments, values):

    if len(arguments) != len(values):
      pass # raise

    topics = []
    i = 0
    for arg in arguments:
      if values[i] is not None:
        topics.append('0x' + encode_event_topic(arg,values[i]))
      else:
        topics.append(None)
      i = i + 1

    return topics

  @classmethod
  def decode_event_topic(cls, indexed, values):
    if len(indexed) != len(values):
      pass # raise

    v = []
    i = 0
    for arg in indexed:
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
      try:
        decode_argument, i = decode(arg,data,offset)
      except Exception as e:
        raise AbiDecodeError(str(e))
      else:
        offset = offset + i
        ret.append(decode_argument)
    if len(ret) != len(arguments):
      raise AbiDecodeError("Invalid argument count, expected %d and %d received" % (len(arguments), len(ret))) 

    return ret

  @classmethod
  def function_signature(cls,function_name,arguments):
    args = []
    for a in arguments:
      args.append(str(a))
    signature_raw = '%s(%s)' % (function_name,','.join(args))
    signature_bytes = bytearray.fromhex(string_to_hex(signature_raw))
    return '0x' + keccak_256(signature_bytes).hexdigest()[:8]

  @classmethod
  def event_hash(cls, event_name,arguments):
    args = []
    for a in arguments:
      args.append(str(a))
    event_raw = '%s(%s)' % (event_name,','.join(args))
    event_bytes = bytearray.fromhex(string_to_hex(event_raw))
    return '0x' + keccak_256(event_bytes).hexdigest()

  @classmethod
  def parse_io(cls, io):
    arg = []
    for i in io:
      if 'components' in i:
        arg.append(TupleComponents(i['type'], i['components']))
      else:
        arg.append(i['type'])
    return arg

