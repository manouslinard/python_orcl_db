'''Main class.'''

from lib.handler import *

c = Connection('IT22064', 'IT22064')

# Creates book categories table & inserts data:
c.create_table('BOOK_CATEGORIES', 'book_categories.csv', replace=True, req_columns=['Title', 'Cat_id'], pr_keys=['Cat_id'], pr_con_name='pr_key_cat')
c.insert('BOOK_CATEGORIES', 'book_categories.csv')

# Creates members table & inserts data:
c.create_table('MEMBERS', 'members.csv', replace=True, req_columns=['id', 'name', 'address'], pr_keys=['id'], pr_con_name='pr_key_memb')
c.add_unique_constr('MEMBERS', ['id', 'name', 'address'], 'member_constraint')
c.insert('MEMBERS', 'members.csv')

# Creates loans table & inserts data:
c.create_table('LOANS', 'loans.csv', replace=True, req_columns=['loan_date', 'loan_deadline', 'member_id', 'ISBN', 'return_date'], pr_keys=['ISBN', 'member_id'], pr_con_name='pr_key_book_memb')
c.add_foreign_key('LOANS', 'ISBN', 'BOOKS', 'ISBN', 'FK_loans_books')
c.add_foreign_key('LOANS', 'member_id', 'MEMBERS', 'id', 'FK_loans_members')
c.insert('LOANS', 'loans.csv')

# m = LoansHandler(c)
# m.update_deadline_date(1111111111111, '2023-01-15')
