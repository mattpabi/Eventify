import tkinter as tk
from tkinter import messagebox
from admin_dashboard_view import AdminDashboardView

class AdminLoginView:
    def __init__(self, root, db_manager, back_callback=None):
        """
        Initialise the admin login view with tkinter widgets

        The back_callback parameter is the function to call when the user wants to go back to the main menu.
        """
        self.root = root  # Store reference to main window
        self.db_manager = db_manager  # Store database manager for login verification
        self.back_callback = back_callback  # Store function to return to main menu
        
        # Create main frame to hold all login elements
        self.frame = tk.Frame(root)
        # Pack frame to fill entire window with padding
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and arrange all UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface elements for the login form."""
        
        # Application title at the top of the login form
        title_label = tk.Label(self.frame, text="Administrator Login", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))  # Add vertical padding around title
        
        # Back button to return to main menu (only if callback function provided)
        if self.back_callback:
            back_button = tk.Button(
                self.frame, 
                text="Back", 
                command=self.back_callback,  # Call the back function when clicked
                font=("Arial", 10),
                width=8
            )
            # Position button at top-left corner using relative positioning
            back_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create centred content frame for login form elements
        content_frame = tk.Frame(self.frame, width=400)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=100)  # Centre with horizontal padding
        
        # Username input section
        username_frame = tk.Frame(content_frame)  # Container for username label and entry
        username_frame.pack(fill=tk.X, pady=10)  # Fill width with vertical padding
        
        # Username label with fixed width for alignment
        username_label = tk.Label(username_frame, text="Username:", width=12, anchor="w", font=("Arial", 12))
        username_label.pack(side=tk.LEFT, padx=(0, 10))  # Position on left with right padding
        
        # Username text entry field
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Fill remaining width
        
        # Password input section
        password_frame = tk.Frame(content_frame)  # Container for password label and entry
        password_frame.pack(fill=tk.X, pady=10)  # Fill width with vertical padding
        
        # Password label with fixed width for alignment
        password_label = tk.Label(password_frame, text="Password:", width=12, anchor="w", font=("Arial", 12))
        password_label.pack(side=tk.LEFT, padx=(0, 10))  # Position on left with right padding
        
        # Password text entry field with asterisk masking
        self.password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Fill remaining width
        
        # Login button section
        button_frame = tk.Frame(content_frame)  # Container for login button
        button_frame.pack(fill=tk.X, pady=(30, 0))  # Fill width with top padding
        
        # Login button to submit credentials
        login_button = tk.Button(button_frame, text="Login", command=self.login, 
                               width=10, height=2, font=("Arial", 11))
        login_button.pack()  # Centre the button in its frame
    
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
            return  # Exit function if fields are empty
        
        # Validate input to ensure only alphanumeric characters (security measure)
        if not username.isalnum() or not password.isalnum():
            messagebox.showerror("Error", "No special characters or spaces allowed in username or password")
            return  # Exit function if invalid characters found
        
        # Attempt to verify credentials against database for admin users only
        if self.db_manager.verify_user(username, password, user_type="admin"):
            # Login successful - show welcome message
            messagebox.showinfo("Success", f"Welcome, {username}!")
            # Navigate to the admin dashboard
            self.show_admin_dashboard()
        else:
            # Login failed - show error message
            messagebox.showerror("Error", "Invalid administrator credentials")
    
    def show_admin_dashboard(self):
        """
        Show the admin dashboard after successful login.
        """
        
        # Clear all widgets from the current window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Import and create the admin dashboard (import here to avoid circular imports)
        from admin_dashboard_view import AdminDashboardView
        # Create and display the admin dashboard with logout callback
        AdminDashboardView(self.root, self.db_manager, self.back_callback)