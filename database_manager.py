# database_manager.py - SQLite database handling class

import sqlite3
import hashlib
import os

class DatabaseManager:
    def __init__(self, db_name="user_auth.db"):
        """Initialize the database manager with the given database name."""
        self.db_name = db_name
        
    def setup_database(self):
        """Create the database and tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                user_type TEXT DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)
    
    def _hash_password(self, password, salt=None):
        """Hash the password with a salt for secure storage.
        
        Args:
            password: The password to hash
            salt: A salt to use, or None to generate a new one
            
        Returns:
            tuple: (hashed_password, salt)
        """
        if salt is None:
            salt = os.urandom(32).hex()  # Generate a random salt
        
        # Create hash
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Number of iterations
        ).hex()
        
        return password_hash, salt
    
    def create_user(self, username, password, user_type='customer'):
        """Create a new user in the database.
        
        Args:
            username: The username for the new user
            password: The password for the new user
            user_type: The type of user (customer or admin)
            
        Returns:
            bool: True if the user was created successfully
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Hash the password with a new salt
            password_hash, salt = self._hash_password(password)
            
            # Insert the new user
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt, user_type) VALUES (?, ?, ?, ?)",
                (username, password_hash, salt, user_type)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def verify_user(self, username, password, user_type=None):
        """Verify a user's credentials.
        
        Args:
            username: The username to verify
            password: The password to verify
            user_type: If specified, only verify users of this type
            
        Returns:
            bool: True if the credentials are valid
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get the user's stored password hash and salt
            if user_type:
                cursor.execute(
                    "SELECT password_hash, salt FROM users WHERE username = ? AND user_type = ?",
                    (username, user_type)
                )
            else:
                cursor.execute(
                    "SELECT password_hash, salt FROM users WHERE username = ?",
                    (username,)
                )
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            stored_hash, salt = result
            
            # Hash the provided password with the stored salt
            calculated_hash, _ = self._hash_password(password, salt)
            
            # Compare the hashes
            return calculated_hash == stored_hash
        except Exception as e:
            print(f"Error verifying user: {e}")
            return False
            
    def get_user_type(self, username):
        """Get the user type for a given username.
        
        Args:
            username: The username to check
            
        Returns:
            str: The user type or None if user not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT user_type FROM users WHERE username = ?",
                (username,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error getting user type: {e}")
            return None
    
    def user_exists(self, username):
        """Check if a username already exists.
        
        Args:
            username: The username to check
            
        Returns:
            bool: True if the username exists
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE username = ?",
                (username,)
            )
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
        except Exception as e:
            print(f"Error checking if user exists: {e}")
            return False