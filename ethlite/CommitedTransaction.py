from .JsonRpc import JsonRpc
from .Abi import dec_uint

class CommitedTransaction:
  def __init__(self, transactionHash, jsonrpc_provider):
    self.transactionHash = transactionHash
    self.jsonrpc_provider = jsonrpc_provider
    self.receipt = None

  def __str__(self):
    return 'CommitedTransaction(%s)' % self.transactionHash

  def receipt(self):
    uint_keys = ['blockNumber', 'cumulativeGasUsed', 'gasUsed', 'status', 'transactionIndex']

    if self.receipt != None:
      return self.receipt

    response = self.jsonrpc_provider.eth_getTransactionReceipt(self.transactionHash)
    if 'result' in response:
      if response['result'] == None:
        return None

      receipt = response['result']
      for key in uint_keys:
        receipt[key] = dec_uint(receipt[key])
    
      self.receipt = receipt
      return receipt
    else:
      raise JsonRpcError(str(response)) 

