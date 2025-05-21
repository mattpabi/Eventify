# edit_event_view.py - Event editing UI class

import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import re

class EditEventView:
    def __init__(self, root, db_manager, event_id, back_callback=None):
        """Initialise the event editing view with tkinter widgets."""
        self.root = root
        self.db_manager = db_manager
        self.event_id = event_id
        self.back_callback = back_callback
        self.event = self.db_manager.get_event_by_id(event_id)
        
        if not self.event:
            messagebox.showerror("Error", f"Event with ID {event_id} not found")
            if back_callback:
                back_callback()
            return
        
        # Create main frame
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and place widgets
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface elements."""
        # App title
        title_label = tk.Label(self.frame, text=f"Edit Event: {self.event['name']}", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))
        
        # Back button
        if self.back_callback:
            back_button = tk.Button(
                self.frame, 
                text="Back to Dashboard", 
                command=self.back_callback,
                font=("Arial", 10),
                width=15
            )
            back_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create centered content frame
        content_frame = tk.Frame(self.frame, width=600)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=100)
        
        # Event Name
        name_frame = tk.Frame(content_frame)
        name_frame.pack(fill=tk.X, pady=10)
        
        name_label = tk.Label(name_frame, text="Event Name:", width=10, anchor="w", font=("Arial", 12))
        name_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.name_entry = tk.Entry(name_frame, font=("Arial", 12))
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.name_entry.insert(0, self.event['name'])
        
        # Date
        date_frame = tk.Frame(content_frame)
        date_frame.pack(fill=tk.X, pady=10)
        
        date_label = tk.Label(date_frame, text="Date (YYYY-MM-DD):", width=17, anchor="w", font=("Arial", 12))
        date_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.date_entry = tk.Entry(date_frame, font=("Arial", 12))
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.date_entry.insert(0, self.event['date'])
        
        # Time
        time_frame = tk.Frame(content_frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        time_label = tk.Label(time_frame, text="Time (HH:MM):", width=12, anchor="w", font=("Arial", 12))
        time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.time_entry = tk.Entry(time_frame, font=("Arial", 12))
        self.time_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.time_entry.insert(0, self.event['time'])
        
        # Venue information (read-only display)
        venue_frame = tk.Frame(content_frame)
        venue_frame.pack(fill=tk.X, pady=10)
        
        venue_label = tk.Label(venue_frame, text="Venue:", width=6, anchor="w", font=("Arial", 12))
        venue_label.pack(side=tk.LEFT, padx=(0, 10))
        
        venue_info = tk.Label(venue_frame, text="Castle Hill High School auditorium (550 seats)", font=("Arial", 12), anchor="w")
        venue_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Price
        price_frame = tk.Frame(content_frame)
        price_frame.pack(fill=tk.X, pady=10)
        
        price_label = tk.Label(price_frame, text="Price ($):", width=7, anchor="w", font=("Arial", 12))
        price_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.price_entry = tk.Entry(price_frame, font=("Arial", 12))
        self.price_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.price_entry.insert(0, str(self.event['price']))

        # Description
        description_frame = tk.Frame(content_frame)
        description_frame.pack(fill=tk.X, pady=10)

        description_label = tk.Label(description_frame, text="Description:", font=("Arial", 12))
        description_label.pack(anchor="w")

        # Create a frame to hold both Text and Scrollbar side by side
        text_scroll_frame = tk.Frame(description_frame)
        text_scroll_frame.pack(fill=tk.X, expand=True, pady=(5, 0))

        # Text widget with fixed height and width (width optional)
        self.description_text = tk.Text(text_scroll_frame, height=12, font=("Arial", 12), wrap="word")
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.description_text.insert("1.0", self.event['description'] if self.event['description'] else "")

        # Scrollbar packed to the right of the Text widget, inside the same frame
        scrollbar = tk.Scrollbar(text_scroll_frame, orient="vertical", command=self.description_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Connect scrollbar and text widget
        self.description_text.config(yscrollcommand=scrollbar.set)

        # Button frame
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Save and Cancel buttons
        save_button = tk.Button(
            button_frame, 
            text="Save Changes", 
            command=self.save_changes,
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=self.back_callback if self.back_callback else self.frame.quit,
            font=("Arial", 12),
            width=10,
            height=2
        )
        cancel_button.pack(side=tk.LEFT)
    
    def validate_inputs(self):
        """Validate all inputs before saving the event."""
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        price = self.price_entry.get().strip()
        
        # Check required fields
        if not name or not date or not time:
            messagebox.showerror("Error", "Name, date, and time are required fields")
            return False
        
        # Validate date format (YYYY-MM-DD)
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(date):
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
            return False
        
        # Validate time format (HH:MM)
        time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
        if not time_pattern.match(time):
            messagebox.showerror("Error", "Time must be in HH:MM format (24-hour)")
            return False
        
        # Validate price as float
        try:
            price_float = float(price)
            if price_float < 0:
                messagebox.showerror("Error", "Price must be a positive number")
                return False
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
            return False
        
        return True
    
    def save_changes(self):
        """Save the event changes to the database."""
        if not self.validate_inputs():
            return
        
        # Get values from form
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        price = float(self.price_entry.get().strip())
        description = self.description_text.get("1.0", tk.END).strip()
        
        # Fixed venue and capacity values
        venue = "Castle Hill High School auditorium"
        capacity = 550
        
        # Update the event in the database
        success = self.db_manager.update_event(
            event_id=self.event_id,
            name=name,
            description=description,
            date=date,
            time=time,
            venue=venue,
            capacity=capacity,
            price=price
        )
        
        if success:
            messagebox.showinfo("Success", f"Event '{name}' updated successfully!")
            # Return to dashboard
            if self.back_callback:
                self.back_callback()
        else:
            messagebox.showerror("Error", "Failed to update event")