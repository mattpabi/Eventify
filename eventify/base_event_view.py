import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import re


class BaseEventView:  
    def __init__(self, root, db_manager, back_callback=None, title="Event"):
        """
        Initialise the BaseEventView with required components and references.
        """
        # Store references to important objects that we'll need throughout the class
        self.root = root  # Main application window
        self.db_manager = db_manager  # Database connection for data operations
        self.back_callback = back_callback  # Function to return to previous screen
        self.title = title  # Title to display on the form
        
        # Create the main container frame that will hold all our GUI widgets
        # fill=BOTH means expand in both horizontal and vertical directions
        # expand=True allows the frame to grow when window is resized
        # padx/pady add spacing around the frame edges
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Initialise widget references that will be created later in setup_ui()
        # Setting these to None initially prevents errors if referenced before creation
        self.name_entry = None  # Text input for event name
        self.date_entry = None  # Text input for event date
        self.time_entry = None  # Text input for start time
        self.end_time_entry = None  # Text input for end time
        self.price_entry = None  # Text input for ticket price
        self.description_text = None  # Multi-line text area for description
        self.name_char_count = None  # Label showing name character count
        self.description_char_count = None  # Label showing description character count
    
    def setup_ui(self):
        """
        Set up all the user interface elements for the event form.
        
        This method creates the complete form layout including:
        - Title heading
        - Back button (if callback provided)
        - All input sections (name, date, time, venue, price, description)
        - Button section for save/cancel actions
        """
        # Create the main title at the top of the form
        # font parameter: (font_family, size, style)
        title_label = tk.Label(self.frame, text=self.title, font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 30))  # Add vertical spacing: 10px above, 30px below
        
        # Create a back button only if a callback function was provided
        if self.back_callback:
            back_button = tk.Button(
                self.frame, 
                text="Back to Dashboard", 
                command=self.back_callback,  # Function to call when clicked
                font=("Arial", 10),
                width=15
            )
            # Position button at top-left corner using place geometry manager
            # relx/rely use relative positioning (0.0 = left/top, 1.0 = right/bottom)
            back_button.place(relx=0.0, rely=0.0, anchor="nw")
        
        # Create a centred frame to hold all the form content
        # This provides consistent spacing and alignment for form elements
        content_frame = tk.Frame(self.frame, width=600)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=100)
        
        # Create all form sections by calling individual setup methods
        # This modular approach makes the code easier to maintain and understand
        self.create_name_section(content_frame)      # Event name input
        self.create_date_section(content_frame)      # Date selection
        self.create_time_sections(content_frame)     # Start and end times
        self.create_venue_section(content_frame)     # Venue information (read-only)
        self.create_price_section(content_frame)     # Ticket price input
        self.create_description_section(content_frame)  # Event description
        self.create_button_section(content_frame)    # Action buttons (save, cancel, etc.)
    
    def create_name_section(self, parent):
        """
        Create the event name input section with character counting and limiting.
        
        Parameters:
            parent: The parent frame to contain this section
        """
        # Create container frame for this entire section
        name_frame = tk.Frame(parent)
        name_frame.pack(fill=tk.X, pady=(5, 10))  # Fill horizontally, add vertical spacing
        
        # Create header frame to hold label and character count on same line
        name_header_frame = tk.Frame(name_frame)
        name_header_frame.pack(fill=tk.X)
        
        # Create label for the name input field
        # anchor="w" aligns text to the left (west)
        name_label = tk.Label(name_header_frame, text="Event Name:", anchor="w", font=("Arial", 12))
        name_label.pack(side=tk.LEFT)  # Position on left side of header
        
        # Create character count display label
        # This will be updated dynamically as user types
        self.name_char_count = tk.Label(name_header_frame, text="0/40 characters", 
                                       font=("Arial", 9), fg="gray")
        self.name_char_count.pack(side=tk.RIGHT)  # Position on right side of header
        
        # Create the actual text input field for event name
        self.name_entry = tk.Entry(name_frame, font=("Arial", 12))
        self.name_entry.pack(fill=tk.X, pady=(5, 0))  # Fill width, add top spacing
        
        # Bind events to enable character counting and input limiting
        # '<KeyRelease>' triggers after a key is released (character appears)
        self.name_entry.bind('<KeyRelease>', self.update_name_char_count)
        # '<KeyPress>' triggers before character appears (allows prevention)
        self.name_entry.bind('<KeyPress>', self.limit_name_input)
    
    def create_date_section(self, parent):
        """
        Create the event date input section with format guidance.
        
        The parent parameter is the parent frame to contain this section
        """
        # Create container frame for date input
        date_frame = tk.Frame(parent)
        date_frame.pack(fill=tk.X, pady=10)  # Fill horizontally, add vertical spacing
        
        # Create label with specific width for consistent alignment
        # width=17 ensures consistent spacing across all form labels
        date_label = tk.Label(date_frame, text="Date (YYYY-MM-DD):", width=17, 
                             anchor="w", font=("Arial", 12))
        date_label.pack(side=tk.LEFT, padx=(0, 10))  # Left align with right padding
        
        # Create text input for date entry
        # expand=True allows field to grow if window is resized
        self.date_entry = tk.Entry(date_frame, font=("Arial", 12))
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_time_sections(self, parent):
        """
        Create the start and end time input sections.
        
        The parent parameter is the parent frame to contain these sections
        """
        # Start time section
        time_frame = tk.Frame(parent)
        time_frame.pack(fill=tk.X, pady=10)
        
        # Label for start time with consistent width for alignment
        time_label = tk.Label(time_frame, text="Start Time (HH:MM):", width=16, 
                             anchor="w", font=("Arial", 12))
        time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Text input for start time
        self.time_entry = tk.Entry(time_frame, font=("Arial", 12))
        self.time_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # End time section (similar structure to start time)
        end_time_frame = tk.Frame(parent)
        end_time_frame.pack(fill=tk.X, pady=10)
        
        # Label for end time
        end_time_label = tk.Label(end_time_frame, text="End Time (HH:MM):", width=16, 
                                 anchor="w", font=("Arial", 12))
        end_time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Text input for end time
        self.end_time_entry = tk.Entry(end_time_frame, font=("Arial", 12))
        self.end_time_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_venue_section(self, parent):
        """
        Create the venue information section (read-only display).
        
        This section shows the venue details but doesn't allow editing, as the venue is fixed for all events in this system.
        
        The parent parameter is the parent frame to contain this section
        """
        # Create container frame for venue information
        venue_frame = tk.Frame(parent)
        venue_frame.pack(fill=tk.X, pady=10)
        
        # Create venue label
        venue_label = tk.Label(venue_frame, text="Venue:", width=6, 
                              anchor="w", font=("Arial", 12))
        venue_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Display venue information (read-only)
        # This shows the fixed venue details that apply to all events
        venue_info = tk.Label(venue_frame, text="Castle Hill High School auditorium (550 seats)", 
                             font=("Arial", 12), anchor="w")
        venue_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_price_section(self, parent):
        """
        Create the ticket price input section.
        
        The parent parameter is the parent frame to contain this section.
        """
        # Create container frame for price input
        price_frame = tk.Frame(parent)
        price_frame.pack(fill=tk.X, pady=10)
        
        # Create price label with dollar sign indication
        price_label = tk.Label(price_frame, text="Price ($):", width=7, 
                              anchor="w", font=("Arial", 12))
        price_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create text input for price entry
        self.price_entry = tk.Entry(price_frame, font=("Arial", 12))
        self.price_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_description_section(self, parent):
        """
        Create the event description input section with character counting and scrolling.
        
        This section provides a multi-line text area for detailed event descriptions with live character counting and input limiting.
        
        The parent parameter is the parent frame to contain this section.
        """
        # Create container frame for description section
        description_frame = tk.Frame(parent)
        description_frame.pack(fill=tk.X, pady=10)
        
        # Create header frame for description label and character count
        description_header_frame = tk.Frame(description_frame)
        description_header_frame.pack(fill=tk.X)
        
        # Create description label
        description_label = tk.Label(description_header_frame, text="Description:", 
                                    font=("Arial", 12))
        description_label.pack(side=tk.LEFT)
        
        # Create character count display for description
        # This will be updated as user types to show remaining characters
        self.description_char_count = tk.Label(description_header_frame, 
                                              text="0/1000 characters", 
                                              font=("Arial", 9), fg="gray")
        self.description_char_count.pack(side=tk.RIGHT)
        
        # Create frame to hold text area and scrollbar together
        # This ensures the scrollbar stays aligned with the text area
        text_scroll_frame = tk.Frame(description_frame)
        text_scroll_frame.pack(fill=tk.X, expand=True, pady=(5, 0))
        
        # Create multi-line text widget for description input
        # height=8 sets the visible number of lines
        # wrap="word" ensures text wraps at word boundaries, not mid-word
        self.description_text = tk.Text(text_scroll_frame, height=8, font=("Arial", 12), 
                                       wrap="word")
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create vertical scrollbar for the text area
        # This allows scrolling when text exceeds the visible area
        scrollbar = tk.Scrollbar(text_scroll_frame, orient="vertical", 
                               command=self.description_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Connect scrollbar to text widget so they work together
        self.description_text.config(yscrollcommand=scrollbar.set)
        
        # Bind events for description character counting and input limiting
        self.description_text.bind('<KeyRelease>', self.update_description_char_count)
        self.description_text.bind('<KeyPress>', self.limit_description_input)
    
    def create_button_section(self, parent):
        """
        Create the button section for form actions.
        
        This method is designed to be overridden by subclasses to provide their own specific buttons (e.g., Save, Cancel, Update, Delete).
        
        The parent parameter is the parent frame to contain the buttons
            
        Returns the button frame for subclasses to add their specific buttons
        """
        # Create container frame for action buttons
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(30, 0))  # Add extra top spacing
        return button_frame
    
    def update_name_char_count(self, event=None):
        """
        Update the character count display for the event name field.
        
        This method is called whenever a key is released in the name field.
        It updates the character count and changes colour based on length.
        
        The event parameter is the tkinter event object (not used but required for binding)
        """
        # Get current length of text in name field
        current_length = len(self.name_entry.get())
        
        # Update the character count display
        self.name_char_count.config(text=f"{current_length}/40 characters")
        
        # Change colour based on character count to warn user
        if current_length > 35:          # Very close to limit - red warning
            self.name_char_count.config(fg="red")
        elif current_length > 30:       # Getting close to limit - orange warning
            self.name_char_count.config(fg="orange")
        else:                           # Normal length - grey text
            self.name_char_count.config(fg="gray")
    
    def limit_name_input(self, event):
        """
        Prevent the user from typing more than 40 characters in the event name field.
        
        This method is called before each character is entered and can prevent
        the character from being added if the limit would be exceeded.
        
        The event parameter is the tkinter event object containing key information
            
        Returns "break" string to prevent character entry if limit reached, or None (default) to allow character entry
        """
        # Allow navigation and editing keys regardless of character count
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
            return  # Return None (default) to allow these keys
        
        # Get current text in the name field
        current_text = self.name_entry.get()
        
        # If already at character limit, prevent new character entry
        if len(current_text) >= 40:
            return "break"  # This prevents the character from being entered
    
    def update_description_char_count(self, event=None):
        """
        Update the character count display for the description field.
        
        This method handles the complexity of counting characters in a Text widget, which includes handling newline characters properly.
        
        The event parameter is the tkinter event object containing key information
        """
        # Get all text from the description field
        # "1.0" means line 1, character 0 (start)
        # tk.END means the end of all text
        current_text = self.description_text.get("1.0", tk.END)
        
        # Text widgets always end with a newline, so subtract 1 if present
        # This gives accurate character count that user expects
        current_length = len(current_text) - 1 if current_text.endswith('\n') else len(current_text)
        
        # Update the character count display
        self.description_char_count.config(text=f"{current_length}/1000 characters")
        
        # Change colour based on character count to warn user
        if current_length > 950:  # Very close to limit - red warning
            self.description_char_count.config(fg="red")
        elif current_length > 800:  # Getting close to limit - orange warning
            self.description_char_count.config(fg="orange")
        else:  # Normal length - grey text
            self.description_char_count.config(fg="gray")
    
    def limit_description_input(self, event):
        """
        Prevent the user from typing more than 1000 characters in the description field.
        
        This method checks the current character count and prevents new character
        entry if the limit would be exceeded.
        
        The event parameter is the tkinter event object containing key information
            
        Returns "break" string to prevent character entry if limit reached, or None (default) to allow character entry
        """
        # Allow navigation and editing keys regardless of character count
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Tab']:
            return  # Return None to allow these keys
        
        # Get current text from description field
        current_text = self.description_text.get("1.0", tk.END)
        
        # Calculate actual character count (excluding automatic newline)
        current_length = len(current_text) - 1 if current_text.endswith('\n') else len(current_text)
        
        # If already at character limit, prevent new character entry
        if current_length >= 1000:
            return "break"  # This prevents the character from being entered
    
    def validate_inputs(self, exclude_event_id=None):
        """
        Comprehensively validate all form inputs to ensure data integrity.
        
        This method checks all form fields for:
        - Required field completion
        - Correct data formats
        - Logical constraints (e.g., end time after start time)
        - Business rules (e.g., no past dates, no double bookings)
        
        The exclude_event_id parameter is the Event ID to exclude from date conflict checking (used when editing existing events)
            
        Returns a boolean: True if all inputs are valid, False if any problems found
        """
        # Get all form values and remove leading/trailing whitespace
        name = self.name_entry.get().strip()
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        price = self.price_entry.get().strip()
        
        # Check that all required fields have been filled in
        if not name or not date or not time or not end_time:
            messagebox.showerror("Error", "Name, date, start time, and end time are required fields")
            return False
        
        # Validate event name length constraint
        if len(name) > 40:
            messagebox.showerror("Error", "Event name must be 40 characters or less")
            return False
        
        # Validate description length constraint
        description = self.description_text.get("1.0", tk.END).strip()
        if len(description) > 1000:
            messagebox.showerror("Error", "Description must be 1000 characters or less")
            return False
        
        # Validate date format using regular expression
        # Pattern: exactly 4 digits, hyphen, 2 digits, hyphen, 2 digits
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(date):
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
            return False
        
        # Validate time format using regular expression
        # Pattern: (00-19 OR 20-23):(00-59) for 24-hour format
        time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
        
        # Check start time format
        if not time_pattern.match(time):
            messagebox.showerror("Error", "Start time must be in HH:MM format (24-hour)")
            return False
            
        # Check end time format
        if not time_pattern.match(end_time):
            messagebox.showerror("Error", "End time must be in HH:MM format (24-hour)")
            return False
        
        # Validate that end time is after start time
        try:
            # Parse start time into hours and minutes
            start_hour, start_minute = map(int, time.split(':'))
            # Parse end time into hours and minutes
            end_hour, end_minute = map(int, end_time.split(':'))
            
            # Convert both times to total minutes for easy comparison
            start_minutes_total = start_hour * 60 + start_minute
            end_minutes_total = end_hour * 60 + end_minute
            
            # Check that end time is genuinely after start time
            if end_minutes_total <= start_minutes_total:
                messagebox.showerror("Error", "End time must be after start time")
                return False
                
        except ValueError:
            # This catches any errors in parsing the time values
            messagebox.showerror("Error", "Invalid time format")
            return False
        
        # Validate price is a positive number
        try:
            price_float = float(price)  # Convert string to floating point number
            if price_float < 0:         # Check for negative values
                messagebox.showerror("Error", "Price must be a positive number")
                return False
        except ValueError:
            # This catches non-numeric price entries
            messagebox.showerror("Error", "Price must be a number")
            return False
        
        # Validate that event date is not in the past
        try:
            # Parse the entered date string into a date object
            event_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            # Get today's date for comparison
            today = datetime.datetime.now().date()
            
            # Check if event date is before today
            if event_date < today:
                messagebox.showerror("Error", "Event date cannot be in the past")
                return False
                
        except ValueError:
            # This catches invalid dates (e.g., February 30th)
            messagebox.showerror("Error", "Invalid date")
            return False
        
        # Check for date conflicts with existing events
        # The venue can only host one event per day
        if exclude_event_id:
            # When editing, exclude the current event from conflict checking
            has_conflict = self.db_manager.date_has_event(date, exclude_event_id=exclude_event_id)
        else:
            # When creating new event, check all existing events
            has_conflict = self.db_manager.date_has_event(date)
            
        # Display error if date conflict found
        if has_conflict:
            messagebox.showerror(
                "Date Conflict", 
                f"An event is already scheduled on {date}.\n"
                "The venue can only host one event per day."
            )
            return False
        
        # If all validations pass, return True
        return True
    
    def get_form_data(self):
        """
        Collect and return all form data as a structured dictionary.
        
        This method extracts all user input from the form fields and
        organises it into a dictionary for easy database storage or processing.
        
        Returns a dictionary containing all form field values with appropriate data types
        """
        return {
            'name': self.name_entry.get().strip(),           # Event name as string
            'date': self.date_entry.get().strip(),           # Date as string (YYYY-MM-DD)
            'time': self.time_entry.get().strip(),           # Start time as string (HH:MM)
            'end_time': self.end_time_entry.get().strip(),   # End time as string (HH:MM)
            'price': float(self.price_entry.get().strip()),  # Price as floating point number
            'description': self.description_text.get("1.0", tk.END).strip()  # Description text
        }
    
    def populate_form(self, event_data):
        """
        Fill the form fields with existing event data for editing.
        
        This method is used when editing existing events to load their
        current values into all form fields.
        
        The event_data parameter is a dictionary containing event information to load
        """
        # Clear all existing content from form fields first
        self.name_entry.delete(0, tk.END)           # Clear name field
        self.date_entry.delete(0, tk.END)           # Clear date field
        self.time_entry.delete(0, tk.END)           # Clear start time field
        self.end_time_entry.delete(0, tk.END)       # Clear end time field
        self.price_entry.delete(0, tk.END)          # Clear price field
        self.description_text.delete("1.0", tk.END) # Clear description field
        
        # Insert event data into form fields
        # .get() method provides default empty string if key doesn't exist
        self.name_entry.insert(0, event_data.get('name', ''))
        self.date_entry.insert(0, event_data.get('date', ''))
        self.time_entry.insert(0, event_data.get('time', ''))
        self.end_time_entry.insert(0, event_data.get('end_time', ''))
        self.price_entry.insert(0, str(event_data.get('price', '')))  # Convert number to string
        
        # Handle description separately as it might be empty
        description = event_data.get('description', '')
        if description:
            # Insert description at the beginning of text widget
            self.description_text.insert("1.0", description)
        
        # Update character count displays to reflect loaded content
        self.update_name_char_count()
        self.update_description_char_count()
    
    def set_default_values(self):
        """
        Set sensible default values for a new event creation.
        
        This method pre-fills form fields with commonly used values to speed up event creation and provide guidance to users.
        """
        # Set default date to tomorrow (avoids past date validation issues)
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.date_entry.insert(0, tomorrow)
        
        # Set default times for typical evening event
        self.time_entry.insert(0, "19:00")   # 7:00 PM start time
        self.end_time_entry.insert(0, "21:00")  # 9:00 PM end time
        
        # Set default price (typical ticket cost)
        self.price_entry.insert(0, "25.00")