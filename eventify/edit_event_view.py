import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import re

class EditEventView:
    def __init__(self, root, db_manager, event_id, back_callback=None):
        """
        Initialise the event editing view with tkinter widgets.
        
        - The event_id parameter is the ID of the event to edit
        - The back_callback parameter is the function to call when user wants to go back
        """
        # Store references to important objects we'll need throughout the class
        self.root = root  # Main application window
        self.db_manager = db_manager  # Database connection for loading/saving events
        self.event_id = event_id  # ID of the event we're editing
        self.back_callback = back_callback  # Function to return to previous screen
        
        # Load the existing event data from the database
        self.event = self.db_manager.get_event_by_id(event_id)
        
        # Check if the event exists in the database
        if not self.event:
            # Show error message if event not found
            messagebox.showerror("Error", f"Event with ID {event_id} not found")
            # Return to previous screen if callback is provided
            if back_callback:
                back_callback()
            return  # Exit the initialisation
        
        # Create the main container frame that will hold all our widgets
        self.frame = tk.Frame(root)  # Create a new frame widget
        # Pack the frame to fill the entire window with padding around the edges
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Call the method that creates all the form elements
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up all the user interface elements including labels, entry fields, and buttons.
        This method creates the entire form layout and populates it with existing event data.
        """
        # Create the main title showing which event is being edited
        title_label = tk.Label(self.frame, text=f"Edit Event: {self.event['name']}", font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))  # Add vertical padding above and below
        
        # Create a back button if a callback function was provided
        if self.back_callback:
            back_button = tk.Button(
                self.frame, 
                text="Back to Dashboard", 
                command=self.back_callback,  # Function to call when clicked
                font=("Arial", 10),
                width=15
            )
            # Position the button in the top-left corner using absolute positioning
            back_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create a centered frame to hold all the form content
        content_frame = tk.Frame(self.frame, width=600)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=100)  # Centre with horizontal padding
        
        # === EVENT NAME SECTION ===
        # Create frame for event name input
        name_frame = tk.Frame(content_frame)
        name_frame.pack(fill=tk.X, pady=10)  # Fill horizontally with vertical padding
        
        # Label for the event name field
        name_label = tk.Label(name_frame, text="Event Name:", width=10, anchor="w", font=("Arial", 12))
        name_label.pack(side=tk.LEFT, padx=(0, 10))  # Pack to left with right padding
        
        # Text input field for the event name
        self.name_entry = tk.Entry(name_frame, font=("Arial", 12))
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Fill remaining space
        # Insert the existing event name into the field
        self.name_entry.insert(0, self.event['name'])
        
        # === DATE SECTION ===
        # Create frame for date input
        date_frame = tk.Frame(content_frame)
        date_frame.pack(fill=tk.X, pady=10)
        
        # Label explaining the required date format
        date_label = tk.Label(date_frame, text="Date (YYYY-MM-DD):", width=17, anchor="w", font=("Arial", 12))
        date_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Input field for the event date
        self.date_entry = tk.Entry(date_frame, font=("Arial", 12))
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Insert the existing event date into the field
        self.date_entry.insert(0, self.event['date'])
        
        # === START TIME SECTION ===
        # Create frame for start time input
        time_frame = tk.Frame(content_frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        # Label for start time with format hint
        time_label = tk.Label(time_frame, text="Start Time (HH:MM):", width=16, anchor="w", font=("Arial", 12))
        time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Input field for start time
        self.time_entry = tk.Entry(time_frame, font=("Arial", 12))
        self.time_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Insert the existing start time into the field
        self.time_entry.insert(0, self.event['time'])
        
        # === END TIME SECTION ===
        # Create frame for end time input
        end_time_frame = tk.Frame(content_frame)
        end_time_frame.pack(fill=tk.X, pady=10)
        
        # Label for end time
        end_time_label = tk.Label(end_time_frame, text="End Time (HH:MM):", width=16, anchor="w", font=("Arial", 12))
        end_time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Input field for end time
        self.end_time_entry = tk.Entry(end_time_frame, font=("Arial", 12))
        self.end_time_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Insert the existing end time into the field
        self.end_time_entry.insert(0, self.event['end_time'])
        
        # === VENUE INFORMATION SECTION ===
        # Create frame for venue display (read-only information)
        venue_frame = tk.Frame(content_frame)
        venue_frame.pack(fill=tk.X, pady=10)
        
        # Venue label
        venue_label = tk.Label(venue_frame, text="Venue:", width=6, anchor="w", font=("Arial", 12))
        venue_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Display venue information (this is fixed and cannot be changed)
        venue_info = tk.Label(venue_frame, text="Castle Hill High School auditorium (550 seats)", font=("Arial", 12), anchor="w")
        venue_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === PRICE SECTION ===
        # Create frame for ticket price input
        price_frame = tk.Frame(content_frame)
        price_frame.pack(fill=tk.X, pady=10)
        
        # Label for price field
        price_label = tk.Label(price_frame, text="Price ($):", width=7, anchor="w", font=("Arial", 12))
        price_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Input field for ticket price
        self.price_entry = tk.Entry(price_frame, font=("Arial", 12))
        self.price_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Insert the existing price, converting from number to string
        self.price_entry.insert(0, str(self.event['price']))

        # === DESCRIPTION SECTION ===
        # Create frame for event description
        description_frame = tk.Frame(content_frame)
        description_frame.pack(fill=tk.X, pady=10)

        # Label for description field
        description_label = tk.Label(description_frame, text="Description:", font=("Arial", 12))
        description_label.pack(anchor="w")  # Anchor to the left (west)

        # Create frame to hold text area and scrollbar together
        text_scroll_frame = tk.Frame(description_frame)
        text_scroll_frame.pack(fill=tk.X, expand=True, pady=(5, 0))

        # Multi-line text widget for event description
        self.description_text = tk.Text(text_scroll_frame, height=8, font=("Arial", 12), wrap="word")
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Insert the existing description into the text area (handle None values)
        self.description_text.insert("1.0", self.event['description'] if self.event['description'] else "")

        # Vertical scrollbar for the text area
        scrollbar = tk.Scrollbar(text_scroll_frame, orient="vertical", command=self.description_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Fill vertically on the right

        # Connect the scrollbar to the text widget so they work together
        self.description_text.config(yscrollcommand=scrollbar.set)

        # === BUTTON SECTION ===
        # Create frame to hold the action buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))  # Add top padding to separate from form
        
        # Save Changes button - primary action button
        save_button = tk.Button(
            button_frame, 
            text="Save Changes", 
            command=self.save_changes,  # Call save_changes method when clicked
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))  # Pack left with right padding
        
        # Cancel button - secondary action button
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=self.back_callback if self.back_callback else self.frame.quit,  # Go back or quit
            font=("Arial", 12),
            width=10,
            height=2
        )
        cancel_button.pack(side=tk.LEFT)  # Pack to the left of save button
    
    def validate_inputs(self):
        """
        Check all form inputs to make sure they are valid before saving the event.
        Returns True if all inputs are valid, False if any problems are found.
        """
        # Get all the values from the form fields and remove extra spaces
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        price = self.price_entry.get().strip()
        
        # Check that all required fields have been filled in
        if not name or not date or not time or not end_time:
            messagebox.showerror("Error", "Name, date, start time, and end time are required fields")
            return False  # Validation failed
        
        # Validate that date is in the correct format (YYYY-MM-DD)
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}')  # Create pattern for date format
        if not date_pattern.match(date):  # Check if date matches the pattern
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
            return False
        
        # Validate that start time is in correct format (HH:MM in 24-hour format)
        time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)')  # Pattern for 24-hour time
        if not time_pattern.match(time):
            messagebox.showerror("Error", "Start time must be in HH:MM format (24-hour)")
            return False
            
        # Validate that end time is in correct format
        if not time_pattern.match(end_time):
            messagebox.showerror("Error", "End time must be in HH:MM format (24-hour)")
            return False
        
        # Check that end time is after start time (events can't end before they start!)
        try:
            # Split times into hours and minutes and convert to integers
            start_hour, start_minute = map(int, time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            # Convert times to total minutes for easy comparison
            start_minutes_total = start_hour * 60 + start_minute
            end_minutes_total = end_hour * 60 + end_minute
            
            # Check if end time is before or same as start time
            if end_minutes_total <= start_minutes_total:
                messagebox.showerror("Error", "End time must be after start time")
                return False
        except ValueError:  # Catch errors if time conversion fails
            messagebox.showerror("Error", "Invalid time format")
            return False
        
        # Validate that price is a valid positive number
        try:
            price_float = float(price)  # Try to convert price to decimal number
            if price_float < 0:  # Price can't be negative
                messagebox.showerror("Error", "Price must be a positive number")
                return False
        except ValueError:  # Catch error if price isn't a valid number
            messagebox.showerror("Error", "Price must be a number")
            return False
        
        # Check that the event date is not in the past
        try:
            # Convert date string to actual date object
            event_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            today = datetime.datetime.now().date()  # Get today's date
            
            # Compare dates to ensure event is in future
            if event_date < today:
                messagebox.showerror("Error", "Event date cannot be in the past")
                return False
        except ValueError:  # Catch error if date conversion fails
            messagebox.showerror("Error", "Invalid date")
            return False
        
        # Check if another event is already scheduled on this date
        # (exclude the current event being edited from this check)
        if self.db_manager.date_has_event(date, exclude_event_id=self.event_id):
            messagebox.showerror(
                "Date Conflict", 
                f"An event is already scheduled on {date}.\nThe venue can only host one event per day."
            )
            return False
        
        return True  # All validation checks passed!
    
    def save_changes(self):
        """
        Save the modified event information to the database.
        Only proceeds if all validation checks pass.
        """
        # First check if all inputs are valid
        if not self.validate_inputs():
            return  # Stop here if validation failed
        
        # Get all values from the form fields
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        price = float(self.price_entry.get().strip())  # Convert price to decimal
        description = self.description_text.get("1.0", tk.END).strip()
        
        # Set fixed venue and capacity values (these don't change)
        venue = "Castle Hill High School auditorium"
        capacity = 550
        
        # Update the event in the database using the database manager
        success = self.db_manager.update_event(
            event_id=self.event_id,  # Which event to update
            name=name,
            description=description,
            date=date,
            time=time,
            end_time=end_time,
            venue=venue,
            capacity=capacity,
            price=price
        )
        
        # Check if the event was successfully updated
        if success:  # If True is returned, update was successful
            messagebox.showinfo("Success", f"Event '{name}' updated successfully!")
            # Return to the main dashboard
            if self.back_callback:
                self.back_callback()
        else:  # If False returned, something went wrong
            messagebox.showerror("Error", "Failed to update event")