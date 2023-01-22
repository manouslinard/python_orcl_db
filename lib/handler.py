'''Handler methods.'''

import cx_Oracle
from lib.connection import Connection
from lib.handlerConst import Compile
from config import DATE_FORMAT

# source: https://stackoverflow.com/questions/72533233/how-can-i-get-the-dbms-output-in-python
def get_dbms_output(cursor, print_res=True) -> str:
    '''
    Returns result of dbms_output.
    Param: print_res: if true, prints result to console.
    '''
    #   variable to colect serveroutputs into
    dbmsRet = ''
    chunk = 100
    # create variables to hold the output
    mLine = cursor.arrayvar(str, chunk)
    mNumLines = cursor.var(int)
    mNumLines.setvalue(0, chunk)
    # fetch the text that was added by PL/SQL
    while True:
        cursor.callproc("dbms_output.get_lines", (mLine, mNumLines))
        num_lines = int(mNumLines.getvalue())
        lines = mLine.getvalue()[:num_lines]
        for line in lines:
            dbmsRet = dbmsRet + line + '\n'
        if num_lines < chunk:
            break
    if print_res:
        print(dbmsRet)
    return dbmsRet


class MemberHandler():
    def __init__(self, conn: Connection) -> None:
        '''
        Creates a member handler object.
        Param: username: the username of the user inside of db.
               password: the password of the user inside of db.
               server: the server address (default is HUA server).
               port: the server's port (default is HUA server's port).
               service_name: the service's name (default is HUA server's service_name).
               csv_folder_name: the folder with all csv files (WARNING: has to be in the same directory as this python file).
        '''
        self.conn = conn
        self.cursor = self.conn.conn.cursor()
        self.cursor.callproc("dbms_output.enable")  # enables dbms output
        Compile.member_handler_obj(self.cursor)

    def lend_book(self, isbn: int, member_id: int, days_deadline: int) -> None:
        '''
        Lends a book to a member (with deadline).
        Param: isbn: the book's isbn.
               member_id: the id of the member that wants the book.
               days_deadline: the days of the deadline.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    member_handler member_handler_obj;
                BEGIN
                    member_handler := member_handler_obj(0);
                    member_handler.h_lend_book_to_member({isbn},{member_id},{days_deadline});
                END;
                """
            )
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)

    def add_member(self, new_member_id: int, member_fullname: str, member_address: str) -> None:
        '''
        Adds a new member.
        Param: new_member_id: the id of the new member.
               member_fullname: the fullname of the new member.
               member_address: the address of the new member.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    member_handler member_handler_obj;
                BEGIN
                    member_handler := member_handler_obj(0);
                    member_handler.h_add_new_member({new_member_id},'{member_fullname}','{member_address}');
                END;
                """
            )
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)


class BookHandler():
    def __init__(self, conn: Connection) -> None:
        '''
        Creates a member handler object.
        Param: username: the username of the user inside of db.
               password: the password of the user inside of db.
               server: the server address (default is HUA server).
               port: the server's port (default is HUA server's port).
               service_name: the service's name (default is HUA server's service_name).
               csv_folder_name: the folder with all csv files (WARNING: has to be in the same directory as this python file).
        '''
        self.conn = conn
        self.cursor = self.conn.conn.cursor()
        self.cursor.callproc("dbms_output.enable")  # enables dbms output
        if not conn.checkTableExists("books_by_cat_res"):
            books_by_cat_res = """create table books_by_cat_res(ISBN NUMBER(13))"""
            self.cursor.execute(books_by_cat_res)
        Compile.book_handler_obj(self.cursor)

    def has_category(self, isbn: int, cat_id: int) -> bool:
        '''
        Checks if input book belongs to a specified category.
        Param: isbn: the isbn of the book.
               cat_id: the id of the category.
        Returns: true if book has input category, else false.
        '''
        try:
            self.cursor.execute(f"""
                    DECLARE
                        book_handler book_handler_obj;
                        result number;
                    BEGIN
                        book_handler := book_handler_obj(0);
                        result := book_handler.h_has_category({isbn}, {cat_id});
                        dbms_output.put_line(result); --prints 1 if book has category assigned, else 0.
                    END;
                """
            )
            r = int(get_dbms_output(self.cursor, print_res=False))
            return bool(r)
        except cx_Oracle.Error as error:
            print(error)
            return False
    
    def book_by_title(self, title: str) -> None:
        '''
        Finds books by input title.
        Param: title: the title to look for.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    book_handler book_handler_obj;
                BEGIN
                    book_handler := book_handler_obj(0);
                    book_handler.h_book_by_title('{title}');
                END;
                """
            )
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)
    
    def book_by_author(self, author:str) -> None:
        '''
        Finds books by input author.
        Param: author: the author to look for.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    book_handler book_handler_obj;
                BEGIN
                    book_handler := book_handler_obj(0);
                    book_handler.h_book_by_author('{author}');
                END;
                """
            )
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)
    
    def return_book_to_library(self, isbn:int) -> None:
        '''
        Returns input book to the library.
        Param: isbn: the isbn of the book to be returned.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    book_handler book_handler_obj;
                BEGIN
                    book_handler := book_handler_obj(0);
                    book_handler.h_return_book_to_library({isbn});
                END;
                """
            )
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)
    
    def add_book(self, new_tite: str, new_author: str, new_isbn: int, cat_id: int) -> None:
        '''
        Adds a book.
        Param: new_title: the title of the book.
               new_author: the author's name.
               new_isbn: the isbn of the new book.
               cat_id: the category id of the book.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    book_handler book_handler_obj;
                BEGIN
                    book_handler := book_handler_obj(0);
                    book_handler.h_add_book('{new_tite}','{new_author}',{new_isbn},{cat_id});
                END;
                """
            )
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)
    
    def books_by_category(self, cat_id: int) -> None:
        '''
        Prints books by input category id.
        Param: cat_id: the category id.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    book_handler book_handler_obj;
            
                BEGIN
                    book_handler := book_handler_obj(0);
                    book_handler.h_books_by_category({cat_id});
                    
                END;
                """
            )
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)
    
    def book_exists(self, isbn: int) -> bool:
        '''
        Returns true if input isbn exists, else false.
        Param: isbn: the isbn of the book.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    book_handler book_handler_obj;
                    result number;
            
                BEGIN
                    book_handler := book_handler_obj(0);
                    result := book_handler.h_book_exists({isbn});
                    dbms_output.put_line(result);
                    
                END;
                """
            )
            r = int(get_dbms_output(self.cursor, print_res=False))
            return bool(r)
        except cx_Oracle.Error as error:
            print(error)

class LoansHandler():
    def __init__(self, conn: Connection) -> None:
        '''
        Creates a loans handler object.
        Param: username: the username of the user inside of db.
               password: the password of the user inside of db.
               server: the server address (default is HUA server).
               port: the server's port (default is HUA server's port).
               service_name: the service's name (default is HUA server's service_name).
               csv_folder_name: the folder with all csv files (WARNING: has to be in the same directory as this python file).
        '''
        self.conn = conn
        self.cursor = self.conn.conn.cursor()
        self.cursor.callproc("dbms_output.enable")  # enables dbms output
        Compile.loan_handler_obj(self.cursor)

    def return_book(self, isbn_loaned_book: int) -> None:
        '''
        Returns book with input isbn.
        Param: isbn_loaned_book: the input isbn of the requested book.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    loans_handler loans_handler_obj;
                    result number;
                BEGIN
                    loans_handler := loans_handler_obj(0);
                    loans_handler.h_return_book({isbn_loaned_book});
                END;
                """
            )
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)

    def update_deadline_date(self, isbn_loaned_book: int, new_deadline: str) -> None:
        '''
        Updates deadline date.
        Param: isbn_loaned_book: the isbn of the book for its date to be updated.
               new_deadline: date of the new deadline.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""ALTER SESSION SET NLS_DATE_FORMAT='{DATE_FORMAT}'""")
            self.cursor.execute(f"""
                DECLARE
                    loans_handler loans_handler_obj;
                    result number;
                BEGIN
                    loans_handler := loans_handler_obj(0);
                    loans_handler.h_update_deadline_date({isbn_loaned_book}, '{new_deadline}');
                END;
                """
            )
            
            self.conn.conn.commit()
            get_dbms_output(self.cursor)
        except cx_Oracle.Error as error:
            print(error)

    def is_loan(self, isbn: int) -> int:
        '''
        Checks if book is loaned.
        Param: isbn: the book's isbn to check if loaned.
        Returns: true if book is loaned, else false.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    loans_handler loans_handler_obj;
                    result number;
            
                BEGIN
                    loans_handler := loans_handler_obj(0);
                    result := loans_handler.h_is_loan({isbn});
                    dbms_output.put_line(result);
                    
                END;
                """
            )
            r = int(get_dbms_output(self.cursor, print_res=False))
            return r
        except cx_Oracle.Error as error:
            print(error)
    
    def get_loans_days(self, isbn: int) -> int:
        '''
        Returns the days that a book is loaned.
        Param: isbn: the isbn of the requested book.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    loans_handler loans_handler_obj;
                    result number;
            
                BEGIN
                    loans_handler := loans_handler_obj(0);
                    result := loans_handler.h_get_loans_days({isbn});
                    dbms_output.put_line(result);
                END;
                """
            )
            r = int(get_dbms_output(self.cursor, print_res=False))
            return r
        except cx_Oracle.Error as error:
            print(error)

    def get_fine(self,isbn: int, daily_fine_cost: int) -> int:
        '''
        Calculates and returns the fine of the requested book.
        Param: isbn: the requested book isbn.
               daily_fine_cost: the dayly fine cost.
        '''
        try:
            # call the stored procedure
            self.cursor.execute(f"""
                DECLARE
                    loans_handler loans_handler_obj;
                    result number;
            
                BEGIN
                    loans_handler := loans_handler_obj(0);
                    result := loans_handler.h_get_fine({isbn}, {daily_fine_cost});
                    dbms_output.put_line(result);
                    
                END;
                """
            )
            r = int(get_dbms_output(self.cursor, print_res=False))
            return r
        except cx_Oracle.Error as error:
            print(error)
