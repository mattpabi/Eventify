import tkinter as tk
from tkinter import messagebox
from register_view import RegisterView
from user_dashboard_view import UserDashboardView

class LoginView:    
    def __init__(self, root, db_manager, back_callback=None, user_type="customer"):
        """
        Initialise the login view with tkinter widgets.
        """
        self.root = root  # Store reference to the main window
        self.db_manager = db_manager  # Store reference to database manager
        self.back_callback = back_callback  # Store the back navigation function
        self.user_type = user_type  # Store what type of user is logging in
        
        # Create main frame to hold all login interface elements
        self.frame = tk.Frame(root)  # Create a container frame
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Place frame and add padding
        
        # Create and place all the user interface widgets
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the user interface elements.
        This method creates all the visual components of the login page including:
        Title label back button, username field, password field, and action buttons
        """
        # Create the main title at the top of the login page
        title_label = tk.Label(self.frame, text="Customer Login", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))  # Place title with vertical padding
        
        # Create back button only if a back callback function was provided
        if self.back_callback:
            back_button = tk.Button(
                self.frame,  # Parent container for the button
                text="Back",  # Text displayed on the button
                command=self.back_callback,  # Function to call when button is clicked
                font=("Arial", 10),
                width=8
            )
            # Position button at top-left corner of the frame
            back_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create a centred content frame to hold the login form
        content_frame = tk.Frame(self.frame, width=400)  # Create frame with fixed width
        content_frame.pack(expand=True, fill=tk.BOTH, padx=100)  # Centre the frame with padding
        
        # Create username input section
        username_frame = tk.Frame(content_frame)  # Container for username label and entry
        username_frame.pack(fill=tk.X, pady=10)  # Place frame horizontally with padding
        
        # Create username label
        username_label = tk.Label(username_frame, text="Username:", width=12, anchor="w", font=("Arial", 12))
        username_label.pack(side=tk.LEFT, padx=(0, 10))  # Place label on left side with padding
        
        # Create username text entry field
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Fill remaining horizontal space
        
        # Create password input section
        password_frame = tk.Frame(content_frame)  # Container for password label and entry
        password_frame.pack(fill=tk.X, pady=10)  # Place frame horizontally with padding
        
        # Create password label
        password_label = tk.Label(password_frame, text="Password:", width=12, anchor="w", font=("Arial", 12))
        password_label.pack(side=tk.LEFT, padx=(0, 10))  # Place label on left side with padding
        
        # Create password text entry field (with asterisks to hide text)
        self.password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Fill remaining horizontal space
        
        # Create button section for login and register buttons
        button_frame = tk.Frame(content_frame)  # Container for action buttons
        button_frame.pack(fill=tk.X, pady=(30, 0))  # Place frame with top padding only
        
        # Create login button
        login_button = tk.Button(button_frame, text="Login", command=self.login, 
                               width=10, height=2, font=("Arial", 11))
        login_button.pack(side=tk.LEFT, padx=(0, 20))  # Place on left with right padding
        
        # Create register button for new users
        register_button = tk.Button(button_frame, text="Register a new account", command=self.show_register,
                                  width=20, height=2, font=("Arial", 11))
        register_button.pack(side=tk.LEFT)  # Place on left side next to login button
    
    def login(self):
        """
        Handle the login process.
        This method:
        1. Gets the username and password from input fields
        2. Validates the input is not empty and contains only allowed characters
        3. Checks credentials against the database
        4. Either shows error message or navigates to dashboard
        """
        # Get the text entered in the username and password fields
        username = self.username_entry.get()  # Retrieve username text
        password = self.password_entry.get()  # Retrieve password text
        
        # Check if either field is empty
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")  # Show error popup
            return  # Exit the function early
        
        # Validate input - only allow alphanumeric characters (letters and numbers)
        if not username.isalnum() or not password.isalnum():
            messagebox.showerror("Error", "No special characters or spaces allowed in username or password")
            return  # Exit the function early

        # Check if the username and password combination is valid in the database
        if self.db_manager.verify_user(username, password):
            # Login successful - navigate to user dashboard
            self.show_dashboard(username)
        else:
            # Login failed - show error message
            messagebox.showerror("Error", "Invalid username or password\n\nNote: both username and password are case-sensitive")
    
    def show_dashboard(self, username):
        """
        Navigate to the user dashboard view.
        This method clears the current login page and displays the user's dashboard.
        """
        # Clear all existing widgets from the main window
        for widget in self.root.winfo_children():
            widget.destroy()  # Remove each widget from the window
            
        # Create and display the user dashboard view
        UserDashboardView(self.root, self.db_manager, username, self.back_callback)
    
    def show_register(self):
        """
        Switch to the registration view.
        This method clears the current login page and displays the registration form.
        """
        # Clear all existing widgets from the main window
        for widget in self.root.winfo_children():
            widget.destroy()  # Remove each widget from the window
            
        # Create and display the registration view
        RegisterView(self.root, self.db_manager)