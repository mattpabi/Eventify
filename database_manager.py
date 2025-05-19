# database_manager.py - SQLite database handling class

import sqlite3
import hashlib
import os
import datetime

class DatabaseManager:
    def __init__(self, db_name="eventify.db"):
        """Initialise the database manager with the given database name."""

        # Get the absolute path of the folder containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Join the script directory with the database filename
        self.db_name = os.path.join(script_dir, db_name)
        
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
        
        # Create events table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                venue TEXT NOT NULL,
                capacity INTEGER DEFAULT 550,
                price REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create user_reservation if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_reservation (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            seat_row TEXT NOT NULL,
            seat_number INTEGER NOT NULL,
            reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'reserved',
            UNIQUE(event_id, seat_row, seat_number)
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
    
    # Event management methods
    
    def create_event(self, name, description, date, time, venue="Castle Hill High School auditorium", capacity=550, price=0.0):
        """Create a new event in the database.
        
        Args:
            name: The name of the event
            description: The description of the event
            date: The date of the event (YYYY-MM-DD)
            time: The time of the event (HH:MM)
            venue: The venue of the event (defaults to Castle Hill High School auditorium")
            capacity: The maximum capacity of the event (fixed at 550)
            price: The ticket price for the event
            
        Returns:
            int: The ID of the new event or None if failed
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO events 
                   (name, description, date, time, venue, capacity, price) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, description, date, time, venue, capacity, price)
            )
            
            # Get the ID of the newly inserted event
            event_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return event_id
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def get_all_events(self):
        """Get all events from the database.
        
        Returns:
            list: A list of event dictionaries
        """
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row  # This enables dictionary access by column name
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM events ORDER BY date, time")
            
            # Convert to list of dictionaries
            events = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return events
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def get_future_events(self):
        """Get all future events from the database.
        
        Returns:
            list: A list of future event dictionaries
        """
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row  # This enables dictionary access by column name
            cursor = conn.cursor()
            
            # Get the current date
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute(
                "SELECT * FROM events WHERE date >= ? ORDER BY date, time",
                (current_date,)
            )
            
            # Convert to list of dictionaries
            events = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return events
        except Exception as e:
            print(f"Error getting future events: {e}")
            return []
    
    def get_event_by_id(self, event_id):
        """Get an event by its ID.
        
        Args:
            event_id: The ID of the event to retrieve
            
        Returns:
            dict: The event data or None if not found
        """
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row  # This enables dictionary access by column name
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM events WHERE id = ?",
                (event_id,)
            )
            
            event = cursor.fetchone()
            
            conn.close()
            
            if event:
                return dict(event)
            return None
        except Exception as e:
            print(f"Error getting event by ID: {e}")
            return None
    
    def update_event(self, event_id, name=None, description=None, date=None, time=None, 
                    venue="Castle Hill High School auditorium", capacity=550, price=None):
        """Update an event in the database.
        
        Args:
            event_id: The ID of the event to update
            name: The new name of the event (optional)
            description: The new description of the event (optional)
            date: The new date of the event (optional)
            time: The new time of the event (optional)
            venue: The venue of the event (fixed as Castle Hill High School auditorium")
            capacity: The capacity of the event (fixed at 550)
            price: The new price of the event (optional)
            
        Returns:
            bool: True if the event was updated successfully
        """
        try:
            # Get the current event data
            current_event = self.get_event_by_id(event_id)
            if not current_event:
                return False
            
            # Update with new values or keep current ones
            name = name if name is not None else current_event['name']
            description = description if description is not None else current_event['description']
            date = date if date is not None else current_event['date']
            time = time if time is not None else current_event['time']
            price = price if price is not None else current_event['price']
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """UPDATE events 
                   SET name = ?, description = ?, date = ?, time = ?, 
                       venue = ?, capacity = ?, price = ?
                   WHERE id = ?""",
                (name, description, date, time, venue, capacity, price, event_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating event: {e}")
            return False
    
    def delete_event(self, event_id):
        """Delete an event from the database.
        
        Args:
            event_id: The ID of the event to delete
            
        Returns:
            bool: True if the event was deleted successfully
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM events WHERE id = ?",
                (event_id,)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
        
    def get_reserved_seats(self, event_id, current_username):
        """Return the list of reserved seats for a given event_id excluding the current user.
        Sorted by seat_row and seat_number.
        Args:
            event_id: The event ID to filter reservations
            current_username: The username to exclude from the results
        Returns:
            list of tuples: Each tuple contains (seat_row, seat_number)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT seat_row, seat_number FROM user_reservation
                WHERE event_id = ? AND username != ?
                ORDER BY seat_row, seat_number
                """,
                (event_id, current_username)
            )
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting reserved seats: {e}")
            return []

    def get_user_reserved_seats(self, event_id, current_username):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT seat_row, seat_number FROM user_reservation
                WHERE event_id = ? AND username = ?
                ORDER BY seat_row, seat_number
                """,
                (event_id, current_username)
            )
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting user reserved seats: {e}")
            return []
    
    def reserve_seats(self, username, event_id, seats):
        """
        Reserve multiple seats for a user for a specific event.

        Args:
            username (str): The username reserving the seats.
            event_id (int): The event ID.
            seats (list of tuples): List of (seat_row, seat_number) tuples to reserve.

        Returns:
            dict: {
                'success': bool,
                'reserved': list of (seat_row, seat_number) reserved,
                'failed': list of (seat_row, seat_number) not reserved (e.g., already taken)
            }
        """
        reserved = []
        failed = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            for seat_row, seat_number in seats:
                try:
                    cursor.execute(
                        """
                        INSERT INTO user_reservation (username, event_id, seat_row, seat_number, status)
                        VALUES (?, ?, ?, ?, 'reserved')
                        """,
                        (username, event_id, seat_row, seat_number)
                    )
                    reserved.append((seat_row, seat_number))
                except sqlite3.IntegrityError:
                    # Seat already reserved (UNIQUE constraint failed)
                    failed.append((seat_row, seat_number))
            conn.commit()
            conn.close()
            return {'success': len(failed) == 0, 'reserved': reserved, 'failed': failed}
        except Exception as e:
            print(f"Error reserving seats: {e}")
            return {'success': False, 'reserved': reserved, 'failed': seats}
