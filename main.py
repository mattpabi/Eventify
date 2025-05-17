# main.py - Main entry point for the application

# main.py - Main entry point for the application

import tkinter as tk
from login_view import LoginView
from database_manager import DatabaseManager
import os

class App:
    def __init__(self, root):
        """Initialize the main application."""
        self.root = root
        self.root.title("StageSet")
        self.root.geometry("1366x768")
        self.root.resizable(True, True)
        
        # Initialize the database
        self.db_manager = DatabaseManager()
        self.db_manager.setup_database()
        
        # Preload admin account if it doesn't exist
        if not self.db_manager.user_exists("admin"):
            self.db_manager.create_user(os.environ.get("ADMIN_USERNAME"), os.environ.get("ADMIN_PASSWORD"), user_type="admin")
        
        # Start with login selection view
        self.show_login_selection()
    
    def show_login_selection(self):
        """Display the login selection page."""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add title
        title_label = tk.Label(main_frame, text="StageSet", font=("Arial", 22, "bold"))
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

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    
    # Center the window on the screen
    window_width = 1366
    window_height = 768
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    
    # Set the logo for the app
    try:    
        root.iconphoto(True, tk.PhotoImage(file="images/logo.png"))
    except:
        try:
            root.iconphoto(True, tk.PhotoImage(file="/images/logo.png"))
        except:
            pass
    
    root.mainloop()