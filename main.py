from lib.handler import *

c = Connection("ITxxxx", "ITxxxx")
b = BookHandler(c)

b.add_book('asd','asd',123123,1)
