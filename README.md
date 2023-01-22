### Manual
This is a short manual on the setup before executing any scripts.

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

### Execution:

To run test program, please run main.py

---

### CSV Insertion:

All the csv files have to be saved to the folder 'INSERT_CSV_HERE' in order for python to find the (csv) files.

If the input table does not exist, it creates a new one with the suitable data types automatically by checking the values of each column.

You can change the name of the folder 'INSERT_CSV_HERE' (<ins>not</ins> its location). It is recommended to change def_folder_name in configuration (see at the top of config.py) to the name of your folder or define it in constructor.

Warning: Requested csv files should not be completely empty, else code does not work.
