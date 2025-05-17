# admin_login_view.py - Admin Login page UI class

import tkinter as tk
from tkinter import messagebox

class AdminLoginView:
    def __init__(self, root, db_manager, back_callback=None):
        """Initialize the admin login view with tkinter widgets."""
        self.root = root
        self.db_manager = db_manager
        self.back_callback = back_callback
        
        # Create main frame
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and place widgets
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface elements."""
        # App title
        title_label = tk.Label(self.frame, text="Administrator Login", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))
        
        # Back button
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
        login_button.pack()
        
        # Default values for testing (comment out or remove in production)
        #$ self.username_entry.insert(0, "admin")
        #$ self.password_entry.insert(0, "admin2025")
    
    def login(self):
        """Handle the login process."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        # Check credentials specifically for admin users
        if self.db_manager.verify_user(username, password, user_type="admin"):
            messagebox.showinfo("Success", f"Welcome, {username}!")
            # Here you would typically navigate to the admin dashboard/event creation
            self.show_admin_dashboard()
        else:
            messagebox.showerror("Error", "Invalid administrator credentials")
    
    def show_admin_dashboard(self):
        """Show the admin dashboard."""
        # In a real application, you would replace this with actual dashboard code
        # For now, we'll just show a message indicating success
        
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create a simple dashboard frame
        dashboard_frame = tk.Frame(self.root)
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Dashboard title
        title_label = tk.Label(dashboard_frame, text="Admin Dashboard", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))
        
        # Dashboard message
        message = "Welcome to the Admin Dashboard!\n\nHere you would be able to create and manage events."
        message_label = tk.Label(dashboard_frame, text=message, font=("Arial", 14))
        message_label.pack(pady=20)
        
        # Back button
        logout_button = tk.Button(
            dashboard_frame, 
            text="Logout", 
            command=self.back_callback,
            font=("Arial", 12),
            width=10,
            height=2
        )
        logout_button.pack(pady=20)