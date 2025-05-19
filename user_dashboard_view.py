# user_dashboard_view.py - User dashboard showing reserved and available events

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class UserDashboardView:
    def __init__(self, root, db_manager, username, logout_callback=None):
        """Initialize the user dashboard view.
        
        Args:
            root: The tkinter root window
            db_manager: Database manager instance
            username: Current logged in username
            logout_callback: Function to call when logging out
        """
        self.root = root
        self.db_manager = db_manager
        self.username = username
        self.logout_callback = logout_callback
        
        # Create main frame
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and place widgets
        self.setup_ui()
        
        # Load events data
        self.load_events()
    
    def setup_ui(self):
        """Set up the user interface elements."""
        # App title and welcome message
        title_frame = tk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="Eventify Dashboard", font=("Arial", 20, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Welcome message with username
        welcome_msg = f"Welcome, {self.username}!"
        welcome_label = tk.Label(title_frame, text=welcome_msg, font=("Arial", 14))
        welcome_label.pack(side=tk.RIGHT)
        
        # Logout button
        if self.logout_callback:
            logout_button = tk.Button(
                self.frame, 
                text="Logout", 
                command=self.logout_callback,
                font=("Arial", 10),
                width=8
            )
            logout_button.place(relx=0.98, rely=0.05, anchor="ne")
        
        # Main content - split into two panels
        content_frame = tk.Frame(self.frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left panel - My Reservations
        left_panel = tk.LabelFrame(content_frame, text="My Reservations", font=("Arial", 12, "bold"))
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create scrollable frame for reserved events
        self.reserved_canvas = tk.Canvas(left_panel)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.reserved_canvas.yview)
        self.reserved_scrollable_frame = ttk.Frame(self.reserved_canvas)
        
        self.reserved_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.reserved_canvas.configure(scrollregion=self.reserved_canvas.bbox("all"))
        )
        
        self.reserved_canvas.create_window((0, 0), window=self.reserved_scrollable_frame, anchor="nw")
        self.reserved_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.reserved_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel - Available Events
        right_panel = tk.LabelFrame(content_frame, text="Available Events", font=("Arial", 12, "bold"))
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Create scrollable frame for available events
        self.available_canvas = tk.Canvas(right_panel)
        scrollbar2 = ttk.Scrollbar(right_panel, orient="vertical", command=self.available_canvas.yview)
        self.available_scrollable_frame = ttk.Frame(self.available_canvas)
        
        self.available_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.available_canvas.configure(scrollregion=self.available_canvas.bbox("all"))
        )
        
        self.available_canvas.create_window((0, 0), window=self.available_scrollable_frame, anchor="nw")
        self.available_canvas.configure(yscrollcommand=scrollbar2.set)
        
        self.available_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure mouse wheel scrolling for both canvases
        self.reserved_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.available_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for the canvas that's under the mouse."""
        # Determine which canvas is under the mouse
        x, y = self.root.winfo_pointerxy()
        widget = self.root.winfo_containing(x, y)
        
        # Scroll the appropriate canvas
        if widget is not None:
            if widget == self.reserved_canvas or widget.winfo_parent() == str(self.reserved_canvas):
                self.reserved_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif widget == self.available_canvas or widget.winfo_parent() == str(self.available_canvas):
                self.available_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_events(self):
        """Load and display events from the database."""
        # Get all future events
        future_events = self.db_manager.get_future_events()
        
        # For now, we'll just display all events in the Available Events section
        # In a real implementation, we would have a reservations table and filter accordingly
        self.display_available_events(future_events)
        
        # For demonstration, we'll show a placeholder in the Reserved Events section
        self.display_reserved_events([])
    
    def display_reserved_events(self, reserved_events):
        """Display the user's reserved events.
        
        Args:
            reserved_events: List of events the user has reserved
        """
        # Clear existing widgets
        for widget in self.reserved_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Display message if no reservations
        if not reserved_events:
            no_events_label = tk.Label(
                self.reserved_scrollable_frame,
                text="You haven't made any reservations yet.",
                font=("Arial", 12),
                justify=tk.LEFT,
                pady=20,
                padx=20
            )
            no_events_label.pack(fill=tk.X)
            return
        
        # Display each reserved event
        for event in reserved_events:
            self.create_event_card(self.reserved_scrollable_frame, event, is_reserved=True)
    
    def display_available_events(self, available_events):
        """Display events available for reservation.
        
        Args:
            available_events: List of available events
        """
        # Clear existing widgets
        for widget in self.available_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Display message if no events
        if not available_events:
            no_events_label = tk.Label(
                self.available_scrollable_frame,
                text="There are no upcoming events at this time.",
                font=("Arial", 12),
                justify=tk.LEFT,
                pady=20,
                padx=20
            )
            no_events_label.pack(fill=tk.X)
            return
        
        # Display each available event
        for event in available_events:
            self.create_event_card(self.available_scrollable_frame, event, is_reserved=False)
    
    def create_event_card(self, parent_frame, event, is_reserved=False):
        """Create a card displaying event information.
        
        Args:
            parent_frame: The frame to place the card in
            event: Event data dictionary
            is_reserved: Whether this is a reserved event
        """
        # Create frame for this event
        event_frame = tk.Frame(parent_frame, relief=tk.RAISED, borderwidth=1)
        event_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Event title
        title_label = tk.Label(
            event_frame,
            text=event['name'],
            font=("Arial", 12, "bold"),
            anchor="w",
            pady=5
        )
        title_label.pack(fill=tk.X, padx=10)
        
        # Event details
        details_frame = tk.Frame(event_frame)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Format date
        try:
            date_obj = datetime.datetime.strptime(event['date'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%A, %d %B %Y")
        except ValueError:
            formatted_date = event['date']
        
        # Date and time
        date_time_label = tk.Label(
            details_frame,
            text=f"Date: {formatted_date} at {event['time']}",
            font=("Arial", 10),
            anchor="w"
        )
        date_time_label.pack(fill=tk.X)
        
        # Venue
        venue_label = tk.Label(
            details_frame,
            text=f"Venue: {event['venue']}",
            font=("Arial", 10),
            anchor="w"
        )
        venue_label.pack(fill=tk.X)
        
        # Price
        price_label = tk.Label(
            details_frame,
            text=f"Price: ${event['price']:.2f}",
            font=("Arial", 10),
            anchor="w"
        )
        price_label.pack(fill=tk.X)
        
        # Button frame
        button_frame = tk.Frame(event_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add appropriate button based on whether event is reserved
        if is_reserved:
            cancel_button = tk.Button(
                button_frame,
                text="Cancel Reservation",
                command=lambda e=event: self.cancel_reservation(e),
                width=20
            )
            cancel_button.pack(side=tk.RIGHT)
        else:
            reserve_button = tk.Button(
                button_frame,
                text="Reserve Seats",
                command=lambda e=event: self.reserve_seats(e),
                width=20
            )
            reserve_button.pack(side=tk.RIGHT)
            
        # View details button
        details_button = tk.Button(
            button_frame,
            text="View Details",
            command=lambda e=event: self.view_event_details(e),
            width=15
        )
        details_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def reserve_seats(self, event):
        """Placeholder for seat reservation functionality.
        
        Args:
            event: The event to reserve seats for
        """
        messagebox.showinfo("Not Implemented", "The reservation functionality will be implemented later.")
    
    def cancel_reservation(self, event):
        """Placeholder for cancellation functionality.
        
        Args:
            event: The event to cancel reservation for
        """
        messagebox.showinfo("Not Implemented", "The cancellation functionality will be implemented later.")
    
    def view_event_details(self, event):
        """Display detailed information about an event.
        
        Args:
            event: The event to view details for
        """
        # Create a new top-level window for the event details
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Event Details: {event['name']}")
        details_window.geometry("600x400")
        
        # Make it modal
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Create frame for content
        content_frame = tk.Frame(details_window, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Event title
        title_label = tk.Label(
            content_frame,
            text=event['name'],
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Event date and time
        try:
            date_obj = datetime.datetime.strptime(event['date'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%A, %d %B %Y")
        except ValueError:
            formatted_date = event['date']
            
        date_time_label = tk.Label(
            content_frame,
            text=f"Date and Time: {formatted_date} at {event['time']}",
            font=("Arial", 12),
            anchor="w"
        )
        date_time_label.pack(fill=tk.X, pady=5)
        
        # Venue
        venue_label = tk.Label(
            content_frame,
            text=f"Venue: {event['venue']}",
            font=("Arial", 12),
            anchor="w"
        )
        venue_label.pack(fill=tk.X, pady=5)
        
        # Capacity and Price
        capacity_price_label = tk.Label(
            content_frame,
            text=f"Capacity: {event['capacity']} seats | Price: ${event['price']:.2f}",
            font=("Arial", 12),
            anchor="w"
        )
        capacity_price_label.pack(fill=tk.X, pady=5)
        
        # Description (in a scrollable text area)
        desc_label = tk.Label(
            content_frame,
            text="Description:",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        desc_label.pack(fill=tk.X, pady=(10, 5))
        
        desc_frame = tk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=1)
        desc_frame.pack(fill=tk.BOTH, expand=True)
        
        desc_text = tk.Text(desc_frame, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
        desc_text.insert(tk.END, event['description'])
        desc_text.config(state=tk.DISABLED)  # Make read-only
        
        # Add scrollbar to description
        desc_scrollbar = ttk.Scrollbar(desc_frame, command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scrollbar.set)
        
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Close button
        close_button = tk.Button(
            content_frame,
            text="Close",
            command=details_window.destroy,
            width=10,
            font=("Arial", 10)
        )
        close_button.pack(pady=(15, 0))