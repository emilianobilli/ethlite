
class Topic:
    def __init__(self,*args):
        self.topic = [a for a in args]
    
    def __str__(self):
        return str(self.topic)

if __name__ == '__main__':
    t = Topic('puta', 'trola')
    print(t)
