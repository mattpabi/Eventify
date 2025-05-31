import tkinter as tk
from base_login_view import BaseLoginView
from register_view import RegisterView
from user_dashboard_view import UserDashboardView

class LoginView(BaseLoginView):
    def __init__(self, root, db_manager, back_callback=None, user_type="customer"):
        """
        Initialize the customer login view by calling the parent constructor with customer-specific parameters.
        """
        super().__init__(
            root=root,
            db_manager=db_manager,
            back_callback=back_callback,
            title="Customer Login",
            user_type=user_type
        )
    
    def setup_additional_buttons(self):
        """
        Add the register button that's specific to customer login.
        """
        # Create register button for new users
        register_button = tk.Button(self.button_frame, text="Register a new account", command=self.show_register,
                                  width=20, height=2, font=("Arial", 11))
        register_button.pack(side=tk.LEFT)
    
    def show_dashboard(self, username):
        """
        Navigate to the user dashboard view after successful login.
        """
        # Clear all existing widgets from the main window
        self.clear_window()
            
        # Create and display the user dashboard view
        UserDashboardView(self.root, self.db_manager, username, self.back_callback)
    
    def show_register(self):
        """
        Switch to the registration view.
        """
        # Clear all existing widgets from the main window
        self.clear_window()
            
        # Create and display the registration view
        RegisterView(self.root, self.db_manager)