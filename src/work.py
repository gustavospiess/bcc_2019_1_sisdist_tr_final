from abc import ABC, abstractmethod #abc é Abstract Base Class...

class Work(ABC):
    @abstractmethod
    def do(self, message, orig):
        pass

    def __call__(self, args):
        (input_bts, orig) = args
        return self.do(input_bts, orig)