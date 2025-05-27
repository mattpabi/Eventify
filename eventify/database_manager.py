import sqlite3
import hashlib
import os
import datetime

class DatabaseManager:
    def __init__(self, db_name="eventify.db"):
        """
        Initialise the database manager with the given database name.
        Sets up the database file path relative to the script location.
        """
        # Get the absolute path of the folder containing this script file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Join the script directory with the database filename to create full path
        # This ensures the database is always created in the same folder as the script
        self.db_name = os.path.join(script_dir, db_name)
        
    def setup_database(self):
        """
        Create the database and all required tables if they don't already exist.
        This method sets up the entire database schema for the application.
        """
        # Establish connection to the SQLite database
        conn = self._get_connection()
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist - stores user account information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Unique user ID (auto-generated)
                username TEXT UNIQUE NOT NULL,             -- Username (must be unique)
                password_hash TEXT NOT NULL,               -- Hashed password for security
                salt TEXT NOT NULL,                        -- Random salt for password hashing
                user_type TEXT DEFAULT 'customer',         -- User role (customer or admin)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Account creation timestamp
            )
        ''')
        
        # Create events table if it doesn't exist - stores event information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Unique event ID
                name TEXT NOT NULL,                        -- Event name
                description TEXT,                          -- Event description
                date TEXT NOT NULL,                        -- Event date (YYYY-MM-DD format)
                time TEXT NOT NULL,                        -- Event start time (HH:MM format)
                end_time TEXT NOT NULL,                    -- Event end time (HH:MM format)
                venue TEXT NOT NULL,                       -- Event venue location
                capacity INTEGER DEFAULT 550,              -- Maximum attendance (fixed at 550)
                price REAL DEFAULT 0.0,                    -- Ticket price
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Event creation timestamp
            )
        ''')

        # Create user_reservation table if it doesn't exist - stores seat bookings
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_reservation (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique reservation ID
            username TEXT NOT NULL,                            -- User making the reservation
            event_id INTEGER NOT NULL,                         -- Which event is being booked
            seat_row TEXT NOT NULL,                            -- Seat row (A, B, C, etc.)
            seat_number INTEGER NOT NULL,                      -- Seat number within the row
            reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- When reservation was made
            status TEXT DEFAULT 'reserved',                    -- Reservation status
            UNIQUE(event_id, seat_row, seat_number)           -- Prevent double-booking same seat
        )
        ''')
        
        # Save all changes to the database
        conn.commit()
        # Close the database connection to free up resources
        conn.close()
    
    def _get_connection(self):
        """
        Get a connection to the SQLite database.
        This is a private method (indicated by the underscore) used internally.
        """
        # Create and return a connection to the SQLite database file
        return sqlite3.connect(self.db_name)
    
    def _hash_password(self, password, salt=None):
        """
        Hash the password with a salt for secure storage.
        This prevents storing plain text passwords and protects against rainbow table attacks.
        
        - The password parameter is the password to hash
        - The salt parameter is the salt (random data value to add to a password before it is hashed, enhancing security) to use, or None to generate a new one
            
        Returns a tuple of (hashed_password, salt) - both as hexadecimal strings
        """
        # If no salt provided, generate a new random 32-byte salt
        if salt is None:
            salt = os.urandom(32).hex()  # Generate random bytes and convert to hex string
        
        # Create secure hash using PBKDF2 algorithm with SHA-256
        # This is a slow hashing function designed to resist brute force attacks
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',                    # Hash algorithm to use
            password.encode('utf-8'),    # Convert password string to bytes
            salt.encode('utf-8'),        # Convert salt string to bytes
            100000                       # Number of iterations (makes hashing slow)
        ).hex()                          # Convert result to hexadecimal string
        
        # Return both the hash and salt (salt needed for verification later)
        return password_hash, salt
    
    def create_user(self, username, password, user_type='customer'):
        """
        Create a new user in the database with secure password storage.

        - The username parameter is the username for the new user
        - The password parameter is the password for the new user
        - The user_type parameter is the type of user ('customer' or 'admin')
            
        Returns a boolean: True if the user was created successfully, False if username already exists
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Hash the password with a new random salt for security
            password_hash, salt = self._hash_password(password)
            
            # Insert the new user record into the database
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt, user_type) VALUES (?, ?, ?, ?)",
                (username, password_hash, salt, user_type)
            )
            
            # Save changes and close connection
            conn.commit()
            conn.close()
            return True  # User created successfully
            
        except sqlite3.IntegrityError:
            # This error occurs when username already exists (UNIQUE constraint violation)
            return False
            
        except Exception as e:
            # Handle any other unexpected errors
            print(f"Error creating user: {e}")
            return False
    
    def verify_user(self, username, password, user_type=None):
        """
        Verify a user's credentials by checking username and password.
        
        - The username parameter is the username to verify
        - The password parameter is the password to verify

        Returns a boolean: True if the credentials are valid, False otherwise
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get the user's stored password hash and salt from database
            if user_type:
                # If user_type specified, check both username and user_type
                cursor.execute(
                    "SELECT password_hash, salt FROM users WHERE username = ? AND user_type = ?",
                    (username, user_type)
                )
            else:
                # If no user_type specified, just check username
                cursor.execute(
                    "SELECT password_hash, salt FROM users WHERE username = ?",
                    (username,)
                )
            
            # Get the first matching record
            result = cursor.fetchone()
            conn.close()
            
            # If no user found, credentials are invalid
            if not result:
                return False
            
            # Extract the stored hash and salt from the database result
            stored_hash, salt = result
            
            # Hash the provided password with the stored salt
            calculated_hash, _ = self._hash_password(password, salt)
            
            # Compare the calculated hash with the stored hash
            # If they match, the password is correct
            return calculated_hash == stored_hash
            
        except Exception as e:
            # Handle any database errors
            print(f"Error verifying user: {e}")
            return False
            
    def get_user_type(self, username):
        """
        Get the user type (role) for a given username.

        - The username parameter is the username to check
            
        Returns a string: The user type ('customer' or 'admin') or None if user not found
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Query the database for the user's type
            cursor.execute(
                "SELECT user_type FROM users WHERE username = ?",
                (username,)
            )
            
            # Get the first matching record
            result = cursor.fetchone()
            conn.close()
            
            # If user found, return their type; otherwise return None
            if result:
                return result[0]  # Return the first column (user_type)
            return None
            
        except Exception as e:
            # Handle any database errors
            print(f"Error getting user type: {e}")
            return None
    
    def user_exists(self, username):
        """
        Check if a username already exists in the database.
        
        - The username parameter is the username to check
            
        Returns a boolean: True if the username exists, False otherwise
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Count how many users have this username (should be 0 or 1)
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE username = ?",
                (username,)
            )
            
            # Get the count from the first column of the result
            count = cursor.fetchone()[0]
            conn.close()
            
            # If count > 0, user exists
            return count > 0
            
        except Exception as e:
            # Handle any database errors
            print(f"Error checking if user exists: {e}")
            return False
    
    # Event management methods - these handle creating, reading, updating and deleting events
    
    def create_event(self, name, description, date, time, end_time, venue="Castle Hill High School auditorium", capacity=550, price=0.0):
        """
        Create a new event in the database.
        
        Returns an int: The ID of the newly created event, or None if creation failed
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert new event record into the events table
            cursor.execute(
                """INSERT INTO events 
                (name, description, date, time, end_time, venue, capacity, price) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, description, date, time, end_time, venue, capacity, price)
            )
            
            # Get the automatically generated ID of the newly inserted event
            event_id = cursor.lastrowid
            
            # Save changes and close connection
            conn.commit()
            conn.close()
            return event_id  # Return the new event's ID
            
        except Exception as e:
            # Handle any database errors
            print(f"Error creating event: {e}")
            return None
    
    def get_all_events(self):
        """
        Get all events from the database, ordered by date and time.
        
        Returns a list of event dictionaries containing all event information
        """
        try:
            # Get database connection
            conn = self._get_connection()
            # Enable dictionary-style access to query results by column name
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all events ordered by date and time (earliest first)
            cursor.execute("SELECT * FROM events ORDER BY date, time")
            
            # Convert each row to a dictionary for easier access
            events = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return events  # Return list of event dictionaries
            
        except Exception as e:
            # Handle any database errors and return empty list
            print(f"Error getting events: {e}")
            return []
    
    def get_future_events(self):
        """
        Get all future events from the database (events on or after today).
        
        Returns a list of future event dictionaries
        """
        try:
            # Get database connection
            conn = self._get_connection()
            # Enable dictionary-style access to query results
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get the current date in YYYY-MM-DD format for comparison
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Get events that are today or in the future
            cursor.execute(
                "SELECT * FROM events WHERE date >= ? ORDER BY date, time",
                (current_date,)  # Comma needed to make this a tuple
            )
            
            # Convert each row to a dictionary
            events = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return events
            
        except Exception as e:
            # Handle any database errors
            print(f"Error getting future events: {e}")
            return []
    
    def get_event_by_id(self, event_id):
        """
        Get a specific event by its unique ID.
            
        Returns the event data dictionary, or None if not found
        """
        try:
            # Get database connection
            conn = self._get_connection()
            # Enable dictionary-style access to results
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Find the event with the specified ID
            cursor.execute(
                "SELECT * FROM events WHERE id = ?",
                (event_id,)
            )
            
            # Get the first (and only) matching event
            event = cursor.fetchone()
            
            conn.close()
            
            # If event found, convert to dictionary; otherwise return None
            if event:
                return dict(event)
            return None
            
        except Exception as e:
            # Handle any database errors
            print(f"Error getting event by ID: {e}")
            return None
    
    def update_event(self, event_id, name=None, description=None, date=None, time=None, end_time=None,
                venue="Castle Hill High School auditorium", capacity=550, price=None):
        """
        Update an existing event in the database.
        Only updates fields that are provided (not None).
            
        Returns a boolean: True if the event was updated successfully, False otherwise
        """
        try:
            # Get the current event data to fill in any missing values
            current_event = self.get_event_by_id(event_id)
            if not current_event:
                return False  # Event doesn't exist
            
            # Update with new values if provided, otherwise keep current values
            # This allows partial updates (only changing some fields)
            name = name if name is not None else current_event['name']
            description = description if description is not None else current_event['description']
            date = date if date is not None else current_event['date']
            time = time if time is not None else current_event['time']
            end_time = end_time if end_time is not None else current_event['end_time']
            price = price if price is not None else current_event['price']
            
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Update the event record with the new/existing values
            cursor.execute(
                """UPDATE events 
                SET name = ?, description = ?, date = ?, time = ?, end_time = ?,
                    venue = ?, capacity = ?, price = ?
                WHERE id = ?""",
                (name, description, date, time, end_time, venue, capacity, price, event_id)
            )
            
            # Save changes and close connection
            conn.commit()
            conn.close()
            return True  # Update successful
            
        except Exception as e:
            # Handle any database errors
            print(f"Error updating event: {e}")
            return False
    
    def delete_event(self, event_id):
        """
        Delete an event from the database permanently.
            
        Returns a boolean: True if the event was deleted successfully, False otherwise
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete the event with the specified ID
            cursor.execute(
                "DELETE FROM events WHERE id = ?",
                (event_id,)
            )
            
            # Save changes and close connection
            conn.commit()
            conn.close()
            return True  # Deletion successful
            
        except Exception as e:
            # Handle any database errors
            print(f"Error deleting event: {e}")
            return False
        
    def get_reserved_seats(self, event_id, current_username):
        """
        Get the list of reserved seats for a given event, excluding the current user's reservations.
        This is used to show which seats are unavailable when a user is making a booking.
        
        - The event_id parameter is the event ID to filter reservations for
        - The current_username parameter is the username to exclude from the results
            
        Returns a list of tuples: Each tuple contains (seat_row, seat_number) for reserved seats
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all reserved seats for this event, excluding current user's reservations
            cursor.execute(
                """
                SELECT seat_row, seat_number FROM user_reservation
                WHERE event_id = ? AND username != ?
                ORDER BY seat_row, seat_number
                """,
                (event_id, current_username)
            )
            # Get all matching records as a list of tuples
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            # Handle any database errors and return empty list
            print(f"Error getting reserved seats: {e}")
            return []

    def get_user_reserved_seats(self, event_id, current_username):
        """
        Get the list of seats reserved by the current user for a specific event.
        This is used to show the user which seats they have already booked.

        - The event_id parameter is the event ID to filter reservations for
        - The current_username parameter is the username to get reservations for
        
        Returns a list of tuples: Each tuple contains (seat_row, seat_number) for user's reservations
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all seats reserved by this specific user for this event
            cursor.execute(
                """
                SELECT seat_row, seat_number FROM user_reservation
                WHERE event_id = ? AND username = ?
                ORDER BY seat_row, seat_number
                """,
                (event_id, current_username)
            )
            # Get all matching records
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            # Handle any database errors
            print(f"Error getting user reserved seats: {e}")
            return []
    
    def reserve_seats(self, username, event_id, seats):
        """
        Reserve multiple seats for a user for a specific event.
        Enforces the 4-seat limit per user and handles conflicts when seats are already taken.

        Args:
        - The username is the username reserving the seats
        - The event_id is the event ID
        - The seats is a list of tuples): List of (seat_row, seat_number) tuples to reserve

        Returns a Python dictionary:
            {
                'success': bool - True if all seats reserved successfully,
                'reserved': list - (seat_row, seat_number) tuples that were reserved,
                'failed': list - (seat_row, seat_number) tuples that couldn't be reserved,
                'message': str - explanation of any failure
            }
        """
        # Initialise lists to track successful and failed reservations
        reserved = []
        failed = []
        message = None
        
        # Check how many seats the user already has reserved for this event
        current_count = self.get_user_reservation_count(event_id, username)
        
        # Check if adding these seats would exceed the 4-seat limit
        if current_count + len(seats) > 4:
            remaining = 4 - current_count  # Calculate how many more seats they can book
            message = f"You can only reserve up to 4 seats total. You currently have {current_count} reservation(s) and can add {remaining} more."
            return {'success': False, 'reserved': [], 'failed': seats, 'message': message}
        
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Try to reserve each seat individually
            for seat_row, seat_number in seats:
                try:
                    # Insert reservation record into database
                    cursor.execute(
                        """
                        INSERT INTO user_reservation (username, event_id, seat_row, seat_number, status)
                        VALUES (?, ?, ?, ?, 'reserved')
                        """,
                        (username, event_id, seat_row, seat_number)
                    )
                    # If successful, add to reserved list
                    reserved.append((seat_row, seat_number))
                    
                except sqlite3.IntegrityError:
                    # This error occurs when seat is already reserved (UNIQUE constraint violation)
                    failed.append((seat_row, seat_number))
                    
            # Save all successful reservations to database
            conn.commit()
            conn.close()
            
            # Return results - success is True only if no seats failed to reserve
            return {'success': len(failed) == 0, 'reserved': reserved, 'failed': failed, 'message': message}
            
        except Exception as e:
            # Handle any other database errors
            print(f"Error reserving seats: {e}")
            return {'success': False, 'reserved': reserved, 'failed': seats, 'message': str(e)}

    def get_user_reservation_count(self, event_id, username):
        """
        Get the count of seats reserved by a user for a specific event.
        This is used to enforce the 4-seat limit per user.
        
        - The event_id parameter is the event ID to check
        - The current_username parameter is the username to check reservations for
            
        Returns an int: The number of seats reserved by the user for this event
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Count the number of reservations for this user and event
            cursor.execute(
                """
                SELECT COUNT(*) FROM user_reservation
                WHERE event_id = ? AND username = ?
                """,
                (event_id, username)
            )
            # Get the count from the first column of the result
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except Exception as e:
            # Handle any database errors and return 0
            print(f"Error getting user reservation count: {e}")
            return 0
    
    def cancel_reservation(self, username, event_id, seat_row, seat_number):
        """
        Cancel a specific seat reservation for a user.
                  
        Returns a boolean: True if the reservation was canceled successfully, False otherwise
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete the specific reservation record
            cursor.execute(
                """
                DELETE FROM user_reservation
                WHERE username = ? AND event_id = ? AND seat_row = ? AND seat_number = ?
                """,
                (username, event_id, seat_row, seat_number)
            )
            
            # Check if any rows were actually deleted (rowcount > 0 means success)
            success = cursor.rowcount > 0
            
            # Save changes and close connection
            conn.commit()
            conn.close()
            return success
            
        except Exception as e:
            # Handle any database errors
            print(f"Error canceling reservation: {e}")
            return False
        
    def date_has_event(self, date, exclude_event_id=None):
        """
        Check if a specific date already has an event scheduled.
        This prevents double-booking the venue on the same date.
        
        - The date parameter is a string, containing the date to check in YYYY-MM-DD format
        - The exclude_event_id is the Event ID to exclude from the check
                
        Returns a boolean: True if the date already has an event, False if the date is available
        """
        try:
            # Get database connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check for existing events on this date
            if exclude_event_id is not None:
                # When updating an event, exclude the current event from the check
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM events
                    WHERE date = ? AND id != ?
                    """,
                    (date, exclude_event_id)
                )
            else:
                # When creating a new event, check all events on this date
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM events
                    WHERE date = ?
                    """,
                    (date,)
                )
            
            # Get the count of events on this date
            count = cursor.fetchone()[0]
            conn.close()
            
            # If count > 0, date already has an event
            return count > 0
            
        except Exception as e:
            # Handle any database errors - assume date is unavailable to be safe
            print(f"Error checking if date has event: {e}")
            return False