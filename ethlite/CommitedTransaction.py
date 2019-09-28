from .JsonRpc import JsonRpc
from .Abi import dec_uint

class CommitedTransaction:
  def __init__(self, transactionHash, jsonrpc_provider):
    self.transactionHash = transactionHash
    self.jsonrpc_provider = jsonrpc_provider

  def receipt(self):
    response = self.jsonrpc_provider.eth_getTransactionReceipt(self.transactionHash)
    print(response)
    #if 'result' in response:
      #rcpt = response['result']
      #rcpt['transactionIndex'] = dec_uint(rcpt['transactionIndex'])
      #rcpt['blockNumber'] = dec_uint(rpc['blockNumber'])
