import sqlite3
import uuid
import hashlib
import bcrypt
from datetime import datetime

# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self):
        self.conn = sqlite3.connect("database.db", uri=True)
        self.cur = self.conn.cursor()

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    #-----------------------------------------------------------------------------
    
    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin'):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.commit()

        # Create the users table
        self.execute("""CREATE TABLE Users(
            username TEXT UNIQUE,
            password TEXT,
            salt TEXT,
            admin INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            block_time DATETIME DEFAULT NULL
        )""")

        self.commit()

        # Add our admin user
        self.add_user('admin', admin_password, admin=1)

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

     # Add a user to the database
    def add_user(self, username, password, admin):
        sql_cmd = """
                INSERT INTO Users(username, password, salt, admin)
                VALUES('{username}', '{password}', '{salt}', {admin})
           """

        # Generate a random number as salt.
        salt = uuid.uuid4().hex

        password_salt = salt + password
        password_hash = hashlib.sha256(password_salt.encode()).hexdigest()

        # Hash the password
        password_double_encrypted = bcrypt.hashpw(password_hash.encode('ascii'), bcrypt.gensalt()).hex()

        sql_cmd = sql_cmd.format(username=username, password=password_double_encrypted, salt=salt, admin=admin)

        self.execute(sql_cmd)
        self.commit()
        return True

    #-----------------------------------------------------------------------------

    def get_user(self, username):
        sql_query = """
                SELECT * 
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        self.commit()

        return self.cur.fetchall()

    def debug(self):
        sql_query = """
                SELECT * 
                FROM Users
            """
            
        self.execute(sql_query)
        self.commit()

        return self.cur.fetchall()
    

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT *
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.execute(sql_query)

        # Get the return result
        result = self.cur.fetchone()

        # Check if the hash is same
        if bcrypt.checkpw(password.encode('ascii'), bytes.fromhex(result[1])):

            #Update the attempts to zero
            sql_query = """
                UPDATE Users
                SET attempts = 0, block_time = NULL
                WHERE username = '{username}'
            """

            sql_query = sql_query.format(username=username)
            self.execute(sql_query)
            self.commit()

            return True
        else:

            attempts = int(result[4]) + 1

            #Update Attempts
            #Update the attempts to zero
            sql_query = """
                UPDATE Users
                SET attempts = '{attempts}'
                WHERE username = '{username}'
            """

            sql_query = sql_query.format(username=username,attempts=attempts)
            self.execute(sql_query)
            self.commit()

            #Do a attempts_check
            self.attempts_check(username)

            return False


    #-----------------------------------------------------------------------------

    # Check if the username is exist
    def check_username(self, username):
        sql_query = """
                SELECT *
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)

        self.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        else:
            return False

    #-----------------------------------------------------------------------------

    # Check user attempts to defense Brute Force Attack
    def attempts_check(self, username):
        sql_query = """
                SELECT *
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        
        # Get the return result
        result = self.cur.fetchone()

        attempts = result[4]
        block_time = result[5]

        #Form the data that the account is block
        format_data = "%Y-%m-%d %H:%M:%S"

        #If the account is block, cooldown for 5 minutes
        if block_time != None:
            
            block_time = datetime.strptime(block_time, format_data)

            #Check if pass the 5 minutes cooldown
            different = datetime.utcnow() - block_time
            different = different.total_seconds() / 60

            if different >= 5:
                return True
            else:
                return False

        #IF the password gets wrong three times, block the account
        if attempts == 3:
            
            current_time = datetime.utcnow().strftime(format_data)
            
            #Update the block time
            sql_query = """
                UPDATE Users
                SET attempts = 0, block_time = '{block_time}'
                WHERE username = '{username}'
            """

            sql_query = sql_query.format(block_time=current_time, username=username)
            self.execute(sql_query)
            self.commit()

            return False

        return True
         