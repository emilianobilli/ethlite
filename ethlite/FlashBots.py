from json import dumps
from re import compile
from re import match
from re import IGNORECASE

from eth_account import Account as eth_Account, messages
from sha3 import keccak_256

import requests


valid_url_re = compile(
  r'^(?:http)s?://'  # http:// or https://
  r'(?:[^:@]*?:[^:@]*?@|)'  # basic auth
  r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
  r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
  r'localhost|'  # localhost...
  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
  r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
  r'(?::\d+)?'  # optional port
  r'(?:/?|[/?]\S+)$', IGNORECASE
)


class FlashBotRpc(object):

  headers = {'content-type': 'application/json'}
  default_timeout = 10

  def __init__(self, node='https://relay.flashbots.net'):
    if match(valid_url_re, node) is not None:
      self.session = requests.Session()
      self.node = node
      self.instance_headers = {}
    else:
      raise ValueError('FlashBotRpc(): %s is not a valid url' % node)

  @classmethod
  def get_body_dict(cls):
    return {
        'jsonrpc': '2.0',
        'method': '',
        'params': [],
        'id': 1
    }

  def doPost(self,data,timeout=None):
    return self.session.post(
      self.node,
      data=data,
      headers={**self.headers, **self.instance_headers},
      timeout=self.default_timeout if timeout is None else timeout
    ).json()


  def authHeader(self, account, body):
    message = messages.encode_defunct(text='0x'+keccak_256(bytearray(dumps(body).encode('utf-8'))).hexdigest())
    self.instance_headers['X-Flashbots-Signature'] = '%s:%s' % (account.addr, eth_Account.sign_message(message, account.privateKey).signature.hex())
    print(self.instance_headers, '\n',dumps(body))

  def flashbots_getBundleStats(self, account, bundleHash, blockNumber):
    data = self.get_body_dict()
    data['method'] = 'flashbots_getBundleStats'
    obj = {
      'bundleHash': bundleHash,
      'blockNumber': blockNumber
    }

    data['params'].append(obj)
    self.authHeader(account, data)
    return self.doPost(dumps(data))

  def eth_sendBundle(self, account, txs, blockNumber, minTimestamp=None, maxTimestamp=None, revertingTxHashes=None):
    data = self.get_body_dict()
    data['method'] = 'eth_sendBundle'
    obj = {
        'txs': txs,
        'blockNumber': blockNumber,
    }
    if minTimestamp:
      obj['minTimestamp'] = minTimestamp

    if maxTimestamp:
      obj['maxTimestamp'] = maxTimestamp

    if revertingTxHashes:
      obj['revertingTxHashes'] = revertingTxHashes
    
    data['params'].append(obj)
    self.authHeader(account, data)
    return self.doPost(dumps(data))