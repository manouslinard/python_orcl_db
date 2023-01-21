import cx_Oracle
from connection import Connection

FUNC_ERROR = -100

# source: https://stackoverflow.com/questions/72533233/how-can-i-get-the-dbms-output-in-python
def get_dbms_output(cursor, print_res=True):
    '''Prints & returns result of dbms_output.'''
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

    def lend_book(self, isbn: int, member_id: int, days_deadline: int):
        '''Lends a book to a member (with deadline).'''
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

    def add_member(self, new_member_id: int, member_fullname: str, member_address: str):
        '''Adds a new member.'''
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

    def has_category(self, isbn: int, cat_id: int):
        '''Checks if input isbn (book) has input category (id).'''
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
            return FUNC_ERROR


c = Connection('ITxxxxx', 'ITxxxxxxx')
m = MemberHandler(c)
m.lend_book(9789606355516, 9, 7)
m.add_member(14,'Nikos Papas','Axompa 2')

b = BookHandler(c)
print(b.has_category(1111111111113, 1))
