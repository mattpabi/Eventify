import tkinter as tk
from tkinter import messagebox, ttk
from edit_event_view import EditEventView
from create_event_view import CreateEventView
from admin_stage_view import AdminStageView

class AdminDashboardView:   
    def __init__(self, root, db_manager, back_callback=None):
        """
        Initialise the admin dashboard view with tkinter widgets
        
        The back_callback is a function to call when user wants to go back (logout)
        """
        self.root = root  # Store reference to main window
        self.db_manager = db_manager  # Store database manager for accessing data
        self.back_callback = back_callback  # Store logout function
        
        # Create main frame to hold all dashboard elements
        self.dashboard_frame = tk.Frame(self.root)
        # Pack the frame to fill entire window with padding
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Set up the dashboard UI elements
        self.setup_ui()
        
    def setup_ui(self):
        """
        Set up the dashboard interface with event list and action buttons.
        """
        
        # Dashboard title at the top of the interface
        title_label = tk.Label(self.dashboard_frame, text="Admin Dashboard - Upcoming Events", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))  # Add vertical padding around the title
        
        # Logout button positioned at top left corner
        logout_button = tk.Button(
            self.dashboard_frame, 
            text="Logout", 
            command=self.back_callback,  # Call the logout function when clicked
            font=("Arial", 11),
            width=10,
            height=2
        )
        # Position button at top-left using relative positioning
        logout_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create Event button positioned at top right corner
        create_event_button = tk.Button(
            self.dashboard_frame, 
            text="Create New Event", 
            command=self.show_create_event,  # Call function to show event creation form
            font=("Arial", 11),
            width=15,
            height=2
        )
        # Position button at top-right using relative positioning
        create_event_button.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Create a frame to contain the event list table
        list_frame = tk.Frame(self.dashboard_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))
        
        # Create Treeview widget (table) for displaying events with multiple columns
        columns = ("id", "name", "date", "time", "end_time", "venue", "capacity", "price")
        self.event_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define column headings for the event table
        self.event_tree.heading("id", text="ID")  # Event ID column
        self.event_tree.heading("name", text="Event Name")  # Event name column
        self.event_tree.heading("date", text="Date")  # Event date column
        self.event_tree.heading("time", text="Start Time")  # Start time column
        self.event_tree.heading("end_time", text="End Time")  # End time column
        self.event_tree.heading("venue", text="Venue")  # Venue location column
        self.event_tree.heading("capacity", text="Reserved / Capacity")  # Booking status column
        self.event_tree.heading("price", text="Price ($)")  # Ticket price column
        
        # Set column widths to fit content properly
        self.event_tree.column("id", width=50, anchor="center")  # Small width for ID
        self.event_tree.column("name", width=200)  # Wider for event names
        self.event_tree.column("date", width=100, anchor="center")  # Centre-aligned date
        self.event_tree.column("time", width=90, anchor="center")  # Centre-aligned time
        self.event_tree.column("end_time", width=90, anchor="center")  # Centre-aligned end time
        self.event_tree.column("venue", width=180)  # Medium width for venue names
        self.event_tree.column("capacity", width=120, anchor="center")  # Centre-aligned capacity info
        self.event_tree.column("price", width=100, anchor="center")  # Centre-aligned price
        
        # Add a vertical scrollbar for the event table
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.event_tree.yview)
        # Connect scrollbar to the treeview's vertical scrolling
        self.event_tree.configure(yscroll=scrollbar.set)
        # Position scrollbar on the right side
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Position treeview on the left, expanding to fill available space
        self.event_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Load events from database into the table
        self.populate_event_list()
        
        # Create frame for event details and action buttons below the table
        details_frame = tk.Frame(self.dashboard_frame)
        details_frame.pack(fill=tk.X, expand=False, padx=20, pady=10)
        
        # Create frame to hold all control buttons in a row
        button_frame = tk.Frame(details_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Edit button - allows editing selected event
        edit_button = tk.Button(
            button_frame, 
            text="Edit Selected Event", 
            command=self.edit_selected_event,  # Function to edit selected event
            font=("Arial", 11),
            width=20,
            height=2
        )
        edit_button.pack(side=tk.LEFT, padx=(0, 10))  # Position on left with right padding
        
        # Delete button - allows deleting selected event
        delete_button = tk.Button(
            button_frame, 
            text="Delete Selected Event", 
            command=self.delete_selected_event,  # Function to delete selected event
            font=("Arial", 11),
            width=20,
            height=2
        )
        delete_button.pack(side=tk.LEFT, padx=(0, 10))  # Position next to edit button
        
        # View details button - shows detailed event information
        view_button = tk.Button(
            button_frame, 
            text="View Event Details", 
            command=self.view_event_details,  # Function to show event details
            font=("Arial", 11),
            width=20,
            height=2
        )
        view_button.pack(side=tk.LEFT, padx=(0, 10))  # Position next to delete button
        
        # View seating layout button - shows interactive seat map
        view_stage_button = tk.Button(
            button_frame, 
            text="View Seating Layout", 
            command=self.view_stage_layout,  # Function to show seating layout
            font=("Arial", 11),
            width=20,
            height=2
        )
        view_stage_button.pack(side=tk.LEFT)  # Position at the end of button row
        
        # Bind double-click event to automatically view seating layout
        self.event_tree.bind("<Double-1>", lambda event: self.view_stage_layout())
    
    def get_reservation_count(self, event_id):
        """
        Get the number of reserved seats for a specific event
        
        The event_id parameter ist he unique identifier for the event.
        """
        try:
            # Get database connection
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()  # Create cursor for executing SQL queries
            
            # SQL query to count all reservations for this event
            cursor.execute(
                """
                SELECT COUNT(*) FROM user_reservation
                WHERE event_id = ?
                """,
                (event_id,)  # Use parameterised query to prevent SQL injection
            )
            count = cursor.fetchone()[0]  # Get the first result (count value)
            conn.close()  # Close database connection to free resources
            return count
        except Exception as e:
            print(f"Error getting reservation count: {e}")  # Log any database errors
            return 0  # Return 0 if there's an error
    
    def populate_event_list(self):
        """
        Populate the event list with upcoming events from the database.
        """
        
        # Clear any existing items in the table
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
            
        # Get future events from the database (events that haven't happened yet)
        future_events = self.db_manager.get_future_events()
        
        # Check if no events were found
        if not future_events:
            # If there are no events, Add a placeholder row to show there are no events
            self.event_tree.insert("", tk.END, values=("N/A", "No upcoming events", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"))
            return  # Exit the function early
            
        # Loop through each event and add it to the table
        for event in future_events:
            # Get the number of reserved seats for this event
            reserved_count = self.get_reservation_count(event['id'])
            
            # Format price to show 2 decimal places (e.g., $25.00)
            price_formatted = f"${event['price']:.2f}"
            
            # Format capacity to show "reserved / total" (e.g., "15 / 100")
            capacity_formatted = f"{reserved_count} / {event['capacity']}"
            
            # Insert event data as a new row in the table
            self.event_tree.insert("", tk.END, values=(
                event['id'],  # Event ID
                event['name'],  # Event name
                event['date'],  # Event date
                event['time'],  # Start time
                event['end_time'],  # End time
                event['venue'],  # Venue location
                capacity_formatted,  # Reservation status
                price_formatted  # Formatted price
            ))
    
    def get_selected_event_id(self):
        """
        Get the ID of the currently selected event in the table
        """
        # Get list of currently selected items in the table
        selected_items = self.event_tree.selection()
        
        # Check if no items are selected
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an event first")
            return None
            
        # Get the first selected item (we only allow single selection)
        item = selected_items[0]
        
        # Get the event ID from the first column of the selected row
        event_id = self.event_tree.item(item, "values")[0]
        
        # Check if it's the placeholder "N/A" (no events available)
        if event_id == "N/A":
            messagebox.showinfo("Info", "No events available to select")
            return None
            
        return event_id  # Return the actual event ID
    
    def show_create_event(self):
        """
        Show the event creation form.
        """
        
        # Clear all widgets from the current window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create and show the event creation form
        CreateEventView(self.root, self.db_manager, self.refresh_dashboard)
    
    def refresh_dashboard(self):
        """
        Refresh the dashboard view after making changes.
        """
        
        # Clear all widgets from the current window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Recreate the dashboard with updated data
        AdminDashboardView(self.root, self.db_manager, self.back_callback)
    
    def edit_selected_event(self):
        """
        Edit the currently selected event.
        """
        
        # Get the ID of the selected event
        event_id = self.get_selected_event_id()
        
        # Only proceed if an event is selected
        if event_id:
            # Clear all widgets from the current window
            for widget in self.root.winfo_children():
                widget.destroy()
                
            # Show the edit event form with the selected event's data
            EditEventView(self.root, self.db_manager, event_id, self.refresh_dashboard)
    
    def delete_selected_event(self):
        """
        Delete the selected event after asking for confirmation.
        """
        
        # Get the ID of the selected event
        event_id = self.get_selected_event_id()
        
        # Only proceed if an event is selected
        if event_id:
            # Ask user to confirm the deletion (yes/no dialogue)
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete event ID {event_id}?"):
                # Attempt to delete the event from the database
                if self.db_manager.delete_event(event_id):
                    messagebox.showinfo("Success", "Event deleted successfully")
                    # Refresh the event list to show updated data
                    self.populate_event_list()
                else:
                    # Show error message if deletion failed
                    messagebox.showerror("Error", "Failed to delete event")
    
    def view_event_details(self):
        """
        View detailed information about the selected event in a popup window.
        """
        
        # Get the ID of the selected event
        event_id = self.get_selected_event_id()
        
        # Only proceed if an event is selected
        if event_id:
            # Get complete event details from the database
            event = self.db_manager.get_event_by_id(event_id)
            
            # Check if event data was successfully retrieved
            if event:
                # Build formatted details string for display
                details = f"Event Details:\n\n"
                details += f"ID: {event['id']}\n"
                details += f"Name: {event['name']}\n"
                details += f"Date: {event['date']}\n"
                details += f"Start Time: {event['time']}\n"
                details += f"End Time: {event['end_time']}\n"
                details += f"Venue: {event['venue']}\n"
                details += f"Capacity: {event['capacity']}\n"
                details += f"Price: ${event['price']:.2f}\n\n"  # Format price to 2 decimal places
                details += f"Description:\n{event['description']}"
                
                # Display the details in a popup message box
                messagebox.showinfo("Event Details", details)
    
    def view_stage_layout(self):
        """
        View the interactive seating layout for the selected event.
        """
        
        # Get the ID of the selected event
        event_id = self.get_selected_event_id()
        
        # Only proceed if an event is selected
        if event_id:
            # Clear all widgets from the current window
            for widget in self.root.winfo_children():
                widget.destroy()
                
            # Show the interactive seating layout view
            AdminStageView(self.root, self.db_manager, event_id, self.refresh_dashboard)