'''Contains db handler.'''

import os
import csv
import pandas as pd
import cx_Oracle
import config

PATH_INSTANT_CLIENT_ORCL = config.PATH_INSTANT_CLIENT_ORCL
DEF_CSV_FOLDER = config.DEF_CSV_FOLDER
DATE_FORMAT = config.DATE_FORMAT

class Connection():
    """Connect to Database and handles requests."""
    def __init__(self, username: str = None, password: str = None, server: str = 'oracle12c.hua.gr', port: str = '1521', service_name: str = 'orcl', csv_folder_name: str = DEF_CSV_FOLDER) -> None:
        '''
        Creates a connection to an oracle sql server.
        Param: username: the username of the user inside of db.
               password: the password of the user inside of db.
               server: the server address (default is HUA server).
               port: the server's port (default is HUA server's port).
               service_name: the service's name (default is HUA server's service_name).
               csv_folder_name: the folder with all csv files (WARNING: has to be in the same directory as this python file).
        '''
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # gets path of this python file directory
        self.CSV_FOLDER = os.path.join(self.BASE_DIR, csv_folder_name)
        os.makedirs(self.CSV_FOLDER,exist_ok=True)
        if not username:
            self.username=input("Enter your user name for the database server connection: ")
        else:
            self.username = username
        if not password:
            self.password=input("Enter your password: ")
        else:
            self.password = password
        self.conn = self.__connect(server, port, service_name)
        self.cursor=self.conn.cursor()

    def __connect(self, server: str, port: str, service_name: str):
        '''
        Connects to server.
        Param: server: the server address.
               port: the server's port.
               service_name: the service's name.
        Returns: connection to server.
        '''
        try:
            cx_Oracle.init_oracle_client(lib_dir=PATH_INSTANT_CLIENT_ORCL)
            dsn_tns=cx_Oracle.makedsn(server,port,service_name=service_name)
            conn=cx_Oracle.connect(user=self.username,password=self.password,dsn=dsn_tns)
            print("You are connected. Database version:",conn.version)
        except:
            print("Could not connect to requested server")
            exit()
        return conn

    def checkTableExists(self, table_name: str) -> bool:
        '''
        Checks if input table exists.
        Param: table_name: the input table's name.
        Returns: true if table exists, else false.
        '''
        table = table_name.upper()
        _SQL = "SELECT table_name FROM user_tables"
        self.cursor.execute(_SQL)
        results = self.cursor.fetchall()
        results_list = [item[0] for item in results] # Conversion to list of str
        if table in results_list:
            return True
        else:
            return False

    def drop_table(self, table_name: str):
        '''
        Drops requested table.
        Param: table_name: the table to be removed.
        '''
        try:
            self.cursor.execute(f"DROP TABLE {table_name}")
            print(f"Older version of table {table_name} has been dropped.")
        except:
            print(f"Failed to drop older version of table {table_name}. Check for foreign keys or connection to server.")
            print("Reminder: you should always commit in each session (did you commit in oracle sql dev?).")
            # terminate_conn()

    def __data_type(self, column_name, csv_file) -> str:
        '''
        Creates correct datatypes (and their size) by reading csv automatically.
        Param: column_name: the name of the column to check for.
               csv_file: the name of the csv_file.
        '''
        irisData = pd.read_csv(f'{csv_file}',index_col=False)
        v=irisData.get(column_name)
        max_fl=-1    # saves max length number after '.'
        max=1
        isint=True
        isstring=True
        for i in v:
            # if number is int, continues if statement
            # if 1 number is not int -> isint=false for the rest of the column
            if isinstance(i,int) and isint:
                isint=True
            else:
                isint=False
            # same logic here -> if value is not string -> wont be string for the rest of the column
            if isinstance(i, str) and isstring:
                isstring=True
            else:
                isstring=False
            if isinstance(i,float):
                max_fl=1
            # takes length of i and calculates the size we will put in sql server (ex l=2 then number(2) -- if i is also not float) 
            l=len(str(i))
            if max < l:
                max=l
            if max_fl >= 0: # i is float
                c=str(i).split('.')
                lf = len(c[-1])
                if max_fl<lf:
                    max_fl=lf
        if max_fl >=0:  # float values
            return f"NUMBER({max},{max_fl})"
        elif isint: # int values
            return f"NUMBER({max})"
        else:
            return f"VARCHAR2({max})"

    def create_table(self, table_name: str, csv_name: str, replace: bool = False, req_columns: list = None, date_columns: list = None, pr_keys: list = None, pr_con_name: str = None) -> None:
        '''
        Creates new table (or replaces it).
        Param: table_name: the input table name.
               csv_name: the name of the csv file.
               replace: if true (and if table exists), re-creates table.
               req_columns: list of columns required in table (use it for foreign keys or primary keys).
               date_columns: list of columns that are dates.
               pr_keys: list of primary keys (make sure they exist in csv file) - optional.
               pr_con_name: the name of the primary key constraint - optional.
        '''
        tmp_csv_name = os.path.join(self.CSV_FOLDER, csv_name)
        if (not tmp_csv_name.endswith(".csv")):
            tmp_csv_name+=".csv"
        if not os.path.exists(tmp_csv_name):
            print("Could not find requested csv file in csv folder.")
            self.__del__()
            return

        table_exists = self.checkTableExists(table_name)
        if table_exists and replace:
            self.drop_table(table_name)
        elif table_exists and not replace:
            print('Table already exists (you can replace it).')
            return

        columns = self.__get_columns(tmp_csv_name, req_columns)

        print(f"Creating new table {table_name}...")
        str=""
        for i in columns:
            r=self.__data_type(i,tmp_csv_name)
            if date_columns is not None and i in date_columns:
                r = 'DATE'
            # r contains data type of column (ex number(3,1))
            str += i +" "+r+", "
        self.cursor.execute(f"CREATE TABLE {table_name} ({str[:-2]})")   # str -> removes these last 2 characters : ', '
        print(f"{table_name} table has been created..............")

        if pr_keys is not None:
            print('Inserting primary keys.....')
            self.add_primary_key(table_name, pr_keys, pr_con_name)

    def __del__(self):
        self.terminate_conn()

    def terminate_conn(self) -> None:
        '''Closes connection to server and exits program.'''
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def __get_columns(self, csv_name: str, req_columns: list = None) -> list:
        '''
        Gets columns of input csv and checks if there are any required columns missing.
        Param: csv_name: the name of the csv file.
               req_columns: a list of columns required in table.
        Returns: a list of column names (according to csv file).
        '''
        # with the variable name as csv_file
        with open(csv_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')
            list_of_column_names = []
            for row in csv_reader:
                list_of_column_names.append(row)
                break
        # checks for input table if it has required columns:
        if req_columns is None:
            return list_of_column_names[0]
        for r_c in req_columns:
            if r_c not in list_of_column_names[0]:
                print(f'Required column "{r_c}" does not exist in csv file.')
                raise RuntimeError
        # returns column names:
        return list_of_column_names[0]

    def __get_columns_str(self, csv_name: str) -> str:
        '''Returns columns of requested csv file as a string.'''
        col = self.__get_columns(csv_name)
        if len(col) <= 1:
            return col
        else:
            return ', '.join(col)

    def __num_values_str(self, csv_name: str) -> str:
        '''
        Returns the enumerate values of csv columns.
        Param: csv_name: the name of the csv file.
        '''
        l=self.__get_columns(csv_name)
        str=""
        count=1
        for i in l:
            str+=(":"+f"{count}"+",")
            count+=1
        return str[:-1]

    def delete_contents(self, table_name: str) -> None:
        '''
        Deletes contents from input table
        Param: table_name: the requested table.
        '''
        if not self.checkTableExists(table_name):
            print('Cannot delete contents of non existing table.')
            return
        self.cursor.execute(f"DELETE FROM {table_name}")
        print(f'Previous contents of table "{table_name}" have been deleted.')

    def insert(self, table_name: str, csv_name: str = None, delete_prev_recs: bool = False) -> None:
        '''
        Inserts data of csv to input table.
        Param: table_name: the name of the table for the data to be saved to.
               csv_name: the name of the csv file for the data to be saved.
               delete_prev_recs: if true, deletes all previous records of input table.
        '''
        if not self.checkTableExists(table_name):
            print('Requested table does not exist. Please create it first.')
            return
        tmp_csv_name = os.path.join(self.CSV_FOLDER, csv_name)
        if (not tmp_csv_name.endswith(".csv")):
            tmp_csv_name+=".csv"
        if not os.path.exists(tmp_csv_name):
            print("Could not find requested csv file in csv folder.")
            self.__del__()
            return

        if delete_prev_recs:
            self.delete_contents(table_name)

        # gets column names
        column_names=self.__get_columns_str(tmp_csv_name)
        if (not column_names):
            print("CSV File is empty")
            self.terminate_conn()
        num_values=self.__num_values_str(tmp_csv_name)
        # self.__create_table(table_name,csv_name, replace)
        irisData = pd.read_csv(f'{tmp_csv_name}',index_col=False)
        irisData.head()
        print(f"Inserting data from requested csv into table {table_name}....")
        try:
            self.cursor.execute(f"ALTER SESSION SET NLS_DATE_FORMAT='{DATE_FORMAT}'")
            for i,row in irisData.iterrows():
                sql = f"INSERT INTO {table_name} ({column_names}) VALUES({num_values})"
                row.fillna('', inplace=True)
                self.cursor.execute(sql, tuple(row))
                # the connection is not autocommitted by default, so we must commit to save our changes
            self.conn.commit()
            print("Records inserted succesfully")
        except:
            print(f"Failed to insert csv to table {table_name}. Check for incorrect data types or constraints (ex repetition of primary keys) in the requested csv file.")

    def add_foreign_key(self, table1: str, f_col1: str, table2: str, pk_table2: str, fk_con_name: str = None) -> None:
        '''
        Adds a foreign key.
        Param: table1: the table to add the foreign key to.
               f_col1: the column of table1 to become foreign key (make sure it exists).
               table2: the table for the foreign key to refer to.
               pk_table2: the column of table2 that the foreign key refers to.
               fk_con_name: input constraint name for foreign key (optional).
        '''
        if not self.checkTableExists(table1):
            print(f'Requested table {table1} does not exist')
            return
        if not self.checkTableExists(table2):
            print(f'Requested table {table2} does not exist')
            return
        if fk_con_name is None:
            fk_con_name =  f'FK_{f_col1}_{pk_table2}'
        exec_string = f"ALTER TABLE {table1} add Constraint {fk_con_name} Foreign Key({f_col1}) REFERENCES {table2}({pk_table2})"
        try:
            self.cursor.execute(exec_string)
            self.conn.commit()
            print(f'Requested Foreign Keys added to tables {table1} and {table2}')
        except:
            print("Failed to add foreign key constraints (make sure that requested columns exist or primary key exists or change contstraint name).")
            print("Reminder: cannot reference a primary key of a combination of primary keys with a foreign key")

    def add_primary_key(self, table_name: str, primary_key: list, pr_con_name: str = None) -> None:
        '''
        Adds a primary key.
        Param: table_name: the table to add the primary key.
               primary_key: the column of input table to become primary key (make sure it exists).
               pk_con_name: input constraint name for primary key (optional).
        '''
        if not self.checkTableExists(table_name):
            print(f'Requested table {table_name} does not exist')
            return
        if len(primary_key) == 0:
            print('Could not import primary keys => not defined in function call.')
            return
        if len(primary_key) == 1:
            prString = primary_key[0]
        else:
            prString = ', '.join(primary_key)
        if pr_con_name is None:
            pr_con_name =  f'PK_{table_name}'
        exec_string = f"ALTER TABLE {table_name} ADD CONSTRAINT {pr_con_name} PRIMARY KEY ({prString})"
        try:
            self.cursor.execute(exec_string)
            self.conn.commit()
            print(f'Requested Primary Keys added to table {table_name}')
        except:
            print("Failed to add primary key constraints (make sure that requested columns exist or change contstraint name).")

    def check_col_exist(self, table_name: str, col_name: str) -> bool:
        '''
        Checks if column exists.
        Param: table_name: the table's name.
               col_name: the column's name to check for.
        Returns: true if column exists in specified table, else false.
        '''
        if not self.checkTableExists(table_name):
            print('Requested Table does not exist.')
            return False
        try:
            self.cursor.execute(f'SELECT {col_name} FROM {table_name}')
            return True
        except:
            return False

    def add_unique_constr(self, table_name: str, col: list, constr_name: str = None) -> None:
        '''
        Adds unique constraint.
        Param: table_name: the name of the table to add the unique constraints to.
               col: list of columns
        '''
        if not self.checkTableExists(table_name):
            print(f'Requested table {table_name} does not exist')
            return
        if len(col) == 0:
            print('Unique columns not defined in function call, could not execute.')
            return
        if len(col) == 1:
            uniqString = col[0]
        else:
            uniqString = ', '.join(col)
        if constr_name is None:
            constr_name =  f'uniq_{table_name}'
        exec_string = f"ALTER TABLE {table_name} ADD CONSTRAINT {constr_name} UNIQUE ({uniqString})"
        try:
            self.cursor.execute(exec_string)
            self.conn.commit()
            print(f'Requested unique constraints added to table {table_name}')
        except:
            print("Failed to add unique key constraints (make sure that requested columns exist or change contstraint name).")
