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

book_by_category = """
CREATE OR REPLACE Function books_by_category ( cat IN number ) RETURN number
IS
cat_found number;
cursor c1 is
SELECT isbn, cat_id
FROM assign_to;
BEGIN
cat_found := 0;
DELETE FROM books_by_cat_res;
FOR assign_to_rec in c1
LOOP
IF cat = assign_to_rec.cat_id then
-- Inserts to table
INSERT INTO books_by_cat_res VALUES(assign_to_rec.isbn);
cat_found := 1;
end if;
END LOOP;
return cat_found; -- returns 1 if category exists.
END;
"""
has_category = """
CREATE OR REPLACE Function has_category( new_isbn IN number, cat_id IN number )
RETURN number
IS
cursor c1 is
SELECT *
FROM assign_to
where isbn=new_isbn;
BEGIN
FOR assign_to_rec in c1
LOOP
IF cat_id = assign_to_rec.cat_id then
RETURN 1; -- returns 'true' if book has input category.
end if;
END LOOP;
return 0; -- returns 'false' if book does not have input category.
END;
"""
add_book = """
CREATE OR REPLACE PROCEDURE add_book ( new_title IN varchar2, new_author IN varchar2, new_isbn IN number, categ_id IN number )
IS
book_created number(1);
cursor c1 is
SELECT cat_id from book_categories;
BEGIN
book_created :=0;
FOR book_cat_rec in c1
LOOP
if book_cat_rec.cat_id = categ_id then -- adds book if input category exists
book_created := 1;
if book_already_exists(new_isbn) != 1 then -- if book does not exist, it adds it as new in db:
INSERT INTO BOOKS values(new_title, new_author, new_isbn);
-- adds book to db
INSERT INTO ASSIGN_TO values(new_isbn, categ_id); -- assigns category to new book
dbms_output.put_line('Book saved.');
else -- book already exists:
if has_category(new_isbn, categ_id) != 1 then -- if book does not have input category, it adds input cat.
INSERT INTO ASSIGN_TO values(new_isbn, categ_id); -- assigns category to old book
dbms_output.put_line('Book categories updated.');
else -- if book does not have input category, it adds input cat.
dbms_output.put_line('Book already has input category.');
end if;
end if;
end if;
END LOOP;
if book_created = 0 then
dbms_output.put_line('Input category does not exist.');
end if;
END;
"""
return_book_to_library = """
CREATE OR REPLACE PROCEDURE return_book ( isbn_loaned_book IN NUMBER)
IS
d_current_date DATE;
cursor c1 is
SELECT * from Loans
where isbn=isbn_loaned_book;
BEGIN
d_current_date := SYSDATE;
FOR book_rec in c1
LOOP
if is_loan ( isbn_loaned_book)=1 then
UPDATE Loans
SET return_date= d_current_date
WHERE isbn=isbn_loaned_book AND return_date IS NULL;
dbms_output.put_line('Book returned.');
else
dbms_output.put_line('Book is already returned');
end if;
END LOOP;
if book_already_exists(isbn_loaned_book) != 1 then
dbms_output.put_line('Could not find requested book.');
end if;
END;
"""
book_by_author = """
CREATE OR REPLACE PROCEDURE book_by_author ( author_in IN varchar2 )
IS
cursor c1 is
SELECT * from books
where author=author_in;
BEGIN
FOR book_rec in c1
LOOP
dbms_output.put_line('ISBN: '||book_rec.isbn||', Title:
'||book_rec.title||', Author: '||book_rec.author);
END LOOP;
END;
"""
book_by_title = """
CREATE OR REPLACE PROCEDURE book_by_title ( title_in IN varchar2 )
IS
cursor c1 is
SELECT * from books
where title=title_in;
BEGIN
FOR book_rec in c1
LOOP
dbms_output.put_line('ISBN: '||book_rec.isbn||', Title:
'||book_rec.title||', Author: '||book_rec.author);
END LOOP;
END;
"""
book_handler_obj = """
CREATE OR REPLACE TYPE book_handler_obj AS OBJECT
(
id number(3),
-- procedures:
MEMBER PROCEDURE h_book_by_title(title Varchar2),
MEMBER PROCEDURE h_book_by_author(author varchar2),
MEMBER PROCEDURE h_return_book_to_library(isbn NUMBER), -- procedure return book.
MEMBER PROCEDURE h_add_book(new_title varchar2, new_author varchar2, new_isbn number, cat_id number),
MEMBER PROCEDURE h_books_by_category(cat_id NUMBER), -- function books_by_category written as procedure (only prints - does not return).
-- functions:
MEMBER FUNCTION h_has_category(isbn NUMBER, cat_id NUMBER) RETURN NUMBER,
MEMBER FUNCTION h_book_exists(isbn NUMBER) RETURN NUMBER
);
"""

