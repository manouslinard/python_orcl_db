book_already_exists = """
CREATE OR REPLACE Function book_already_exists( isbn IN number ) RETURN number
IS
   cursor c1 is
     SELECT isbn
     FROM books;
BEGIN
   FOR book_rec in c1
   LOOP
      IF isbn = book_rec.isbn then
            RETURN 1;
      end if;
   END LOOP;
   return 0;
END;
"""
is_loan = """
CREATE OR REPLACE Function is_loan ( isbn IN number ) RETURN number
IS
   -- total_val number(6);
   res number;
   cursor c1 is
     SELECT isbn, return_date
     FROM loans;
BEGIN
   FOR assign_to_rec in c1
   LOOP
      IF isbn = assign_to_rec.isbn then
            if assign_to_rec.return_date is null then
                RETURN 1;   -- book is loaned.
            else
               return 0;    -- book is not loaned.
            end if;
      end if;
   END LOOP;
   res := book_already_exists(isbn);
   if res = 1 then
        return -1;   -- book is not in loans
    else
        return -2;  -- book does not even exist.
    end if;
END;
"""
lend_book_member = """
-- 2.3 Answer
CREATE OR REPLACE PROCEDURE lend_book_to_member ( isbn_lend in number, member_id in number, days_until_deadline in number )
IS
 	result number;
BEGIN
  result :=  is_loan (isbn_lend);
  if result = 1 then
        dbms_output.put_line('Book is loaned and you cant lend it');
    elsif result = 0 then -- book is not loaned and exists.
        dbms_output.put_line('Book is not loaned. You can have it.');
        -- update if exists in loans:
        UPDATE Loans SET loan_date= CURRENT_DATE, loan_deadline = CURRENT_DATE+days_until_deadline, member_id = member_id, return_date = null where isbn = isbn_lend;
    elsif result = -1 then    -- book is not inserted in loans table:
        -- insert if not exists in loans:
        dbms_output.put_line('Book is not loaned. You can have it.');
        insert into loans values(CURRENT_DATE,CURRENT_DATE+days_until_deadline,member_id,isbn_lend,null);
    else
        dbms_output.put_line('Book does not exist.');        
   end if;
END;
"""
member_handler_obj = """
-- 3.2 Answer
CREATE OR REPLACE TYPE member_handler_obj AS OBJECT
(
id number(3),
-- procedures:
MEMBER PROCEDURE h_lend_book_to_member(isbn_lend in number, member_id in number, days_until_deadline in number),
MEMBER PROCEDURE h_add_new_member(new_member_id number, member_fullname varchar2, member_address varchar2)
);
"""
member_handler_obj_body = """
CREATE OR REPLACE TYPE BODY member_handler_obj AS
MEMBER PROCEDURE h_lend_book_to_member (isbn_lend in number, member_id in number, days_until_deadline in number) IS
BEGIN
	lend_book_to_member (isbn_lend,member_id,days_until_deadline);
END h_lend_book_to_member;

MEMBER PROCEDURE h_add_new_member (new_member_id number, member_fullname varchar2, member_address varchar2) IS
BEGIN
	add_new_member (new_member_id, member_fullname, member_address);
END h_add_new_member;
END;
"""

class Compile():
    def member_handler_obj(cursor):
        '''Compiles required functions and procedures for member handler object'''
        cursor.execute(book_already_exists)
        cursor.execute(is_loan)
        cursor.execute(lend_book_member)
        cursor.execute(member_handler_obj)
        cursor.execute(member_handler_obj_body)

    def book_handler_obj(cursor):
        '''Compiles required functions and procedures for book handler object'''
        # TODO
