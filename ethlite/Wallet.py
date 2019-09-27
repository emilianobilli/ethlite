from Account import Account
from JsonRpc import JsonRpc
from Transaction import Transaction

class Wallet:
  def __init__(self, http_provider):
    self.account = None
    self.json_rpc_privider = JsonRpc(http_provider)

  def import_account(self,account):
    if isinstance(account,Account):
      self.account = account
    elif isinstance(account,int):
      self.account = Account(account)
    elif isinstance(account,str) and account.startswith('0x'):
      self.account = Account.fromhex(account)
    else:
      raise TypeError('import_account(): Expect a private_key in one of these formats-> int, hextring or Account() instance')          

  def from_paraphrase(self,paraphrase):
    pass

  def new_random(self, seed=None):
    pass

  def send(self, **kwargs):
    pass
    