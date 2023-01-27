### Description

* This project was made as an bonus assignment to the lesson 'Databases' at [HUA](https://www.hua.gr/index.php/el/). Basically it handles a book library from python using csv files. It is important however to emphasize that some of its classes (like connection class - see below) can be used regardless in other projects that need a way to connect to an oracle database and handle it with csv files using python (it is also recommended to include config.py file in parent directory for easier configuration).

* This README file is a short manual on the setup before executing any scripts.

---

### Prerequisites:

Install [oracle instant client](https://www.oracle.com/database/technologies/instant-client/downloads.html). Here is a helpful [tutorial](https://www.youtube.com/watch?v=v0TkfVFGO5c) (for windows) to do so.

---

### Configuration:

In config.py file, you can change the following:

- Change the path of your instant client directly in the config.py script so the instant client will be configured correctly (see at the top of config.py).

- Enter your credentials (username + password to database).

- Date format: put the format that you want to save in database.

- Connect with vpn to oracle server (if needed).

---

### Connection class:

The Connection class is a useful class to connect and handle a oracle database with csv files from python. It contains methods such as create, insert (and others) that can be used for handling a database (from python). It also attempts to detect and block any sql injections statements. This class can be used in other projects and not only this one (you should also contain config.py file in parent directory for easier configuration).


---

### Execution:

To run test program, please run main.py

---

### CSV Insertion:

All the csv files have to be saved to the folder 'INSERT_CSV_HERE' in order for python to find the (csv) files.

If the input table does not exist, it creates a new one with the suitable data types automatically by checking the values of each column (except if the data type is other than int, float - double, string or date, then it asks user).

You can change the name of the folder 'INSERT_CSV_HERE' (<ins>not</ins> its location). It is recommended to change def_folder_name in configuration (see at the top of config.py) to the name of your folder or define it in constructor.

Warning: Requested csv files should not be completely empty, else code does not work.
