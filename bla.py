
class Bla:
    name: str
    
    def __init__(self, name) -> None:
        self.name = name
        print('i am being constructed')
        
    def __del__(self) -> None:
        print('desctructor')
        
        
b = Bla('adfasdf')

print(b.name)