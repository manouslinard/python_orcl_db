insert.py inserts data from a csv file to a requested table in sql server.

CONNECTION ====================================================

If you check the sript, on the top you will see some variables that you can change. Configure these variables as shown below:

First of all change the path of your instant client directly in the python script so the instant client will be configured correctly.

You can also type the username and password you use to connect to database server (if you do not do so, program will ask you to type them when executed).

If you want to change the database server you connect to, change the SERVER variable.


EXECUTION =====================================================

To run it, type in cmd the following:

py -i insert.py

or

python3 -i insert.py

depending on the version of python and os you are using


CSV ============================================================

User inserts the name (with or without the '.csv') and the table that they want to insert the csv file to.

The values of the csv file are separated with commas (,).
Also the first row of the csv file has to have the names of the columns.

**The names of the csv files have to be in lowercase. 

All the csv files have to be saved to the folder 'INSERT_CSV_HERE' in order for python to find the (csv) files.

If the input table does not exist, it creates a new one with the suitable data types automatically by checking the values of each column (except if the data type is other than int, float or string, then it asks user).


TABLES =========================================================

If the table does exist, the user has 2 options:

1) Append the existing table:

	With append, the input csv file is being inserted as is to the requested table.
	Input csv has to have the same sequence of columns (and the corresponding data) as the table in the database. If it differs, then the insertion cannot be executed. 
	Like so, the user has the old entries of the table and inserts some new ones (the ones from the csv file that is).

	The table will fail to insert if there is any repetition of unique (constraint) columns (example csv file has the same primary keys as some entries in the existing table)


2) Not appending the existing table:
	When user chooses this option, the older verion of the requested table is dropped, thus losing all older entries.
	The table however is being recreated with the datatypes and columns (column names) of the input csv file.

	The drop of a table may fail if there is any constraint that prevents the droping of the table (example foreign keys). 
	User has to delete foreign key constraints directly from the database in order to be able to drop the requested table (when choosing not to append it).

	