book_handler_obj_body= """
CREATE OR REPLACE TYPE BODY book_handler_obj AS
-- functions:
MEMBER FUNCTION h_has_category(isbn NUMBER, cat_id NUMBER) RETURN NUMBER IS
BEGIN
-- returns 'true' (1) if book has category assigned, else 0.
return has_category(isbn, cat_id);
END h_has_category;
MEMBER FUNCTION h_book_exists(isbn NUMBER) RETURN NUMBER IS
BEGIN
-- returns 1 if book exists in db, else 0.
return book_already_exists(isbn);
END h_book_exists;
-- procedures:
MEMBER PROCEDURE h_books_by_category(cat_id NUMBER) IS
res number;
cursor c1 is
SELECT isbn
FROM books_by_cat_res;
BEGIN
res := books_by_category(cat_id);
if res = 1 then -- category exists.
FOR cat_rec in c1
LOOP
dbms_output.put_line(cat_rec.isbn);
END LOOP;
else
dbms_output.put_line('Requested category does not exist.');
end if;
END h_books_by_category;
MEMBER PROCEDURE h_book_by_title (title Varchar2) IS
BEGIN
book_by_title (title);
END h_book_by_title;
MEMBER PROCEDURE h_book_by_author (author varchar2) IS
BEGIN
book_by_author (author);
END h_book_by_author;
MEMBER PROCEDURE h_return_book_to_library (isbn NUMBER) IS
BEGIN
return_book (isbn);
END h_return_book_to_library;
MEMBER PROCEDURE h_add_book(new_title varchar2, new_author varchar2, new_isbn
number, cat_id number) IS
BEGIN
add_book(new_title, new_author, new_isbn, cat_id);
END h_add_book;
END;
"""

# loan handler object:
upd_deadline_date = """
CREATE OR REPLACE PROCEDURE update_deadline_date ( isbn_loaned_book IN NUMBER, new_deadline DATE)
IS
    cursor c1 is
    SELECT * from Loans
    where isbn=isbn_loaned_book;
BEGIN  
    FOR book_rec in c1
    LOOP      
        IF is_loan ( isbn_loaned_book)=1 then
            if book_rec.loan_date < new_deadline then
                UPDATE Loans 
                SET loan_deadline= new_deadline
                WHERE isbn=isbn_loaned_book AND return_date IS NULL;
                dbms_output.put_line('Deadline date updated.');
            else
                dbms_output.put_line('Did not update deadline (deadline should be after loan date).');                
            end if;
        ELSE
            dbms_output.put_line('The book is already returned.');
        END IF;
    END LOOP;
    if book_already_exists(isbn_loaned_book) != 1 then
        dbms_output.put_line('Could not find requested book.');        
    end if;
END;
"""

get_loans_days = """
CREATE OR REPLACE Function get_loans_days ( isbn IN number ) RETURN number
IS
    res number;
   cursor c1 is
     SELECT isbn, loan_date, return_date
     FROM loans;
BEGIN
    res := is_loan(isbn);
    if res = 1 then
        return 0;
    end if;
   FOR assign_to_rec in c1
   LOOP
      IF isbn = assign_to_rec.isbn then
            if assign_to_rec.return_date is null then
                return to_date(CURRENT_DATE) - assign_to_rec.loan_date; -- book not returned yet.
            else
                return -2;  -- book is returned.
            end if;
      end if;
   END LOOP;
   return -1;
END;
"""

