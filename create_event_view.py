# create_event_view.py - Event creation UI class

import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import re

class CreateEventView:
    def __init__(self, root, db_manager, back_callback=None):
        """Initialise the event creation view with tkinter widgets."""
        self.root = root
        self.db_manager = db_manager
        self.back_callback = back_callback
        
        # Create main frame
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and place widgets
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface elements."""
        # App title
        title_label = tk.Label(self.frame, text="Create New Event", font=("Arial", 20, "bold"))
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
        
        # Date
        date_frame = tk.Frame(content_frame)
        date_frame.pack(fill=tk.X, pady=10)
        
        date_label = tk.Label(date_frame, text="Date (YYYY-MM-DD):", width=17, anchor="w", font=("Arial", 12))
        date_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.date_entry = tk.Entry(date_frame, font=("Arial", 12))
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Set default date to tomorrow
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.date_entry.insert(0, tomorrow)
        
        # Start Time
        time_frame = tk.Frame(content_frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        time_label = tk.Label(time_frame, text="Start Time (HH:MM):", width=16, anchor="w", font=("Arial", 12))
        time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.time_entry = tk.Entry(time_frame, font=("Arial", 12))
        self.time_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.time_entry.insert(0, "19:00")  # Default time

        # End Time
        end_time_frame = tk.Frame(content_frame)
        end_time_frame.pack(fill=tk.X, pady=10)
        
        end_time_label = tk.Label(end_time_frame, text="End Time (HH:MM):", width=16, anchor="w", font=("Arial", 12))
        end_time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.end_time_entry = tk.Entry(end_time_frame, font=("Arial", 12))
        self.end_time_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.end_time_entry.insert(0, "21:00")  # Default end time
        
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
        self.price_entry.insert(0, "25.00")  # Default price

        # Description
        description_frame = tk.Frame(content_frame)
        description_frame.pack(fill=tk.X, pady=10)

        description_label = tk.Label(description_frame, text="Description:", font=("Arial", 12))
        description_label.pack(anchor="w")

        # Create a frame to hold both Text and Scrollbar side by side
        text_scroll_frame = tk.Frame(description_frame)
        text_scroll_frame.pack(fill=tk.X, expand=True, pady=(5, 0))

        # Text widget with fixed height and width (width optional)
        self.description_text = tk.Text(text_scroll_frame, height=8, font=("Arial", 12), wrap="word")
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar packed to the right of the Text widget, inside the same frame
        scrollbar = tk.Scrollbar(text_scroll_frame, orient="vertical", command=self.description_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Connect scrollbar and text widget
        self.description_text.config(yscrollcommand=scrollbar.set)

        # Button frame
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Create and Cancel buttons
        create_button = tk.Button(
            button_frame, 
            text="Create Event", 
            command=self.create_event,
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        create_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = tk.Button(
            button_frame, 
            text="Clear Form", 
            command=self.clear_form,
            font=("Arial", 12),
            width=10,
            height=2
        )
        clear_button.pack(side=tk.LEFT)
    
    def validate_inputs(self):
        """Validate all inputs before creating the event."""
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        price = self.price_entry.get().strip()
        
        # Check required fields
        if not name or not date or not time or not end_time:
            messagebox.showerror("Error", "Name, date, start time, and end time are required fields")
            return False
        
        # Validate date format (YYYY-MM-DD)
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(date):
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
            return False
        
        # Validate time format (HH:MM)
        time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
        if not time_pattern.match(time):
            messagebox.showerror("Error", "Start time must be in HH:MM format (24-hour)")
            return False
            
        # Validate end time format (HH:MM)
        if not time_pattern.match(end_time):
            messagebox.showerror("Error", "End time must be in HH:MM format (24-hour)")
            return False
        
        # Validate that end time is after start time
        try:
            start_hour, start_minute = map(int, time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            start_minutes_total = start_hour * 60 + start_minute
            end_minutes_total = end_hour * 60 + end_minute
            
            if end_minutes_total <= start_minutes_total:
                messagebox.showerror("Error", "End time must be after start time")
                return False
        except ValueError:
            messagebox.showerror("Error", "Invalid time format")
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
        
        # Validate that the date is not in the past
        try:
            event_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            today = datetime.datetime.now().date()
            
            if event_date < today:
                messagebox.showerror("Error", "Event date cannot be in the past")
                return False
        except ValueError:
            messagebox.showerror("Error", "Invalid date")
            return False
        
        # Check if date already has an event scheduled
        if self.db_manager.date_has_event(date):
            messagebox.showerror(
                "Date Conflict", 
                f"An event is already scheduled on {date}.\nThe venue can only host one event per day."
            )
            return False
        
        return True
    
    def create_event(self):
        """Create a new event with the provided information."""
        if not self.validate_inputs():
            return
        
        # Get values from form
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        price = float(self.price_entry.get().strip())
        description = self.description_text.get("1.0", tk.END).strip()
        
        # Create the event in the database (venue and capacity are fixed)
        event_id = self.db_manager.create_event(
            name=name,
            description=description,
            date=date,
            time=time,
            end_time=end_time,
            price=price
        )
        
        if event_id:
            messagebox.showinfo("Success", f"Event '{name}' created successfully!")
            # Return to dashboard
            if self.back_callback:
                self.back_callback()
        else:
            messagebox.showerror("Error", "Failed to create event")
    
    def clear_form(self):
        """Clear all form fields."""
        self.name_entry.delete(0, tk.END)
        
        # Reset date to tomorrow
        self.date_entry.delete(0, tk.END)
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.date_entry.insert(0, tomorrow)
        
        # Reset time to default
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "19:00")
        
        # Reset end time to default
        self.end_time_entry.delete(0, tk.END)
        self.end_time_entry.insert(0, "21:00")
        
        # Reset price to default
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, "25.00")
        
        # Clear description
        self.description_text.delete("1.0", tk.END)