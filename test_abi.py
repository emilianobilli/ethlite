from ethlite.Abi import encode, AbiEncoder, get_number_of_words

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
