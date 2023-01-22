'''Main class.'''

from lib.handler import *

c = Connection('ITxxxx', 'ITxxxx')

# Creates book categories table & inserts data:
c.create_table('BOOK_CATEGORIES', 'book_categories.csv', replace=True, req_columns=['Title', 'Cat_id'], pr_keys=['Cat_id'], pr_con_name='pr_key_cat')
c.insert('BOOK_CATEGORIES', 'book_categories.csv')

# Creates books table & inserts data (also adds constraints):
c.create_table('BOOKS', 'books.csv', replace=True, req_columns=['Title', 'Author','ISBN'], pr_keys=['ISBN'], pr_con_name='pr_book_key')
c.add_unique_constr('BOOKS',['Title', 'Author', 'ISBN'],'book_constraint')
c.insert('BOOKS', 'books.csv')

# Creates assign_to table & inserts data (also adds constraints):
c.create_table('ASSIGN_TO', 'assign_to.csv', replace=True, req_columns=['ISBN','Cat_id'], pr_keys=['ISBN','Cat_id'], pr_con_name='pr_key_book_cat')
c.add_foreign_key('ASSIGN_TO','ISBN','BOOKS','ISBN','FK_book_assign')
c.add_foreign_key('ASSIGN_TO','Cat_id','BOOKS_CATEGORIES','Cat_id','FK_category_assign')
c.insert('ASSIGN_TO', 'assign_to.csv')

# Creates members table & inserts data (also adds constraints):
c.create_table('MEMBERS', 'members.csv', replace=True, req_columns=['id', 'name', 'address'], pr_keys=['id'], pr_con_name='pr_key_memb')
c.add_unique_constr('MEMBERS', ['id', 'name', 'address'], 'member_constraint')
c.insert('MEMBERS', 'members.csv')

# Creates loans table & inserts data (also adds constraints):
c.create_table('LOANS', 'loans.csv', replace=True, req_columns=['loan_date', 'loan_deadline', 'member_id', 'ISBN', 'return_date'], pr_keys=['ISBN', 'member_id'], pr_con_name='pr_key_book_memb')
c.add_foreign_key('LOANS', 'ISBN', 'BOOKS', 'ISBN', 'FK_loans_books')
c.add_foreign_key('LOANS', 'member_id', 'MEMBERS', 'id', 'FK_loans_members')
c.insert('LOANS', 'loans.csv')
