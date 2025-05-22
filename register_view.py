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
        username_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Username label and character count on same line
        username_header_frame = tk.Frame(username_frame)
        username_header_frame.pack(fill=tk.X)
        
        username_label = tk.Label(username_header_frame, text="Username:", anchor="w", font=("Arial", 12))
        username_label.pack(side=tk.LEFT)
        
        # Username character count label
        self.username_char_count = tk.Label(username_header_frame, text="0/20 characters", font=("Arial", 9), fg="gray")
        self.username_char_count.pack(side=tk.RIGHT)
        
        # Username entry field
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Bind events to update character count and limit input
        self.username_entry.bind('<KeyRelease>', self.update_username_char_count)
        self.username_entry.bind('<KeyPress>', self.limit_username_input)
        
        # Password
        password_frame = tk.Frame(content_frame)
        password_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Password label and character count on same line
        password_header_frame = tk.Frame(password_frame)
        password_header_frame.pack(fill=tk.X)
        
        password_label = tk.Label(password_header_frame, text="Password:", anchor="w", font=("Arial", 12))
        password_label.pack(side=tk.LEFT)
        
        # Password character count label
        self.password_char_count = tk.Label(password_header_frame, text="0/30 characters", font=("Arial", 9), fg="gray")
        self.password_char_count.pack(side=tk.RIGHT)
        
        # Password entry field
        self.password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Bind events to update character count and limit input
        self.password_entry.bind('<KeyRelease>', self.update_password_char_count)
        self.password_entry.bind('<KeyPress>', self.limit_password_input)
        
        # Confirm Password
        confirm_frame = tk.Frame(content_frame)
        confirm_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Confirm password label and character count on same line
        confirm_header_frame = tk.Frame(confirm_frame)
        confirm_header_frame.pack(fill=tk.X)
        
        confirm_label = tk.Label(confirm_header_frame, text="Confirm Pass:", anchor="w", font=("Arial", 12))
        confirm_label.pack(side=tk.LEFT)
        
        # Confirm password character count label
        self.confirm_char_count = tk.Label(confirm_header_frame, text="0/30 characters", font=("Arial", 9), fg="gray")
        self.confirm_char_count.pack(side=tk.RIGHT)
        
        # Confirm password entry field
        self.confirm_entry = tk.Entry(confirm_frame, show="*", font=("Arial", 12))
        self.confirm_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Bind events to update character count and limit input
        self.confirm_entry.bind('<KeyRelease>', self.update_confirm_char_count)
        self.confirm_entry.bind('<KeyPress>', self.limit_confirm_input)
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        register_button = tk.Button(button_frame, text="Register", command=self.register,
                                  width=10, height=2, font=("Arial", 11))
        register_button.pack(side=tk.LEFT, padx=(0, 20))
        
        back_button = tk.Button(button_frame, text="Back to Login", command=self.back_to_login,
                              width=12, height=2, font=("Arial", 11))
        back_button.pack(side=tk.LEFT)
    
    def update_username_char_count(self, event=None):
        """Update the character count display for the username."""
        current_length = len(self.username_entry.get())
        self.username_char_count.config(text=f"{current_length}/20 characters")
        
        # Change color based on character count
        if current_length > 18:
            self.username_char_count.config(fg="red")
        elif current_length > 15:
            self.username_char_count.config(fg="orange")
        else:
            self.username_char_count.config(fg="gray")
    
    def limit_username_input(self, event):
        """Prevent input beyond 20 characters for username."""
        # Allow special keys (backspace, delete, arrow keys, etc.)
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
            return
        
        # Check if we're at the character limit
        current_text = self.username_entry.get()
        if len(current_text) >= 20:
            return "break"  # Prevent the keystroke
    
    def update_password_char_count(self, event=None):
        """Update the character count display for the password."""
        current_length = len(self.password_entry.get())
        self.password_char_count.config(text=f"{current_length}/30 characters")
        
        # Change color based on character count
        if current_length > 27:
            self.password_char_count.config(fg="red")
        elif current_length > 22:
            self.password_char_count.config(fg="orange")
        else:
            self.password_char_count.config(fg="gray")
    
    def limit_password_input(self, event):
        """Prevent input beyond 30 characters for password."""
        # Allow special keys (backspace, delete, arrow keys, etc.)
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
            return
        
        # Check if we're at the character limit
        current_text = self.password_entry.get()
        if len(current_text) >= 30:
            return "break"  # Prevent the keystroke
    
    def update_confirm_char_count(self, event=None):
        """Update the character count display for the confirm password."""
        current_length = len(self.confirm_entry.get())
        self.confirm_char_count.config(text=f"{current_length}/30 characters")
        
        # Change color based on character count
        if current_length > 27:
            self.confirm_char_count.config(fg="red")
        elif current_length > 22:
            self.confirm_char_count.config(fg="orange")
        else:
            self.confirm_char_count.config(fg="gray")
    
    def limit_confirm_input(self, event):
        """Prevent input beyond 30 characters for confirm password."""
        # Allow special keys (backspace, delete, arrow keys, etc.)
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
            return
        
        # Check if we're at the character limit
        current_text = self.confirm_entry.get()
        if len(current_text) >= 30:
            return "break"  # Prevent the keystroke
    
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
        
        # Validate character limits
        if len(username) > 20:
            messagebox.showerror("Error", "Username must be 20 characters or less")
            return
        
        if len(password) > 30:
            messagebox.showerror("Error", "Password must be 30 characters or less")
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