# admin_dashboard.py - Admin Dashboard UI class

import tkinter as tk
from tkinter import messagebox, ttk
from edit_event_view import EditEventView
from create_event_view import CreateEventView

class AdminDashboardView:
    def __init__(self, root, db_manager, back_callback=None):
        """Initialize the admin dashboard view with tkinter widgets."""
        self.root = root
        self.db_manager = db_manager
        self.back_callback = back_callback
        
        # Create main frame
        self.dashboard_frame = tk.Frame(self.root)
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Set up the dashboard UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dashboard interface with event list and action buttons."""
        # Dashboard title
        title_label = tk.Label(self.dashboard_frame, text="Admin Dashboard - Upcoming Events", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))
        
        # Logout button (top left)
        logout_button = tk.Button(
            self.dashboard_frame, 
            text="Logout", 
            command=self.back_callback,
            font=("Arial", 11),
            width=10,
            height=2
        )
        logout_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create Event button (top right)
        create_event_button = tk.Button(
            self.dashboard_frame, 
            text="Create New Event", 
            command=self.show_create_event,
            font=("Arial", 11),
            width=15,
            height=2
        )
        create_event_button.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Create a frame for the event list
        list_frame = tk.Frame(self.dashboard_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))
        
        # Create Treeview widget for events
        columns = ("id", "name", "date", "time", "venue", "capacity", "price")
        self.event_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define column headings
        self.event_tree.heading("id", text="ID")
        self.event_tree.heading("name", text="Event Name")
        self.event_tree.heading("date", text="Date")
        self.event_tree.heading("time", text="Time")
        self.event_tree.heading("venue", text="Venue")
        self.event_tree.heading("capacity", text="Capacity")
        self.event_tree.heading("price", text="Price ($)")
        
        # Set column widths
        self.event_tree.column("id", width=50, anchor="center")
        self.event_tree.column("name", width=250)
        self.event_tree.column("date", width=100, anchor="center")
        self.event_tree.column("time", width=100, anchor="center")
        self.event_tree.column("venue", width=200)
        self.event_tree.column("capacity", width=100, anchor="center")
        self.event_tree.column("price", width=100, anchor="center")
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.event_tree.yview)
        self.event_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.event_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add events to the list
        self.populate_event_list()
        
        # Add event details and action buttons below the list
        details_frame = tk.Frame(self.dashboard_frame)
        details_frame.pack(fill=tk.X, expand=False, padx=20, pady=10)
        
        # Add control buttons
        button_frame = tk.Frame(details_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        edit_button = tk.Button(
            button_frame, 
            text="Edit Selected Event", 
            command=self.edit_selected_event,
            font=("Arial", 11),
            width=20,
            height=2
        )
        edit_button.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_button = tk.Button(
            button_frame, 
            text="Delete Selected Event", 
            command=self.delete_selected_event,
            font=("Arial", 11),
            width=20,
            height=2
        )
        delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        view_button = tk.Button(
            button_frame, 
            text="View Event Details", 
            command=self.view_event_details,
            font=("Arial", 11),
            width=20,
            height=2
        )
        view_button.pack(side=tk.LEFT)
        
        # Add double-click event to view details
        self.event_tree.bind("<Double-1>", lambda event: self.view_event_details())
    
    def populate_event_list(self):
        """Populate the event list with upcoming events from the database."""
        # Clear existing items
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
            
        # Get future events from the database
        future_events = self.db_manager.get_future_events()
        
        if not future_events:
            # Add a placeholder item if no events exist
            self.event_tree.insert("", tk.END, values=("N/A", "No upcoming events", "N/A", "N/A", "N/A", "N/A", "N/A"))
            return
            
        # Add each event to the treeview
        for event in future_events:
            # Format price with 2 decimal places
            price_formatted = f"${event['price']:.2f}"
            
            self.event_tree.insert("", tk.END, values=(
                event['id'],
                event['name'],
                event['date'],
                event['time'],
                event['venue'],
                event['capacity'],
                price_formatted
            ))
    
    def get_selected_event_id(self):
        """Get the ID of the currently selected event in the treeview."""
        selected_items = self.event_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an event first")
            return None
            
        # Get the first selected item
        item = selected_items[0]
        
        # Get the event ID from the first column
        event_id = self.event_tree.item(item, "values")[0]
        
        # Check if it's the placeholder "N/A"
        if event_id == "N/A":
            messagebox.showinfo("Info", "No events available to select")
            return None
            
        return event_id
    
    def show_create_event(self):
        """Show the event creation form."""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Show the create event form
        CreateEventView(self.root, self.db_manager, self.refresh_dashboard)
    
    def refresh_dashboard(self):
        """Refresh the dashboard view."""
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Recreate the dashboard
        AdminDashboardView(self.root, self.db_manager, self.back_callback)
    
    def edit_selected_event(self):
        """Edit the selected event."""
        event_id = self.get_selected_event_id()
        if event_id:
            # Clear the current frame
            for widget in self.root.winfo_children():
                widget.destroy()
                
            # Show the edit event form
            EditEventView(self.root, self.db_manager, event_id, self.refresh_dashboard)
    
    def delete_selected_event(self):
        """Delete the selected event after confirmation."""
        event_id = self.get_selected_event_id()
        if event_id:
            # Ask for confirmation
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete event ID {event_id}?"):
                if self.db_manager.delete_event(event_id):
                    messagebox.showinfo("Success", "Event deleted successfully")
                    # Refresh the event list
                    self.populate_event_list()
                else:
                    messagebox.showerror("Error", "Failed to delete event")
    
    def view_event_details(self):
        """View detailed information about the selected event."""
        event_id = self.get_selected_event_id()
        if event_id:
            # Get the event details
            event = self.db_manager.get_event_by_id(event_id)
            
            if event:
                # Format the details message
                details = f"Event Details:\n\n"
                details += f"ID: {event['id']}\n"
                details += f"Name: {event['name']}\n"
                details += f"Date: {event['date']}\n"
                details += f"Time: {event['time']}\n"
                details += f"Venue: {event['venue']}\n"
                details += f"Capacity: {event['capacity']}\n"
                details += f"Price: ${event['price']:.2f}\n\n"
                details += f"Description:\n{event['description']}"
                
                # Show the details in a message box
                messagebox.showinfo("Event Details", details)