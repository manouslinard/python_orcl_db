'''Main class.'''

from lib.handler import *
from config import CLIENT_USERNAME, CLIENT_PASSWORD

def create_lib_tables(c: Connection):
    '''
    Creates all required tables for library.
    Param: c: the connection to database.
    '''
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
    c.create_table('LOANS', 'loans.csv', replace=True, req_columns=['loan_date', 'loan_deadline', 'member_id', 'ISBN', 'return_date'], date_columns=['loan_date', 'loan_deadline', 'return_date'], pr_keys=['ISBN', 'member_id'], pr_con_name='pr_key_book_memb')
    c.add_foreign_key('LOANS', 'ISBN', 'BOOKS', 'ISBN', 'FK_loans_books')
    c.add_foreign_key('LOANS', 'member_id', 'MEMBERS', 'id', 'FK_loans_members')
    c.insert('LOANS', 'loans.csv')

def drop_lib_tables(c: Connection):
    '''
    Drops existing tables of library.
    Param: c: the connection to database.
    '''
    if c.checkTableExists('ASSIGN_TO'):
        c.drop_table('ASSIGN_TO')
    if c.checkTableExists('LOANS'):
        c.drop_table('LOANS')
    if c.checkTableExists('BOOK_CATEGORIES'):
        c.drop_table('BOOK_CATEGORIES')
    if c.checkTableExists('MEMBERS'):
        c.drop_table('MEMBERS')
    if c.checkTableExists('BOOKS'):
        c.drop_table('BOOKS')

def test_book_handler(book_handler: BookHandler):
    '''Tests all functions & procedures of book handler object.'''
    print('Result of h_books_by_category:')
    book_handler.books_by_category(1)
    print('Result of h_book_by_title:')
    book_handler.book_by_title('Little Prince')
    print('Result of h_book_by_author:')
    book_handler.book_by_author('Gwendal Fossois')
    print('Result of h_return_book_to_library:')
    book_handler.return_book_to_library(9876543210987)
    print('Result of h_add_book:')
    book_handler.add_book('Lord of the rings 3', 'J.R.R. Tolkien', 1111111111113, 1)
    result = book_handler.has_category(1111111111113, 1)
    print(f'Result of h_has_category: {result}') # prints 1 if book has category assigned, else 0.
    result = book_handler.book_exists(1111111111113)
    print(f'Result of h_book_exists: {result}') # prints 1 if book exists in db, else 0.

def test_member_handler(member_handler: MemberHandler):
    '''Tests all functions & procedures of member handler object.'''
    member_handler.lend_book(5555555555555,1,7)
    print('Book lended succesfully')
    member_handler.add_member(20,'Nikos Papas','Marousi')

def test_loan_handler(loans_handler: LoansHandler):
    '''Tests all functions & procedures of loan handler object.'''
    print('Result of h_return_book:')
    loans_handler.return_book(9789606355516)
    print('Result of h_update_deadline_date:')
    loans_handler.update_deadline_date(1111111111111, '2023-1-15')
    print('Result of h_is_loan: ')
    result = loans_handler.is_loan(5555555555555)
    if result == 1:
       print('Book is loaned.')
    elif result == -2:
       print('Book does not exist.')
    else:
       print('Book is not loaned.')
    print('Result of h_get_loans_days: ')
    result = loans_handler.get_loans_days(9789606355516)
    if result == -1:
        print('Book not found.')
    elif result == -2:
        print('Book has been returned.')
    elif result == 0:
        print('Book is still on deadline.')
    else:
        print(result)
    result = loans_handler.get_fine(1111111111111, 2)
    if result == -1:
        print('Book not found in loans.')
    else:
        print(f'Result of h.get_fine: {result}')

if __name__ == "__main__":
    '''Tests all library:'''
    c = Connection(username=CLIENT_USERNAME, password=CLIENT_PASSWORD)
    drop_lib_tables(c)
    create_lib_tables(c)
    
    b_h = BookHandler(c)
    test_book_handler(b_h)

    m_h = MemberHandler(c)
    test_member_handler(m_h)

    l_h = LoansHandler(c)
    test_loan_handler(l_h)
