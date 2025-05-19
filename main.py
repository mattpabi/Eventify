# main.py - Main entry point for the application

import tkinter as tk
from tkinter import messagebox
from login_view import LoginView
from database_manager import DatabaseManager
import os
import datetime

class App:
    def __init__(self, root):
        """Initialise the main application."""
        self.root = root
        self.root.title("Eventify")
        self.root.geometry("1366x720")
        self.root.resizable(True, True)
        
        # Attempt to initialise database three times.
        print("\nAttempting to initialise database.\nPlease open the app again if this process fails.")
        try:
            print(f"{(datetime.datetime.now()).strftime("%Y-%m-%d %H:%M")} | Attempt 1", end="")
            self.db_manager = DatabaseManager()
            self.initialise_database()
            print(": Success\n\nEventify is now up and running. A new window for the graphical user interface has opened.\nOpen the window to login and start using Eventify.")
        except:
            try:
                print(f"{(datetime.datetime.now()).strftime("%Y-%m-%d %H:%M")} | Attempt 3", end="")
                self.db_manager = DatabaseManager()
                self.initialise_database()
                print(": Success\n\nEventify is now up and running. A new window for the graphical user interface has opened.\nOpen the window to login and start using Eventify.")
            except:
                try:
                    print(f"{(datetime.datetime.now()).strftime("%Y-%m-%d %H:%M")} | Attempt 3", end="")
                    self.db_manager = DatabaseManager()
                    self.initialise_database()
                    print(": Success\n\nEventify is now up and running. A new window for the graphical user interface has opened.\nOpen the window to login and start using Eventify.")
                except Exception as e:
                    tk.messagebox.showerror("Database Error", f"Failed to initialise database: {e}")
                    root.destroy()
                    return
        
        # Start with login selection view
        self.show_login_selection()
    
    def initialise_database(self):
        """Initialise the database with tables and initial data."""
        # Set up the database schema
        self.db_manager.setup_database()
        
        # Preload admin account if it doesn't exist
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin2025")
        
        if not self.db_manager.user_exists(admin_username):
            self.db_manager.create_user(admin_username, admin_password, user_type="admin")
        
        # Create some sample events if there are no future events
        future_events = self.db_manager.get_future_events()
        if not future_events:
            self.create_sample_events()
    
    def create_sample_events(self):
        """Create sample events for testing."""
        # Calculate dates for sample events (starting tomorrow)
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        two_weeks = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        one_month = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Sample events data
        sample_events = [
            {
                "name": "The SpongeBob Musical",
                "description": "The stakes are higher than ever in this dynamic stage musical, as SpongeBob and all of Bikini Bottom face the total annihilation of their undersea world. Chaos erupts. Lives hang in the balance. And just when all hope seems lost, a most unexpected hero rises up and takes center stage. The power of optimism really can save the world!",
                "date": tomorrow,
                "time": "18:00",
                "venue": "Castle Hill High School auditorium",
                "capacity": 550,
                "price": 10.00
            },
            {
                "name": "Comedy Night",
                "description": "An evening of stand-up comedy featuring both established and up-and-coming comedians.",
                "date": two_weeks,
                "time": "20:00",
                "venue": "Castle Hill High School auditorium",
                "capacity": 550,
                "price": 5.00
            },
            {
                "name": "Tech Conference 2025",
                "description": "Explore the latest innovations in technology with industry experts and thought leaders.",
                "date": one_month,
                "time": "09:00",
                "venue": "Castle Hill High School auditorium",
                "capacity": 550,
                "price": 25.00
            }
        ]
        
        # Create each sample event
        for event in sample_events:
            self.db_manager.create_event(
                name=event["name"],
                description=event["description"],
                date=event["date"],
                time=event["time"],
                venue=event["venue"],
                capacity=event["capacity"],
                price=event["price"]
            )
    
    def show_login_selection(self):
        """Display the login selection page."""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add title
        title_label = tk.Label(main_frame, text="Eventify", font=("Arial", 22, "bold"))
        title_label.pack(pady=(10, 30))
        
        # Add admin login button at top-right
        admin_button = tk.Button(
            main_frame, 
            text="Login as Administrator", 
            command=self.show_admin_login,
            font=("Arial", 11),
            width=20,
            height=2
        )
        admin_button.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Add customer login button in the middle
        customer_button = tk.Button(
            main_frame, 
            text="Login as Customer", 
            command=self.show_login,
            font=("Arial", 14, "bold"),
            width=20,
            height=3
        )
        customer_button.place(relx=0.5, rely=0.5, anchor="center")
    
    def show_login(self):
        """Display the customer login page."""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Show login frame
        LoginView(self.root, self.db_manager, self.show_login_selection, user_type="customer")
    
    def show_admin_login(self):
        """Display the admin login page."""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Show admin login frame
        from admin_login_view import AdminLoginView
        AdminLoginView(self.root, self.db_manager, self.show_login_selection)

    def on_close(self):
        """Ask the user to confirm before closing the app."""
        response = messagebox.askyesno('Exit', 'Are you sure you want to exit?')
        if response:
            print(f"\n{(datetime.datetime.now()).strftime("%Y-%m-%d %H:%M")} | You have closed the app. We hope to see you again.\n")
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    
    # Center the window on the screen
    window_width = 1366
    window_height = 720
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    # Set the minimum and maximum window sizes
    root.minsize(1280, 720)
    root.maxsize(1920, 1080)
    
    # Set the logo for the app
    try:    
        root.iconphoto(True, tk.PhotoImage(file="images/logo.png"))
    except:
        try:
            root.iconphoto(True, tk.PhotoImage(file="/images/logo.png"))
        except:
            pass

    # Set the close window protocol to show confirmation dialog
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    
    root.mainloop()