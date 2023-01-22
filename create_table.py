
from lib.handler import *

c = Connection('ITxxxxx', 'ITxxxxx')

# #Creates BOOKS table
# c.create_table('BOOKS', 'books.csv', replace=True, req_columns=['Title', 'Author','ISBN'], pr_keys=['ISBN'], pr_con_name='pr_book_key')
# #Adding the constraint 
# c.add_unique_constr('BOOKS',['Title', 'Author', 'ISBN'],'book_constraint')
# #Insert values form csv
# c.insert('BOOKS', 'books.csv')

# #Creates BOOKS table
# c.create_table('ASSIGN_TO', 'assign_to.csv', replace=True, req_columns=['ISBN','Cat_id'], pr_keys=['ISBN','Cat_id'], pr_con_name='pr_key_book_cat')
# #Adding the foreign keys
# c.add_foreign_key('ASSIGN_TO','ISBN','BOOKS','ISBN','FK_book_assign')
# c.add_foreign_key('ASSIGN_TO','Cat_id','BOOKS_CATEGORIES','Cat_id','FK_category_assign')
# #Insert values form csv
# c.insert('ASSIGN_TO', 'assign_to.csv')

