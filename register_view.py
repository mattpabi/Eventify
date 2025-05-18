# register_view.py - Registration page UI class

import tkinter as tk
from tkinter import messagebox

class RegisterView:
    def __init__(self, root, db_manager, back_callback=None):
        """Initialise the registration view with tkinter widgets."""
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
        title_label = tk.Label(self.frame, text="Create Account", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))
        
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
        
        # Confirm Password
        confirm_frame = tk.Frame(content_frame)
        confirm_frame.pack(fill=tk.X, pady=10)
        
        confirm_label = tk.Label(confirm_frame, text="Confirm Pass:", width=12, anchor="w", font=("Arial", 12))
        confirm_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.confirm_entry = tk.Entry(confirm_frame, show="*", font=("Arial", 12))
        self.confirm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        register_button = tk.Button(button_frame, text="Register", command=self.register,
                                  width=10, height=2, font=("Arial", 11))
        register_button.pack(side=tk.LEFT, padx=(0, 20))
        
        back_button = tk.Button(button_frame, text="Back to Login", command=self.back_to_login,
                              width=12, height=2, font=("Arial", 11))
        back_button.pack(side=tk.LEFT)
    
    def register(self):
        """Handle the registration process."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        # Validate input
        if not username.isalnum() or not password.isalnum():
            messagebox.showerror("Error", "No special characters or spaces allowed in username or password")
            return

        if not username or not password or not confirm:
            messagebox.showerror("Error", "All fields are required")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Check if username already exists
        if self.db_manager.user_exists(username):
            messagebox.showerror("Error", "Username already exists")
            return
        
        # Create the new user
        if self.db_manager.create_user(username, password):
            messagebox.showinfo("Success", "Account created successfully!")
            self.back_to_login()
        else:
            messagebox.showerror("Error", "Failed to create account")
    
    def back_to_login(self):
        """Switch back to the login view."""
        # Import here to avoid circular import
        from login_view import LoginView
        
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Show login frame
        LoginView(self.root, self.db_manager, self.back_callback)