'''Main class.'''

from lib.handler import *

c = Connection('ITxxxxx', 'ITxxxxx')
m = LoansHandler(c)
m.update_deadline_date(1111111111111, '2023-01-15')