get_fine = """
CREATE OR REPLACE Function get_fine ( isbn IN number, daily_fine_cost IN number ) RETURN number
IS
    res number;
   fine_days number(6);
   calc_days number(6);
   cursor c1 is
     SELECT isbn, loan_deadline, return_date
     FROM loans;
BEGIN
   FOR assign_to_rec in c1
   LOOP
      IF isbn = assign_to_rec.isbn then -- book is loaned:
            --if assign_to_rec.return_date = null then    -- book has not been returned:
            IF assign_to_rec.return_date IS NULL then
                fine_days := to_date(CURRENT_DATE) - assign_to_rec.loan_deadline;
                return daily_fine_cost*fine_days;
            end if;
            calc_days := assign_to_rec.return_date - assign_to_rec.loan_deadline;
            if calc_days <= 0 then
                return 0;
            else
                return daily_fine_cost*calc_days;
            end if;
      end if;
   END LOOP;
   return -1;
END;
"""

loan_handler_obj = """
CREATE OR REPLACE TYPE loans_handler_obj AS OBJECT
(
id number(3),
-- procedures:
MEMBER PROCEDURE h_return_book(isbn_loaned_book NUMBER), 
MEMBER PROCEDURE h_update_deadline_date(isbn_loaned_book NUMBER, new_deadline DATE),

-- functions:
MEMBER Function h_is_loan(isbn NUMBER) RETURN NUMBER, 
MEMBER Function h_get_loans_days ( isbn number )RETURN NUMBER, 
MEMBER Function h_get_fine ( isbn number, daily_fine_cost number ) RETURN NUMBER
);
"""

loan_handler_obj_body = """
CREATE OR REPLACE TYPE BODY loans_handler_obj AS
-- functions:
MEMBER Function h_is_loan(isbn NUMBER) RETURN NUMBER IS
BEGIN
    return is_loan(isbn);
END h_is_loan;
MEMBER Function h_get_loans_days ( isbn number )RETURN NUMBER IS 
BEGIN 
    return get_loans_days(isbn);
END h_get_loans_days;
MEMBER Function h_get_fine ( isbn number, daily_fine_cost number ) RETURN NUMBER IS
BEGIN 
    return get_fine(isbn, daily_fine_cost);
END h_get_fine;
-- procedures:
MEMBER PROCEDURE h_return_book(isbn_loaned_book NUMBER) IS
BEGIN 
    return_book(isbn_loaned_book);
END h_return_book;
MEMBER PROCEDURE h_update_deadline_date(isbn_loaned_book NUMBER, new_deadline DATE) IS 
BEGIN 
    update_deadline_date(isbn_loaned_book, new_deadline );
END h_update_deadline_date;
END;
"""

class Compile():
    def member_handler_obj(cursor):
        '''Compiles required functions and procedures for member handler object.'''
        cursor.execute(book_already_exists)
        cursor.execute(is_loan)
        cursor.execute(lend_book_member)
        cursor.execute(member_handler_obj)
        cursor.execute(member_handler_obj_body)

    def book_handler_obj(cursor):
        '''Compiles required functions and procedures for book handler object.'''
        cursor.execute(book_already_exists)
        cursor.execute(is_loan)
        cursor.execute(has_category)
        cursor.execute(book_by_title)
        cursor.execute(book_by_author)
        cursor.execute(return_book_to_library)
        cursor.execute(add_book)
        cursor.execute(book_by_category)
        cursor.execute(book_handler_obj)
        cursor.execute(book_handler_obj_body)

    def loan_handler_obj(cursor):
        '''Compiles required functions and procedures for loan handler object.'''
        cursor.execute(book_already_exists)
        cursor.execute(is_loan)
        cursor.execute(return_book_to_library)
        cursor.execute(upd_deadline_date)
        cursor.execute(get_loans_days)
        cursor.execute(get_fine)
        cursor.execute(loan_handler_obj)
        cursor.execute(loan_handler_obj_body)
