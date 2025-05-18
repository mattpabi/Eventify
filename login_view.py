# login_view.py - Login page UI class

import tkinter as tk
from tkinter import messagebox
from register_view import RegisterView
from user_dashboard_view import UserDashboardView

class LoginView:
    def __init__(self, root, db_manager, back_callback=None, user_type="customer"):
        """Initialise the login view with tkinter widgets."""
        self.root = root
        self.db_manager = db_manager
        self.back_callback = back_callback
        self.user_type = user_type
        
        # Create main frame
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and place widgets
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface elements."""
        # App title
        title_label = tk.Label(self.frame, text="Customer Login", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))
        
        # Back button if back callback exists
        if self.back_callback:
            back_button = tk.Button(
                self.frame, 
                text="Back", 
                command=self.back_callback,
                font=("Arial", 10),
                width=8
            )
            back_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create centered content frame
        content_frame = tk.Frame(self.frame, width=400)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=100)
        
        # Username
        username_frame = tk.Frame(content_frame)
        username_frame.pack(fill=tk.X, pady=10)
        
        username_label = tk.Label(username_frame, text="Username:", width=12, anchor="w", font=("Arial", 12))
        username_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Password
        password_frame = tk.Frame(content_frame)
        password_frame.pack(fill=tk.X, pady=10)
        
        password_label = tk.Label(password_frame, text="Password:", width=12, anchor="w", font=("Arial", 12))
        password_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Login button
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        login_button = tk.Button(button_frame, text="Login", command=self.login, 
                               width=10, height=2, font=("Arial", 11))
        login_button.pack(side=tk.LEFT, padx=(0, 20))
        
        register_button = tk.Button(button_frame, text="Register a new account", command=self.show_register,
                                  width=20, height=2, font=("Arial", 11))
        register_button.pack(side=tk.LEFT)
    
    def login(self):
        """Handle the login process."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        # Validate input
        if not username.isalnum() or not password.isalnum():
            messagebox.showerror("Error", "No special characters or spaces allowed in username or password")
            return

        # Check credentials
        if self.db_manager.verify_user(username, password):
            # Navigate to user dashboard view
            self.show_dashboard(username)
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def show_dashboard(self, username):
        """Navigate to the user dashboard view."""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Show user dashboard
        UserDashboardView(self.root, self.db_manager, username, self.back_callback)
    
    def show_register(self):
        """Switch to the registration view."""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Show registration frame
        RegisterView(self.root, self.db_manager)