import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import re

class CreateEventView:
    def __init__(self, root, db_manager, back_callback=None):
        """
        Initialise the event creation view with tkinter widgets.
        
        The back_callback is a function to call when user wants to go back.
        """
        # Store references to important objects we'll need throughout the class
        self.root = root  # Main application window
        self.db_manager = db_manager  # Database connection for saving events
        self.back_callback = back_callback  # Function to return to previous screen
        
        # Create the main container frame that will hold all our widgets
        self.frame = tk.Frame(root)  # Create a new frame widget
        # Pack the frame to fill the entire window with padding around the edges
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Call the method that creates all the form elements
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up all the user interface elements including labels, entry fields, and buttons.
        This method creates the entire form layout.
        """
        # Create the main title at the top of the form
        title_label = tk.Label(self.frame, text="Create New Event", font=("Arial", 20, "bold"))
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
        # Create a frame to hold the event name input and character counter
        name_frame = tk.Frame(content_frame)
        name_frame.pack(fill=tk.X, pady=(5, 10))  # Fill horizontally with vertical padding
        
        # Create a sub-frame for the label and character count on the same line
        name_header_frame = tk.Frame(name_frame)
        name_header_frame.pack(fill=tk.X)  # Fill the width of its parent
        
        # Label for the event name field
        name_label = tk.Label(name_header_frame, text="Event Name:", anchor="w", font=("Arial", 12))
        name_label.pack(side=tk.LEFT)  # Pack to the left side
        
        # Character count display (shows current length out of maximum 40)
        self.name_char_count = tk.Label(name_header_frame, text="0/40 characters", font=("Arial", 9), fg="gray")
        self.name_char_count.pack(side=tk.RIGHT)  # Pack to the right side
        
        # Text input field for the event name
        self.name_entry = tk.Entry(name_frame, font=("Arial", 12))
        self.name_entry.pack(fill=tk.X, pady=(5, 0))  # Fill width with top padding
        
        # Bind events to update character count and limit input length
        self.name_entry.bind('<KeyRelease>', self.update_name_char_count)  # Update count after key is released
        self.name_entry.bind('<KeyPress>', self.limit_name_input)  # Check limit before key is processed
        
        # === DATE SECTION ===
        # Create frame for date input
        date_frame = tk.Frame(content_frame)
        date_frame.pack(fill=tk.X, pady=10)  # Fill horizontally with vertical padding
        
        # Label explaining the required date format
        date_label = tk.Label(date_frame, text="Date (YYYY-MM-DD):", width=17, anchor="w", font=("Arial", 12))
        date_label.pack(side=tk.LEFT, padx=(0, 10))  # Pack left with right padding
        
        # Input field for the event date
        self.date_entry = tk.Entry(date_frame, font=("Arial", 12))
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Fill remaining space
        
        # Set default date to tomorrow's date automatically
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.date_entry.insert(0, tomorrow)  # Insert the calculated date
        
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
        self.time_entry.insert(0, "19:00")  # Default to 7:00 PM

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
        self.end_time_entry.insert(0, "21:00")  # Default to 9:00 PM
        
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
        self.price_entry.insert(0, "25.00")  # Default price of $25.00

        # === DESCRIPTION SECTION ===
        # Create frame for event description
        description_frame = tk.Frame(content_frame)
        description_frame.pack(fill=tk.X, pady=10)

        # Create header frame for description label and character count
        description_header_frame = tk.Frame(description_frame)
        description_header_frame.pack(fill=tk.X)

        # Label for description field
        description_label = tk.Label(description_header_frame, text="Description:", font=("Arial", 12))
        description_label.pack(side=tk.LEFT)

        # Character count display for description (maximum 1000 characters)
        self.description_char_count = tk.Label(description_header_frame, text="0/1000 characters", font=("Arial", 9), fg="gray")
        self.description_char_count.pack(side=tk.RIGHT)

        # Create frame to hold text area and scrollbar together
        text_scroll_frame = tk.Frame(description_frame)
        text_scroll_frame.pack(fill=tk.X, expand=True, pady=(5, 0))

        # Multi-line text widget for event description
        self.description_text = tk.Text(text_scroll_frame, height=8, font=("Arial", 12), wrap="word")
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Vertical scrollbar for the text area
        scrollbar = tk.Scrollbar(text_scroll_frame, orient="vertical", command=self.description_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Fill vertically on the right

        # Connect the scrollbar to the text widget so they work together
        self.description_text.config(yscrollcommand=scrollbar.set)

        # Bind events for description character counting and input limiting
        self.description_text.bind('<KeyRelease>', self.update_description_char_count)  # Update count after typing
        self.description_text.bind('<KeyPress>', self.limit_description_input)  # Check limit before typing

        # === BUTTON SECTION ===
        # Create frame to hold the action buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))  # Add top padding to separate from form
        
        # Create Event button - primary action button
        create_button = tk.Button(
            button_frame, 
            text="Create Event", 
            command=self.create_event,  # Call create_event method when clicked
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        create_button.pack(side=tk.LEFT, padx=(0, 10))  # Pack left with right padding
        
        # Clear Form button - secondary action button
        clear_button = tk.Button(
            button_frame, 
            text="Clear Form", 
            command=self.clear_form,  # Call clear_form method when clicked
            font=("Arial", 12),
            width=10,
            height=2
        )
        clear_button.pack(side=tk.LEFT)  # Pack to the left of create button
    
    def update_name_char_count(self, event=None):
        """
        Update the character count display for the event name field.
        Changes colour based on how close to the limit the user is.
        """
        # Get the current length of text in the name field
        current_length = len(self.name_entry.get())
        # Update the display to show current count out of maximum
        self.name_char_count.config(text=f"{current_length}/40 characters")
        
        # Change the colour of the counter based on character count
        if current_length > 35:  # Very close to limit - show red warning
            self.name_char_count.config(fg="red")
        elif current_length > 30:  # Getting close to limit - show orange warning
            self.name_char_count.config(fg="orange")
        else:  # Still plenty of space - show normal grey
            self.name_char_count.config(fg="gray")
    
    def limit_name_input(self, event):
        """
        Prevent the user from typing more than 40 characters in the event name field.
        Allows special keys like backspace and arrow keys to still work.
        """
        # Allow special navigation and editing keys to work normally
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
            return  # Don't block these keys
        
        # Check if we're already at the maximum character limit
        current_text = self.name_entry.get()  # Get current text in field
        if len(current_text) >= 40:  # If at or over limit
            return "break"  # Block the keystroke from being processed
    
    def update_description_char_count(self, event=None):
        """
        Update the character count display for the description field.
        Handles the automatic newline character that tkinter adds.
        """
        # Get all text from the description field (from start to end)
        current_text = self.description_text.get("1.0", tk.END)
        # Calculate length, accounting for automatic newline that tkinter adds
        current_length = len(current_text) - 1 if current_text.endswith('\n') else len(current_text)
        # Update the character count display
        self.description_char_count.config(text=f"{current_length}/1000 characters")
        
        # Change colour based on how close to the limit the user is
        if current_length > 950:  # Very close to limit - show red
            self.description_char_count.config(fg="red")
        elif current_length > 800:  # Getting close - show orange
            self.description_char_count.config(fg="orange")
        else:  # Plenty of space - show grey
            self.description_char_count.config(fg="gray")
    
    def limit_description_input(self, event):
        """
        Prevent the user from typing more than 1000 characters in the description field.
        Allows navigation keys to continue working.
        """
        # Allow special keys for navigation and editing
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Tab']:
            return  # Don't block these keys
        
        # Get current text and calculate its length
        current_text = self.description_text.get("1.0", tk.END)
        current_length = len(current_text) - 1 if current_text.endswith('\n') else len(current_text)
        
        # Block further input if at character limit
        if current_length >= 1000:
            return "break"  # Prevent the keystroke
    
    def validate_inputs(self):
        """
        Check all form inputs to make sure they are valid before creating the event.
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
        
        # Check that event name is not too long
        if len(name) > 40:
            messagebox.showerror("Error", "Event name must be 40 characters or less")
            return False
        
        # Check that description is not too long
        description = self.description_text.get("1.0", tk.END).strip()
        if len(description) > 1000:
            messagebox.showerror("Error", "Description must be 1000 characters or less")
            return False
        
        # Validate that date is in the correct format (YYYY-MM-DD)
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # Create pattern for date format
        if not date_pattern.match(date):  # Check if date matches the pattern
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
            return False
        
        # Validate that start time is in correct format (HH:MM in 24-hour format)
        time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')  # Pattern for 24-hour time
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
        if self.db_manager.date_has_event(date):
            messagebox.showerror(
                "Date Conflict", 
                f"An event is already scheduled on {date}.\nThe venue can only host one event per day."
            )
            return False
        
        return True  # All validation checks passed!
    
    def create_event(self):
        """
        Create a new event with the information provided in the form.
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
        
        # Save the event to the database using the database manager
        event_id = self.db_manager.create_event(
            name=name,
            description=description,
            date=date,
            time=time,
            end_time=end_time,
            price=price
        )
        
        # Check if the event was successfully created
        if event_id:  # If event_id is returned, creation was successful
            messagebox.showinfo("Success", f"Event '{name}' created successfully!")
            # Return to the main dashboard
            if self.back_callback:
                self.back_callback()
        else:  # If no event_id returned, something went wrong
            messagebox.showerror("Error", "Failed to create event")
    
    def clear_form(self):
        """
        Reset all form fields to their default values.
        Useful if user wants to start over or create multiple similar events.
        """
        # Clear the event name field completely
        self.name_entry.delete(0, tk.END)
        
        # Reset date field to tomorrow's date
        self.date_entry.delete(0, tk.END)  # Clear current date
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.date_entry.insert(0, tomorrow)  # Insert new default date
        
        # Reset start time to default
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "19:00")  # 7:00 PM
        
        # Reset end time to default
        self.end_time_entry.delete(0, tk.END)
        self.end_time_entry.insert(0, "21:00")  # 9:00 PM
        
        # Reset price to default value
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, "25.00")  # $25.00
        
        # Clear the description text area completely
        self.description_text.delete("1.0", tk.END)
        
        # Update the character count displays to show 0 characters
        self.update_name_char_count()
        self.update_description_char_count()