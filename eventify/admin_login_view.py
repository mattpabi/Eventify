from base_login_view import BaseLoginView

class AdminLoginView(BaseLoginView):
    def __init__(self, root, db_manager, back_callback=None):
        """
        Initialise the admin login view by calling the parent constructor with admin-specific parameters.
        """
        super().__init__(
            root=root,
            db_manager=db_manager,
            back_callback=back_callback,
            title="Administrator Login",
            user_type="admin"
        )
    
    def show_dashboard(self, username):
        """
        Show the admin dashboard after successful login.
        """
        # Clear all widgets from the current window
        self.clear_window()
            
        # Import and create the admin dashboard (import here to avoid circular imports)
        from admin_dashboard_view import AdminDashboardView
        # Create and display the admin dashboard with logout callback
        AdminDashboardView(self.root, self.db_manager, self.back_callback)