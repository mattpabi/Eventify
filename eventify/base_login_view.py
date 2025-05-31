import tkinter as tk
from tkinter import messagebox

class BaseLoginView:
    def __init__(self, root, db_manager, back_callback=None, title="Login", user_type="customer"):
        """
        Base class for login views with common functionality.

        The user_type parameter is the type of user logging in, either admin or customer, (used for verification).
        """
        self.root = root
        self.db_manager = db_manager
        self.back_callback = back_callback
        self.title = title
        self.user_type = user_type
        
        # Create main frame to hold all login elements
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and arrange all UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the common user interface elements for the login form.
        """
        
        # Application title at the top of the login form
        title_label = tk.Label(self.frame, text=self.title, font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))
        
        # Back button to return to main menu (only if callback function provided)
        if self.back_callback:
            back_button = tk.Button(
                self.frame, 
                text="Back", 
                command=self.back_callback,
                font=("Arial", 10),
                width=8
            )
            back_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create centred content frame for login form elements
        content_frame = tk.Frame(self.frame, width=400)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=100)
        
        # Username input section
        username_frame = tk.Frame(content_frame)
        username_frame.pack(fill=tk.X, pady=10)
        
        username_label = tk.Label(username_frame, text="Username:", width=12, anchor="w", font=("Arial", 12))
        username_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Password input section
        password_frame = tk.Frame(content_frame)
        password_frame.pack(fill=tk.X, pady=10)
        
        password_label = tk.Label(password_frame, text="Password:", width=12, anchor="w", font=("Arial", 12))
        password_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Button section - create the button frame, subclasses will add their specific buttons
        self.button_frame = tk.Frame(content_frame)
        self.button_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Create login button - common to both views
        login_button = tk.Button(self.button_frame, text="Login", command=self.login, 
                               width=10, height=2, font=("Arial", 11))
        login_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # Call method for subclasses to add additional buttons
        self.setup_additional_buttons()
    
    def setup_additional_buttons(self):
        """
        Override this method in subclasses to add additional buttons.
        Base implementation does nothing.
        """
        pass
    
    def login(self):
        """
        Handle the login process when user clicks the login button.
        """
        # Get text from both input fields
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Check if both fields have been filled in
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        # Validate input to ensure only alphanumeric characters
        if not username.isalnum() or not password.isalnum():
            messagebox.showerror("Error", "No special characters or spaces allowed in username or password")
            return
        
        # Attempt to verify credentials against database
        if self.verify_credentials(username, password):
            # Login successful - show welcome message
            messagebox.showinfo("Success", f"Welcome, {username}!")
            # Navigate to the appropriate dashboard
            self.show_dashboard(username)
        else:
            # Login failed - show error message
            self.show_login_error()
    
    def verify_credentials(self, username, password):
        """
        Verify user credentials.

        Returns a boolean: True if credentials are valid, False otherwise
        """
        if self.user_type == "admin":
            return self.db_manager.verify_user(username, password, user_type="admin")
        else:
            return self.db_manager.verify_user(username, password)
    
    def show_login_error(self):
        """
        Show login error message.
        """
        if self.user_type == "admin":
            messagebox.showerror("Error", "Invalid administrator credentials")
        else:
            messagebox.showerror("Error", "Invalid username or password\n\nNote: both username and password are case-sensitive")
    
    def show_dashboard(self, username):
        """
        Navigate to the appropriate dashboard (admin dashboard, or customer dashboard).
        """
        raise NotImplementedError("Subclasses must implement show_dashboard method")
    
    def clear_window(self):
        """
        Helper method to clear all widgets from the main window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()