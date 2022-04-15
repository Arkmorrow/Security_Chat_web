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
        self.execute("DROP TABLE IF EXISTS Friends")
        self.execute("DROP TABLE IF EXISTS Messages")
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

        # Create the Firends table
        self.execute("""CREATE TABLE Friends(
            Id INTEGER PRIMARY KEY,
            username TEXT,
            friend TEXT
        )""")

        # Create the Messages table to store encrypted messages
        self.execute("""CREATE TABLE Messages(
            Id INTEGER PRIMARY KEY,
            sender_username TEXT,
            receiver_username TEXT,
            encrypted_messagge TEXT
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
    
    def debug_friend(self):
        sql_query = """
                SELECT * 
                FROM Friends
            """
            
        self.execute(sql_query)
        self.commit()

        return self.cur.fetchall()

    def debug_message(self):
        sql_query = """
                SELECT * 
                FROM Messages
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

    #-----------------------------------------------------------------------------

    # Add a friend to a user
    def add_friend(self, username ,friend):


        # Check if the friend usernmae is exist
        if len(self.get_user(friend)) == 0:
            return False

        sql_cmd = """
                INSERT INTO Friends(username, friend)
                VALUES('{username}', '{friend}')
           """

        sql_cmd = sql_cmd.format(username=username, friend=friend)

        self.execute(sql_cmd)
        self.commit()

        return True


    #-----------------------------------------------------------------------------

    # Get a user friends list
    def get_friendlist(self, username):

        sql_query = """
                SELECT * 
                FROM Friends
                WHERE username='{username}' or friend='{username}'
            """
        
        sql_cmd = sql_query.format(username=username)
        self.execute(sql_cmd)

        return self.cur.fetchall()

    #-----------------------------------------------------------------------------

    # Check if two user is friends
    def check_friendlist(self, username, friend_username):

        sql_query = """
                SELECT *
                FROM Friends
                WHERE (username = '{username}' and friend = '{friend_username}') or (username = '{friend_username}' and friend = '{username}')
            """

        sql_cmd = sql_query.format(username=username, friend_username=friend_username)
        self.execute(sql_cmd)

        return self.cur.fetchone()

    #-----------------------------------------------------------------------------

    # Add encrypted message to the database
    def add_messages(self, sender_username, receiver_username, encrypted_messagge):

        sql_query = """
                INSERT INTO Messages(sender_username, receiver_username, encrypted_messagge)
                VALUES('{sender_username}', '{receiver_username}', '{encrypted_messagge}')
           """

        sql_cmd = sql_query.format(sender_username=sender_username, receiver_username=receiver_username, encrypted_messagge=encrypted_messagge)
        self.execute(sql_cmd)
        self.commit()

        return True


    #-----------------------------------------------------------------------------

    # Get encrypted message to the database between two user
    def get_messages(self, username, friend_username):

        sql_query = """
                SELECT *
                FROM Messages
                WHERE (sender_username = '{username}' and receiver_username = '{friend_username}') or (sender_username = '{friend_username}' and receiver_username = '{username}')
            """

        sql_cmd = sql_query.format(username=username,friend_username=friend_username)
        self.execute(sql_cmd)

        return self.cur.fetchall()
         
         