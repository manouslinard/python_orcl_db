from lib.handler import *

c = Connection("ITxxxx", "ITxxxx")
b = BookHandler(c)

b.add_book('Lord of the rings 3', 'J.R.R. Tolkien', 1111111111113, 1)
