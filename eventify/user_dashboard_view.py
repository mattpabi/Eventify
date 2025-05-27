import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
import sys

class UserDashboardView:
    def __init__(self, root, db_manager, username, logout_callback=None):
        """
        Constructor method that sets up the dashboard when a new instance is created.

        - The username parameter is the name of the currently logged-in user
        - The logout_callback parameter is the function to call when the user wants to log out 
        """
        # Store the parameters as instance variables so other methods can access them
        self.root = root  # Store reference to the main window
        self.db_manager = db_manager  # Database connection object
        self.username = username  # Current user's name
        self.logout_callback = logout_callback  # Function to handle logout
        
        # Create the main container frame that will hold all dashboard elements
        self.frame = tk.Frame(root)
        # Pack the frame to fill the entire window with 20 pixel padding on all sides
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Call method to create all the visual elements (buttons, labels, etc.)
        self.setup_ui()
        
        # Fetch event data from database and display it on screen
        self.load_events()
        
        # Variable to keep track of stage view window if it's opened
        self.stage_view = None
    
    def setup_ui(self):
        """
        Method that creates all the visual elements of the dashboard interface.
        This includes the title, welcome message, logout button, and two main panels.
        """
        
        # === TOP SECTION: Title and Welcome Message ===
        
        # Create a horizontal frame for the top section (title on left, welcome on right)
        title_frame = tk.Frame(self.frame)
        # Pack it to fill the width with 20 pixels spacing below
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create the main app title label
        title_label = tk.Label(title_frame, text="Eventify Dashboard", font=("Arial", 20, "bold"))
        # Position it on the left side of the title frame
        title_label.pack(side=tk.LEFT)
        
        # Create personalised welcome message using the user's name
        welcome_msg = f"Welcome, {self.username}!"  # f-string to insert username into message
        welcome_label = tk.Label(title_frame, text=welcome_msg, font=("Arial", 14))
        # Position it on the right side of the title frame
        welcome_label.pack(side=tk.RIGHT)
        
        # === LOGOUT BUTTON ===
        
        # Only create logout button if a logout function was provided
        if self.logout_callback:
            logout_button = tk.Button(
                self.frame,  # Parent container
                text="Logout",  # Button text
                command=self.logout_callback,  # Function to call when clicked
                font=("Arial", 10),
                width=8
            )
            # Position button in top-right corner using relative positioning
            # relx=0.98 means 98% across the width, rely=0.05 means 5% down from top
            logout_button.place(relx=0.98, rely=0.05, anchor="ne")
        
        # === MAIN CONTENT AREA ===
        
        # Create frame to hold the two main panels (reservations and available events)
        content_frame = tk.Frame(self.frame)
        # Pack it to fill remaining space with 10 pixels spacing above
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # === LEFT PANEL: My Reservations ===
        
        # Create labelled frame for user's reserved events
        left_panel = tk.LabelFrame(content_frame, text="My Reservations", font=("Arial", 12, "bold"))
        # Pack on left side, fill vertically, with 10 pixel gap on right
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create scrollable area for reserved events (in case there are many)
        self.reserved_canvas = tk.Canvas(left_panel)  # Canvas widget allows scrolling
        # Create vertical scrollbar linked to the canvas
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.reserved_canvas.yview)
        # Create frame that goes inside the canvas to hold the actual event cards
        self.reserved_scrollable_frame = ttk.Frame(self.reserved_canvas)
        
        # Set up automatic scrollbar updating when content size changes
        self.reserved_scrollable_frame.bind(
            "<Configure>",  # Event triggered when frame size changes
            # Lambda function to update scroll region when content changes size
            lambda e: self.reserved_canvas.configure(scrollregion=self.reserved_canvas.bbox("all"))
        )
        
        # Put the scrollable frame inside the canvas at position 0,0
        self.reserved_canvas.create_window((0, 0), window=self.reserved_scrollable_frame, anchor="nw")
        # Connect canvas scrolling to the scrollbar
        self.reserved_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Position canvas and scrollbar within the left panel
        self.reserved_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Canvas takes up most space
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Scrollbar on right edge, full height
        
        # === RIGHT PANEL: Available Events ===
        
        # Create labelled frame for available events (similar structure to left panel)
        right_panel = tk.LabelFrame(content_frame, text="Available Events", font=("Arial", 12, "bold"))
        # Pack on right side with 10 pixel gap on left
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Create scrollable area for available events
        self.available_canvas = tk.Canvas(right_panel)
        # Second scrollbar for the available events panel
        scrollbar2 = ttk.Scrollbar(right_panel, orient="vertical", command=self.available_canvas.yview)
        # Frame to hold available event cards
        self.available_scrollable_frame = ttk.Frame(self.available_canvas)
        
        # Set up scrollbar updating for available events panel
        self.available_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.available_canvas.configure(scrollregion=self.available_canvas.bbox("all"))
        )
        
        # Put scrollable frame inside canvas
        self.available_canvas.create_window((0, 0), window=self.available_scrollable_frame, anchor="nw")
        self.available_canvas.configure(yscrollcommand=scrollbar2.set)
        
        # Position canvas and scrollbar
        self.available_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === MOUSE WHEEL SCROLLING SETUP ===
        
        # Enable mouse wheel scrolling for both panels
        # Bind mouse wheel events to both canvases
        self.reserved_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.available_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """
        Private method that handles mouse wheel scrolling.
        It determines which panel the mouse is over and scrolls that panel.

        The event parameter is the mouse wheel event containing scroll direction and amount.
        """
        # Get current mouse position on screen
        x, y = self.root.winfo_pointerxy()
        # Find which widget is under the mouse cursor
        widget = self.root.winfo_containing(x, y)
        
        # Only scroll if mouse is over a valid widget
        if widget is not None:
            # Check if mouse is over the reserved events panel or its children
            if widget == self.reserved_canvas or widget.winfo_parent() == str(self.reserved_canvas):
                # Scroll the reserved events canvas
                # event.delta/120 gives scroll direction: positive = up, negative = down
                # Multiply by -1 to make scrolling feel natural
                self.reserved_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # Check if mouse is over the available events panel or its children
            elif widget == self.available_canvas or widget.winfo_parent() == str(self.available_canvas):
                # Scroll the available events canvas
                self.available_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_events(self):
        """
        Method that fetches event data from the database and displays it on screen.
        It separates events into two categories: reserved and available.
        """
        # Get all events that haven't happened yet from the database
        future_events = self.db_manager.get_future_events()
        
        # Display all future events in the "Available Events" section
        self.display_available_events(future_events)
        
        # Now find which events the current user has already reserved seats for
        reserved_events = []  # List to store events user has reservations for
        event_ids_with_reservations = set()  # Set to track event IDs (in Python, sets prevent duplicates)
        
        # Loop through each future event to check for user reservations
        for event in future_events:
            # Ask database for seats this user has reserved for this specific event
            user_seats = self.db_manager.get_user_reserved_seats(event['id'], self.username)
            
            # If user has reserved any seats for this event
            if user_seats:  
                # Add this event ID to our tracking set
                event_ids_with_reservations.add(event['id'])
                # Create a copy of the event data to avoid modifying the original
                event_with_seats = event.copy() 
                # Add the reserved seats information to the copied event data
                event_with_seats['reserved_seats'] = user_seats
                # Add this event to the reserved events list
                reserved_events.append(event_with_seats)
        
        # Display all the events the user has reservations for
        self.display_reserved_events(reserved_events)
    
    def get_available_seats_count(self, event_id):
        """
        Method that calculates how many seats are still available for reservation at an event.

        The event_id parameter is the unique ID number of the event to check.
        """
        # Get the event details from the database using its ID
        event = self.db_manager.get_event_by_id(event_id)
        # If event doesn't exist, return 0 available seats
        if not event:
            return 0
            
        # Get the total number of seats at this event
        total_capacity = event['capacity']
        
        # Get all seats that have been reserved by any user for this event
        # Empty string means include reservations from all users
        all_reserved_seats = self.db_manager.get_reserved_seats(event_id, "")  
        
        # Calculate available seats: total seats minus reserved seats
        available_seats = total_capacity - len(all_reserved_seats)
        return available_seats
    
    def display_reserved_events(self, reserved_events):
        """
        Method that creates visual cards for events the user has already reserved.

        The reserved_events parameter is the list of events that the user has made reservations for.
        """
        # Remove any existing event cards from the reserved events panel
        for widget in self.reserved_scrollable_frame.winfo_children():
            widget.destroy()  # Delete the widget from memory
        
        # If user hasn't reserved any events, show a friendly message
        if not reserved_events:
            no_events_label = tk.Label(
                self.reserved_scrollable_frame,  # Parent container
                text="You haven't made any reservations yet.",  # Message text
                font=("Arial", 12),
                justify=tk.LEFT,  # Left-align text
                pady=20,  # 20 pixels padding above and below
                padx=20   # 20 pixels padding left and right
            )
            # Add the label to the panel, filling the width
            no_events_label.pack(fill=tk.X)
            return  # Exit the method early since there's nothing else to display
        
        # Create a visual card for each reserved event
        for event in reserved_events:
            # Call method to create event card, marking it as reserved
            self.create_event_card(self.reserved_scrollable_frame, event, is_reserved=True)
    
    def display_available_events(self, available_events):
        """
        Method that creates visual cards for events available for reservation.

        The available_events parameter is the list of all future events that can be booked.
        """
        # Remove any existing event cards from the available events panel
        for widget in self.available_scrollable_frame.winfo_children():
            widget.destroy()
        
        # If there are no upcoming events, show appropriate message
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
        
        # Create a visual card for each available event
        for event in available_events:
            # Calculate how many seats are still available for this event
            available_seats = self.get_available_seats_count(event['id'])
            # Create a copy of event data and add the available seats count
            event_with_seats = event.copy()
            event_with_seats['available_seats'] = available_seats
            # Create event card, marking it as not reserved
            self.create_event_card(self.available_scrollable_frame, event_with_seats, is_reserved=False)
    
    def generate_qr_code(self, event):
        """
        Method that generates a QR code for a reserved event using the integrated QR code generator.
        
        The event parameter is a dictionary containing the event information and reserved seats
        """
        try:
            # Import the QR code generator
            from make_qr import generate_reservation_qr
            
            # Create reservation information string
            seat_numbers = [str(seat) for seat in event['reserved_seats']]
            seats_str = ", ".join(seat_numbers)
            
            # Format reservation info: USERNAME -- EVENT NAME -- SEATS
            reservation_info = f"{self.username} -- {event['name']} -- SEATS {seats_str}"
            
            # Create images directory if it doesn't exist
            script_dir = os.path.dirname(os.path.abspath(__file__))
            images_dir = os.path.join(script_dir, "images", "qrcode")
            os.makedirs(images_dir, exist_ok=True)
            
            # Generate filename with event ID and username for uniqueness
            filename = f"reservation_qr_event{event['id']}_{self.username}.ppm"
            ppm_path = os.path.join(images_dir, filename)
            
            # Generate the QR code with parent window integration
            generate_reservation_qr(
                reservation_info, 
                ppm_filename=ppm_path,
                parent_window=self.root  # Pass the dashboard window as parent
            )
            
        except ImportError:
            messagebox.showerror(
                "Error", 
                "QR code generator module not found. Please ensure make_qr.py is in the same directory."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
    
    def create_event_card(self, parent_frame, event, is_reserved=False):
        """
        Method that creates a visual card displaying information about a single event.
        
        Parameters:
        - parent_frame: The container where this card will be placed
        - event: Dictionary containing all the event information
        - is_reserved: Boolean indicating if this is a reserved event or available event (default value is False)
        """
        # Create main container frame for this event card with a border
        event_frame = tk.Frame(parent_frame, relief=tk.RAISED, borderwidth=1)
        # Add the card to the parent with spacing around it
        event_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # === EVENT TITLE ===
        
        # Create large, bold title label for the event name
        title_label = tk.Label(
            event_frame,  # Parent container
            text=event['name'],  # Event name from database
            font=("Arial", 12, "bold"),
            anchor="w",  # Left-align text
            pady=5  # 5 pixels padding above and below
        )
        # Add title to card, filling the width
        title_label.pack(fill=tk.X, padx=10)
        
        # === EVENT DETAILS SECTION ===
        
        # Create container for all the event details
        details_frame = tk.Frame(event_frame)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Format the date to be more readable
        try:
            # Convert date string from database into datetime object
            date_obj = datetime.datetime.strptime(event['date'], "%Y-%m-%d")
            # Format like "Monday, 15 January 2024"
            formatted_date = date_obj.strftime("%A, %d %B %Y")
        except ValueError:
            # If date format is unexpected, use the original date string
            formatted_date = event['date']
        
        # Create label showing date and time range
        date_time_label = tk.Label(
            details_frame,
            text=f"Date: {formatted_date} from {event['time']} to {event['end_time']}",
            font=("Arial", 10),
            anchor="w"  # Left-align text
        )
        date_time_label.pack(fill=tk.X)
        
        # Create label showing the venue name
        venue_label = tk.Label(
            details_frame,
            text=f"Venue: {event['venue']}",
            font=("Arial", 10),
            anchor="w"
        )
        venue_label.pack(fill=tk.X)
        
        # Create label showing ticket price (formatted to 2 decimal places)
        price_label = tk.Label(
            details_frame,
            text=f"Price per ticket: ${event['price']:.2f}",  # :.2f ensures 2 decimal places
            font=("Arial", 10),
            anchor="w"
        )
        price_label.pack(fill=tk.X)
        
        # === AVAILABLE SEATS (for available events only) ===
        
        # Only show available seats information for events that aren't reserved
        if not is_reserved and 'available_seats' in event:
            available_seats_label = tk.Label(
                details_frame,
                text=f"Available Seats: {event['available_seats']} of {event['capacity']}",
                font=("Arial", 10, "bold"),
                anchor="w",
                # Green text if seats available, red if sold out
                fg="green" if event['available_seats'] > 0 else "red"
            )
            available_seats_label.pack(fill=tk.X)
        
        # === RESERVATION DETAILS (for reserved events only) ===
        
        # Only show reservation details for events the user has already booked
        if is_reserved and 'reserved_seats' in event:
            # Calculate number of seats user has reserved
            reserved_count = len(event['reserved_seats'])
            # Calculate total amount they need to pay
            total_payable = reserved_count * event['price']
            
            # Show how many seats the user has reserved
            reserved_seats_label = tk.Label(
                details_frame,
                text=f"Your Reserved Seats: {reserved_count}",
                font=("Arial", 10, "bold"),
                anchor="w"
            )
            reserved_seats_label.pack(fill=tk.X)
            
            # Show total amount they need to pay
            total_payable_label = tk.Label(
                details_frame,
                text=f"Total Amount Payable: ${total_payable:.2f}",
                font=("Arial", 10, "bold"),
                anchor="w",
                fg="blue"  # Blue text to highlight important financial information
            )
            total_payable_label.pack(fill=tk.X)
        
        # === BUTTON SECTION ===
        
        # Create container for action buttons
        button_frame = tk.Frame(event_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create different buttons depending on whether event is reserved or not
        if is_reserved:
            # For reserved events, add QR code generation button
            qr_button = tk.Button(
                button_frame,
                text="Generate QR Code",
                # Lambda function is an anonymous function used to call the generate_qr_code method
                command=lambda e=event: self.generate_qr_code(e),
                width=19,
                bg="lightgreen",  # Light green background to make it stand out
                font=("Arial", 9, "bold")
            )
            qr_button.pack(side=tk.RIGHT, padx=(0, 5))
            
            # For reserved events, allow user to view/modify their seat selection
            view_seats_button = tk.Button(
                button_frame,
                text="View/Modify Seats",
                # Lambda function is an anonymous function used to pass the event data when button is clicked
                command=lambda e=event: self.open_stage_view(e),
                width=18
            )
            # Position button on the right side
            view_seats_button.pack(side=tk.RIGHT, padx=(0, 5))
        else:
            # For available events, allow user to reserve seats
            reserve_button = tk.Button(
                button_frame,
                text="Reserve Seats",
                # Lambda function is an anonymous function used to pass the event data when button is clicked
                command=lambda e=event: self.open_stage_view(e),
                width=20
            )
            reserve_button.pack(side=tk.RIGHT)
            
        # Add "View Details" button for all events (both reserved and available)
        details_button = tk.Button(
            button_frame,
            text="View Details",
            # Lambda function is an anonymous function used to pass event data to the details viewer
            command=lambda e=event: self.view_event_details(e),
            width=15
        )
        # Position on right side with 10 pixels space from other button
        details_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def open_stage_view(self, event):
        """
        Method that opens the seat selection interface in the same window.
        This replaces the dashboard temporarily while user selects seats.

        The event parameter is the event data for which to open seat selection.
        """
        # Import the StageView class here to avoid circular import issues
        # (circular imports happen when two files try to import each other)
        from stage_view import StageView
        
        # Clear everything currently displayed in the main window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Define function to return back to dashboard from stage view
        def back_to_dashboard():
            # Clear the stage view widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Recreate the dashboard by calling the constructor again
            self.__init__(self.root, self.db_manager, self.username, self.logout_callback)
        
        # Create new StageView instance in the same window
        self.stage_view = StageView(
            self.root,  # Same main window
            self.db_manager,  # Database connection
            event['id'],  # ID of the event to show seats for
            self.username,  # Current user
            back_callback=back_to_dashboard  # Function to call when user wants to go back
        )
    
    def view_event_details(self, event):
        """
        Method that opens a pop-up window showing detailed information about an event.

        The event parameter expects a dictionary containing all the event information to display.
        """
        # Create new pop-up window for event details
        details_window = tk.Toplevel(self.root)  # Toplevel creates a new window
        # Set window title to include event name
        details_window.title(f"Event Details: {event['name']}")
        # Set window size (width x height in pixels)
        details_window.geometry("600x400")
        
        # Make this window modal (user must close it before using main window)
        details_window.transient(self.root)  # Makes it a child of main window
        details_window.grab_set()  # Prevents interaction with main window
        
        # Create main container frame with padding
        content_frame = tk.Frame(details_window, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # === EVENT TITLE ===
        
        # Create large title label
        title_label = tk.Label(
            content_frame,
            text=event['name'],
            font=("Arial", 16, "bold"),  # Larger font for pop-up window
            anchor="w"
        )
        title_label.pack(fill=tk.X, pady=(0, 10))  # 10 pixels spacing below
        
        # === FORMATTED DATE AND TIME ===
        
        # Format date for better readability
        try:
            date_obj = datetime.datetime.strptime(event['date'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%A, %d %B %Y")
        except ValueError:
            formatted_date = event['date']
            
        # Display date and time range
        date_time_label = tk.Label(
            content_frame,
            text=f"Date and Time: {formatted_date} from {event['time']} to {event['end_time']}",
            font=("Arial", 12),
            anchor="w"
        )
        date_time_label.pack(fill=tk.X, pady=5)  # Horizontally fill any extra space along the x-axis within parent container
        
        # === VENUE INFORMATION ===
        
        venue_label = tk.Label(
            content_frame,
            text=f"Venue: {event['venue']}",
            font=("Arial", 12),
            anchor="w"
        )
        venue_label.pack(fill=tk.X, pady=5)  # Horizontally fill any extra space along the x-axis within parent container
        
        # === CAPACITY AND PRICE ===
        
        # Combine capacity and price information on one line
        capacity_price_label = tk.Label(
            content_frame,
            text=f"Capacity: {event['capacity']} seats | Price per ticket: ${event['price']:.2f}",
            font=("Arial", 12),
            anchor="w"
        )
        capacity_price_label.pack(fill=tk.X, pady=5)  # Horizontally fill any extra space along the x-axis within parent container
        
        # === AVAILABLE SEATS (if information is present) ===
        
        # Only show if the event data includes available seats information
        if 'available_seats' in event:
            available_seats_label = tk.Label(
                content_frame,
                text=f"Available Seats: {event['available_seats']} of {event['capacity']}",
                font=("Arial", 12, "bold"),
                anchor="w",
                # Green if seats available, red if sold out
                fg="green" if event['available_seats'] > 0 else "red"
            )
            available_seats_label.pack(fill=tk.X, pady=5)  # Horizontally fill any extra space along the x-axis within parent container
        
        # === EVENT DESCRIPTION ===
        
        # Label for description section
        desc_label = tk.Label(
            content_frame,
            text="Description:",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        desc_label.pack(fill=tk.X, pady=(10, 5))  # Extra spacing above, normal below
        
        # Create frame with border for description text area
        desc_frame = tk.Frame(content_frame, relief=tk.SUNKEN, borderwidth=1)
        desc_frame.pack(fill=tk.BOTH, expand=True)  # Fill remaining space
        
        # Create scrollable text widget for long descriptions
        desc_text = tk.Text(desc_frame, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
        # Insert the event description text
        desc_text.insert(tk.END, event['description'])
        # Make text read-only so user can't edit it
        desc_text.config(state=tk.DISABLED)
        
        # Add vertical scrollbar for long descriptions
        desc_scrollbar = ttk.Scrollbar(desc_frame, command=desc_text.yview)
        # Connect text widget scrolling to scrollbar
        desc_text.configure(yscrollcommand=desc_scrollbar.set)
        
        # Position scrollbar and text widget
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Scrollbar on right edge
        desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Text takes remaining space
        
        # === ACTION BUTTONS ===
        
        # "Reserve Seats" button - closes this window and opens seat selection
        reserve_button = tk.Button(
            content_frame,
            text="Reserve Seats",
            # Lambda function is an anonymous function with list of commands to execute: [close window, open stage view]
            command=lambda e=event: [details_window.destroy(), self.open_stage_view(e)],
            width=15,
            font=("Arial", 10)
        )
        reserve_button.pack(side=tk.LEFT, pady=(15, 0))  # Position on left with top spacing
        
        # "Close" button - simply closes the pop-up window
        close_button = tk.Button(
            content_frame,
            text="Close",
            command=details_window.destroy,  # Destroy the pop-up window
            width=10,
            font=("Arial", 10)
        )
        close_button.pack(side=tk.RIGHT, pady=(15, 0))  # Position on right with top spacing