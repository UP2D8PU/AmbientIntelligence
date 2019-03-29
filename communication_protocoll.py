
from enum import Enum
class Order(Enum):
    IDLE = 0
    NEW_MESSAGE =  1
    WATER = 2
    STOP = 3

def read_order(f):


print(Order.NEW_MESSAGE)


