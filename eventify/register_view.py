import tkinter as tk
from tkinter import messagebox

class RegisterView:
    def __init__(self, root, db_manager, back_callback=None):
        """
        Initialise the registration view with tkinter widgets.
        
        The back_callback parameter is the function to call when user wants to go back.
        """
        self.root = root  # Store reference to the main window
        self.db_manager = db_manager  # Store reference to database manager
        self.back_callback = back_callback  # Store the back navigation function
        
        # Create main frame to hold all registration interface elements
        self.frame = tk.Frame(root)  # Create a container frame
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Place frame and add padding
        
        # Create and place all the user interface widgets
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the user interface elements.
        This method creates all the visual components of the registration page including:
        - Title label
        - Input fields with character counters
        - Action buttons
        """
        # Create the main title at the top of the registration page
        title_label = tk.Label(self.frame, text="Create Account", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))  # Place title with vertical padding
        
        # Create a centred content frame to hold the registration form
        content_frame = tk.Frame(self.frame, width=400)  # Create frame with fixed width
        content_frame.pack(expand=True, fill=tk.BOTH, padx=100)  # Centre the frame with padding
        
        # Create username input section with character counter
        username_frame = tk.Frame(content_frame)  # Container for username components
        username_frame.pack(fill=tk.X, pady=(5, 10))  # Place frame horizontally with padding
        
        # Create header frame to hold username label and character counter side by side
        username_header_frame = tk.Frame(username_frame)  # Container for label and counter
        username_header_frame.pack(fill=tk.X)  # Fill horizontal space
        
        # Create username label
        username_label = tk.Label(username_header_frame, text="Username:", anchor="w", font=("Arial", 12))
        username_label.pack(side=tk.LEFT)  # Place label on left side
        
        # Create username character count display (shows current/maximum characters)
        self.username_char_count = tk.Label(username_header_frame, text="0/20 characters", font=("Arial", 9), fg="gray")
        self.username_char_count.pack(side=tk.RIGHT)  # Place counter on right side
        
        # Create username text entry field
        self.username_entry = tk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(fill=tk.X, pady=(5, 0))  # Fill horizontal space with top padding
        
        # Bind keyboard events to update character count and enforce limits
        self.username_entry.bind('<KeyRelease>', self.update_username_char_count)  # Update count after key release
        self.username_entry.bind('<KeyPress>', self.limit_username_input)  # Check limits before key press
        
        # Create password input section with character counter
        password_frame = tk.Frame(content_frame)  # Container for password components
        password_frame.pack(fill=tk.X, pady=(5, 10))  # Place frame horizontally with padding
        
        # Create header frame to hold password label and character counter side by side
        password_header_frame = tk.Frame(password_frame)  # Container for label and counter
        password_header_frame.pack(fill=tk.X)  # Fill horizontal space
        
        # Create password label
        password_label = tk.Label(password_header_frame, text="Password:", anchor="w", font=("Arial", 12))
        password_label.pack(side=tk.LEFT)  # Place label on left side
        
        # Create password character count display
        self.password_char_count = tk.Label(password_header_frame, text="0/30 characters", font=("Arial", 9), fg="gray")
        self.password_char_count.pack(side=tk.RIGHT)  # Place counter on right side
        
        # Create password text entry field (with asterisks to hide text)
        self.password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(fill=tk.X, pady=(5, 0))  # Fill horizontal space with top padding
        
        # Bind keyboard events to update character count and enforce limits
        self.password_entry.bind('<KeyRelease>', self.update_password_char_count)  # Update count after key release
        self.password_entry.bind('<KeyPress>', self.limit_password_input)  # Check limits before key press
        
        # Create confirm password input section with character counter
        confirm_frame = tk.Frame(content_frame)  # Container for confirm password components
        confirm_frame.pack(fill=tk.X, pady=(5, 10))  # Place frame horizontally with padding
        
        # Create header frame to hold confirm password label and character counter side by side
        confirm_header_frame = tk.Frame(confirm_frame)  # Container for label and counter
        confirm_header_frame.pack(fill=tk.X)  # Fill horizontal space
        
        # Create confirm password label
        confirm_label = tk.Label(confirm_header_frame, text="Confirm Pass:", anchor="w", font=("Arial", 12))
        confirm_label.pack(side=tk.LEFT)  # Place label on left side
        
        # Create confirm password character count display
        self.confirm_char_count = tk.Label(confirm_header_frame, text="0/30 characters", font=("Arial", 9), fg="gray")
        self.confirm_char_count.pack(side=tk.RIGHT)  # Place counter on right side
        
        # Create confirm password text entry field (with asterisks to hide text)
        self.confirm_entry = tk.Entry(confirm_frame, show="*", font=("Arial", 12))
        self.confirm_entry.pack(fill=tk.X, pady=(5, 0))  # Fill horizontal space with top padding
        
        # Bind keyboard events to update character count and enforce limits
        self.confirm_entry.bind('<KeyRelease>', self.update_confirm_char_count)  # Update count after key release
        self.confirm_entry.bind('<KeyPress>', self.limit_confirm_input)  # Check limits before key press
        
        # Create button section for register and back buttons
        button_frame = tk.Frame(content_frame)  # Container for action buttons
        button_frame.pack(fill=tk.X, pady=(30, 0))  # Place frame with top padding only
        
        # Create register button to submit the registration form
        register_button = tk.Button(button_frame, text="Register", command=self.register,
                                  width=10, height=2, font=("Arial", 11))
        register_button.pack(side=tk.LEFT, padx=(0, 20))  # Place on left with right padding
        
        # Create back button to return to login page
        back_button = tk.Button(button_frame, text="Back to Login", command=self.back_to_login,
                              width=12, height=2, font=("Arial", 11))
        back_button.pack(side=tk.LEFT)  # Place on left side next to register button
    
    def update_username_char_count(self, event=None):
        """
        Update the character count display for the username.
        This method changes the colour of the counter based on how close the user is to the limit.

        The event parameter is the keyboard event of the user containing information about the key pressed.
        """
        # Get the current length of text in the username field
        current_length = len(self.username_entry.get())
        # Update the character counter display
        self.username_char_count.config(text=f"{current_length}/20 characters")
        
        # Change colour based on character count to provide visual feedback
        if current_length > 18:  # Very close to limit (red warning)
            self.username_char_count.config(fg="red")
        elif current_length > 15:  # Getting close to limit (orange warning)
            self.username_char_count.config(fg="orange")
        else:  # Well within limit (normal grey)
            self.username_char_count.config(fg="gray")
    
    def limit_username_input(self, event):
        """
        Prevent input beyond 20 characters for username.
        This method blocks additional keystrokes when the character limit is reached, but still allows special keys like backspace and delete.
        
        The event parameter is the keyboard event of the user containing information about the key pressed.
        """
        # Allow special navigation and editing keys regardless of character count
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
            return  # Allow these keys to work normally
        
        # Get current text in the username field
        current_text = self.username_entry.get()
        # Check if user has reached the maximum character limit
        if len(current_text) >= 20:
            return "break"  # Block the keystroke to prevent further input
    
    def update_password_char_count(self, event=None):
        """
        Update the character count display for the password.
        This method changes the colour of the counter based on how close the user is to the limit.
        
        The event parameter is the keyboard event of the user containing information about the key pressed.
        """
        # Get the current length of text in the password field
        current_length = len(self.password_entry.get())
        # Update the character counter display
        self.password_char_count.config(text=f"{current_length}/30 characters")
        
        # Change colour based on character count to provide visual feedback
        if current_length > 27:  # Very close to limit (red warning)
            self.password_char_count.config(fg="red")
        elif current_length > 22:  # Getting close to limit (orange warning)
            self.password_char_count.config(fg="orange")
        else:  # Well within limit (normal grey)
            self.password_char_count.config(fg="gray")
    
    def limit_password_input(self, event):
        """
        Prevent input beyond 30 characters for password.
        This method blocks additional keystrokes when the character limit is reached, but still allows special keys like backspace and delete.
        
        The event parameter is the keyboard event of the user containing information about the key pressed.
        """
        # Allow special navigation and editing keys regardless of character count
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
            return  # Allow these keys to work normally
        
        # Get current text in the password field
        current_text = self.password_entry.get()
        # Check if user has reached the maximum character limit
        if len(current_text) >= 30:
            return "break"  # Block the keystroke to prevent further input
    
    def update_confirm_char_count(self, event=None):
        """
        Update the character count display for the confirm password.
        This method changes the colour of the counter based on how close the user is to the limit.
        
        The event parameter is the keyboard event of the user containing information about the key pressed.
        """
        # Get the current length of text in the confirm password field
        current_length = len(self.confirm_entry.get())
        # Update the character counter display
        self.confirm_char_count.config(text=f"{current_length}/30 characters")
        
        # Change colour based on character count to provide visual feedback
        if current_length > 27:  # Very close to limit (red warning)
            self.confirm_char_count.config(fg="red")
        elif current_length > 22:  # Getting close to limit (orange warning)
            self.confirm_char_count.config(fg="orange")
        else:  # Well within limit (normal grey)
            self.confirm_char_count.config(fg="gray")
    
    def limit_confirm_input(self, event):
        """
        Prevent input beyond 30 characters for confirm password.
        This method blocks additional keystrokes when the character limit is reached, but still allows special keys like backspace and delete.

        The event parameter is the keyboard event of the user containing information about the key pressed.
        """
        # Allow special navigation and editing keys regardless of character count
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
            return  # Allow these keys to work normally
        
        # Get current text in the confirm password field
        current_text = self.confirm_entry.get()
        # Check if user has reached the maximum character limit
        if len(current_text) >= 30:
            return "break"  # Block the keystroke to prevent further input
    
    def register(self):
        """
        Handle the registration process.
        This method performs comprehensive validation of user input and creates a new account if all checks pass.
        
        Validation includes:
        - Checking all fields are filled
        - Ensuring only alphanumeric characters are used
        - Verifying minimum and maximum character limits
        - Confirming passwords match
        - Ensuring password contains both letters and numbers
        - Checking username doesn't already exist
        """
        # Get the text entered in all input fields
        username = self.username_entry.get()  # Retrieve username text
        password = self.password_entry.get()  # Retrieve password text
        confirm = self.confirm_entry.get()  # Retrieve confirm password text
        
        # Validate input format - only allow alphanumeric characters (letters and numbers)
        if not username.isalnum() or not password.isalnum():
            messagebox.showerror("Error", "No special characters or spaces allowed in username or password")
            return  # Exit function early if validation fails

        # Check that all required fields have been filled in
        if not username or not password or not confirm:
            messagebox.showerror("Error", "All fields are required")
            return  # Exit function early if any field is empty
        
        # Validate minimum character requirements for security
        if len(username) < 4:
            messagebox.showerror("Error", "Username must be at least 4 characters long")
            return  # Username too short

        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return  # Password too short for security

        # Validate maximum character limits (should be prevented by input limiting, but double-check)
        if len(username) > 20:
            messagebox.showerror("Error", "Username must be 20 characters or less")
            return  # Username too long
        
        if len(password) > 30:
            messagebox.showerror("Error", "Password must be 30 characters or less")
            return  # Password too long
        
        # Check that password contains both letters and numbers
        has_letter = any(char.isalpha() for char in password)
        has_number = any(char.isdigit() for char in password)
        if not (has_letter and has_number):
            messagebox.showerror("Error", "Password must contain both letters and numbers")
            return  # Password doesn't meet complexity requirements
        
        # Check that password and confirmation password match exactly
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return  # Passwords don't match
        
        # Check if the username is already taken in the database
        if self.db_manager.user_exists(username):
            messagebox.showerror("Error", "Username already exists")
            return  # Username already exists
        
        # All validation passed - attempt to create the new user account
        if self.db_manager.create_user(username, password):
            # Account creation successful
            messagebox.showinfo("Success", "Account created successfully!")
            self.back_to_login()  # Navigate back to login page
        else:
            # Account creation failed (database error)
            messagebox.showerror("Error", "Failed to create account")
    
    def back_to_login(self):
        """
        Switch back to the login view.
        This method clears the current registration page and displays the login form.
        """
        # Import LoginView class here to avoid circular import issues
        from login_view import LoginView
        
        # Clear all existing widgets from the main window
        for widget in self.root.winfo_children():
            widget.destroy()  # Remove each widget from the window
            
        # Create and display the login view
        LoginView(self.root, self.db_manager, self.back_callback)