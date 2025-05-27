import tkinter as tk
from tkinter import messagebox
from login_view import LoginView
from database_manager import DatabaseManager
import os
import datetime

class App:
    def __init__(self, root):
        """
        Initialise the main application.
        This is a constructor that sets up the main window, initialises the database, and displays the initial login selection screen.
        """
        self.root = root  # Store reference to the main tkinter window object
        self.root.title("Eventify")  # Set the application window title
        self.root.geometry("1366x720")  # Set initial window size (width x height)
        self.root.resizable(True, True)  # Allow user to resize the window
        
        print("\nAttempting to initialise database.\nPlease open the app again if this process fails.")
        
        # Attempt to initialise database with multiple retry attempts for reliability
        # First attempt to initialise database
        try:
            print(f"{(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M')} | Attempt 1", end="")
            self.db_manager = DatabaseManager()  # Create database manager object
            self.initialise_database()  # Set up database tables and initial data
            print(": Success\n\nEventify is now up and running. A new window for the graphical user interface has opened.\nOpen the window to login and start using Eventify.")
        except:
            # Second attempt if first attempt fails
            try:
                print(f"{(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M')} | Attempt 2", end="")
                self.db_manager = DatabaseManager()  # Create new database manager
                self.initialise_database()  # Try to set up database again
                print(": Success\n\nEventify is now up and running. A new window for the graphical user interface has opened.\nOpen the window to login and start using Eventify.")
            except:
                # Third and final attempt
                try:
                    print(f"{(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M')} | Attempt 3", end="")
                    self.db_manager = DatabaseManager()  # Create new database manager
                    self.initialise_database()  # Final attempt to set up database
                    print(": Success\n\nEventify is now up and running. A new window for the graphical user interface has opened.\nOpen the window to login and start using Eventify.")
                except Exception as e:
                    # All attempts failed - show error and close application
                    tk.messagebox.showerror("Database Error", f"Failed to initialise database: {e}")
                    root.destroy()  # Close the application window
                    return  # Exit the constructor
        
        # Database initialisation successful - show the login selection screen
        self.show_login_selection()
    
    def initialise_database(self):
        """
        Initialise the database with tables and initial data.
        This method:
        1. Creates necessary database tables
        2. Sets up an admin account if it doesn't exist
        3. Creates sample events for testing if no future events exist
        """
        # Create all required database tables and structure
        self.db_manager.setup_database()
        
        # Set up admin account credentials from environment variables or use defaults
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")  # Get admin username from environment, if unable then use the "admin" default value
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin2025")  # Get admin password from environment, if unable then use the "admin2025" default value
        
        # Create admin account only if it doesn't already exist in database
        if not self.db_manager.user_exists(admin_username):
            self.db_manager.create_user(admin_username, admin_password, user_type="admin")
        
        # Check if there are any future events in the database
        future_events = self.db_manager.get_future_events()  # Get list of upcoming events
        if not future_events:  # If no future events exist
            self.create_sample_events()  # Create some sample events for demonstration
    
    def create_sample_events(self):
        """
        Create sample events for testing.
        This method generates three sample events with different dates in the future
        to demonstrate the application's functionality.
        """
        # Calculate future dates for sample events
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")  # Tomorrow's date
        two_weeks = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")  # Date 2 weeks from now
        one_month = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")  # Date 1 month from now
        
        # Define sample events data as a list of dictionaries
        sample_events = [
            {
                "name": "The SpongeBob Musical",  # Event title
                "description": "The stakes are higher than ever in this dynamic stage musical, as SpongeBob and all of Bikini Bottom face the total annihilation of their undersea world. Chaos erupts. Lives hang in the balance. And just when all hope seems lost, a most unexpected hero rises up and takes center stage. The power of optimism really can save the world!",
                "date": tomorrow,  # Event date (tomorrow)
                "time": "10:00",  # Start time in 24-hour format
                "end_time": "12:00",  # End time in 24-hour format
                "venue": "Castle Hill High School auditorium",  # Event location
                "capacity": 550,  # Maximum number of attendees
                "price": 10.00  # Ticket price in dollars
            },
            {
                "name": "Comedy Night",  # Event title
                "description": "An evening of stand-up comedy featuring both established and up-and-coming comedians.",
                "date": two_weeks,  # Event date (2 weeks from now)
                "time": "20:00",  # Start time (8:00 PM)
                "end_time": "21:45",  # End time (9:45 PM)
                "venue": "Castle Hill High School auditorium",  # Event location
                "capacity": 550,  # Maximum number of attendees
                "price": 5.00  # Ticket price in dollars
            },
            {
                "name": "Tech Conference 2025",  # Event title
                "description": "Explore the latest innovations in technology with industry experts and thought leaders.",
                "date": one_month,  # Event date (1 month from now)
                "time": "09:00",  # Start time (9:00 AM)
                "end_time": "17:00",  # End time (5:00 PM)
                "venue": "Castle Hill High School auditorium",  # Event location
                "capacity": 550,  # Maximum number of attendees
                "price": 25.00  # Ticket price in dollars
            }
        ]
        
        # Create each sample event in the database
        for event in sample_events:  # Loop through each event dictionary
            self.db_manager.create_event(
                name=event["name"],  # Event name
                description=event["description"],  # Event description
                date=event["date"],  # Event date
                time=event["time"],  # Start time
                end_time=event["end_time"],  # End time
                venue=event["venue"],  # Event venue
                capacity=event["capacity"],  # Maximum capacity
                price=event["price"]  # Ticket price
            )
    
    def show_login_selection(self):
        """
        Display the login selection page.
        This method creates the initial screen where users can choose between
        customer login and administrator login options.
        """
        # Clear any existing widgets (elements, e.g. buttons) from the main window
        # This clears the whole window to prepare it for the login screen
        for widget in self.root.winfo_children():
            widget.destroy()  # Remove each widget
        
        # Create main frame to hold all login selection elements
        main_frame = tk.Frame(self.root)  # Create container frame
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Place frame with padding
        
        # Create and display the application title
        title_label = tk.Label(main_frame, text="Eventify", font=("Arial", 22, "bold"))
        title_label.pack(pady=(10, 30))  # Place title with vertical padding
        
        # Create admin login button positioned at top-right corner
        admin_button = tk.Button(
            main_frame,  # Parent container
            text="Login as Administrator",  # Button text
            command=self.show_admin_login,  # Function to call when clicked
            font=("Arial", 11),
            width=20,
            height=2
        )
        admin_button.place(relx=1.0, rely=0.0, anchor="ne")  # Position at top-right corner
        
        # Create customer login button positioned in the centre of the screen
        customer_button = tk.Button(
            main_frame,  # Parent container
            text="Login as Customer",  # Button text
            command=self.show_login,  # Function to call when clicked
            font=("Arial", 14, "bold"),
            width=20,
            height=3
        )
        customer_button.place(relx=0.5, rely=0.5, anchor="center")  # Position at screen centre
    
    def show_login(self):
        """
        Display the customer login page.
        This method clears the current screen and shows the customer login form.
        """
        # Clear all existing widgets from the main window
        for widget in self.root.winfo_children():
            widget.destroy()  # Remove each widget
            
        # Create and display the customer login view
        LoginView(self.root, self.db_manager, self.show_login_selection, user_type="customer")
    
    def show_admin_login(self):
        """
        Display the admin login page.
        This method clears the current screen and shows the administrator login form.
        """
        # Clear all existing widgets from the main window
        for widget in self.root.winfo_children():
            widget.destroy()  # Remove each widget
            
        # Import admin login view (imported here to avoid circular import issues)
        from admin_login_view import AdminLoginView
        # Create and display the admin login view
        AdminLoginView(self.root, self.db_manager, self.show_login_selection)

    def on_close(self):
        """
        Ask the user to confirm before closing the app.
        This method displays a confirmation dialog when the user tries to close the application.
        """
        # Show yes/no confirmation dialog
        response = messagebox.askyesno('Exit', 'Are you sure you want to close to the application?')
        if response:  # If user clicked 'Yes'
            # Print goodbye message with timestamp
            print(f"\n{(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M')} | You have closed the app. We hope to see you again.\n")
            self.root.destroy()  # Close the application window

# Main execution block - only runs when this file is executed directly (e.g. in Windows, "Open With -> Python")
if __name__ == "__main__":
    root = tk.Tk()  # Create the main tkinter window
    app = App(root)  # Create the main application instance
    
    # Centre the window on the user's screen
    window_width = 1366
    window_height = 720

    # Calculate horizontal position to centre window
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)

    # Calculate vertical position to centre window
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    
    # Set window size and position
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    # Set the minimum and maximum window sizes to maintain proper layout
    root.minsize(1280, 720)  # Minimum window size (width, height)
    root.maxsize(1920, 1080)  # Maximum window size (width, height)
    
    # Get the absolute path of the folder containing this script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to set the application icon/logo
    try:    
        root.iconphoto(True, tk.PhotoImage(file=os.path.join(script_dir, "images/logo.png")))  # Set icon from images folder
    except:
        # Try an alternative path format if the first try fails
        try:
            root.iconphoto(True, tk.PhotoImage(file=os.path.join(script_dir, "/images/logo.png")))
        except:
            pass  # If logo loading fails, continue without icon

    # Set the window close event to show confirmation dialog
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    
    # Start the main application event loop (keeps the window open and responsive)
    root.mainloop()