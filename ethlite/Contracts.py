
class ContractFunction(object):
    def __init__(self,name,obj):
        self.name = name
        self.obj = obj
    def __call__(self, *args, **kwargs):
        print(self.obj.name, ":", self.name)

    

class Contract(object):
    def __init__(self, name, functions):
        self.name = name
        for f in functions:
            setattr(self,f,ContractFunction(f,self))


c = Contract('Victor', ['hola', 'chau'])
c.hola()
c.chau()