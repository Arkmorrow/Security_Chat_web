import sqlite3
import uuid
import hashlib
import bcrypt

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
            admin INTEGER DEFAULT 0
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
                SELECT password
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.execute(sql_query)

        # Get the return result
        result = self.cur.fetchone()

        # Check if the hash is same
        if bcrypt.checkpw(password.encode('ascii'), bytes.fromhex(result[0])):
            return True
        else:
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
