import tkinter as tk  # Import main GUI library for creating interface elements
from tkinter import messagebox  # Import for displaying popup messages to user
from base_event_view import BaseEventView  # Import parent class with shared form functionality


class EditEventView(BaseEventView):  
    def __init__(self, root, db_manager, event_id, back_callback=None):
        """
        Initialise the event editing view with existing event data.
        
        Loads the specified event from the database and sets up the complete interface for editing. If the event doesn't exist, displays an error and returns to the previous screen.
        """
        # Store the event ID for use throughout the editing process
        self.event_id = event_id
        
        # Load the existing event data from the database using the provided ID
        # This returns a dictionary with all event details or None if not found
        self.event = db_manager.get_event_by_id(event_id)
        
        # Check if the event exists in the database before proceeding
        if not self.event:
            # Display error message to user if event cannot be found
            messagebox.showerror("Error", f"Event with ID {event_id} not found")
            
            # Return to previous screen if callback function was provided
            if back_callback:
                back_callback()  # Navigate back to prevent user getting stuck
            return  # Exit initialisation early to prevent further setup
        
        # Initialise the parent class with event-specific title showing event name
        # This sets up all the common form elements and layout
        super().__init__(root, db_manager, back_callback, 
                        title=f"Edit Event: {self.event['name']}")
        
        # Call the method that creates all the form elements and layout
        # This includes input fields, labels, and validation setup
        self.setup_ui()
        
        # Populate the form with existing event data for editing
        # This fills all form fields with current values from the database
        self.populate_form(self.event)
    
    def create_button_section(self, parent):
        """
        Create the button section specific to event editing.
        
        Overrides the parent method to provide buttons appropriate for editing existing events (Save Changes and Cancel) rather than creating new ones.
        
        The parent parameter is the parent widget to contain the button section.
            
        Returns button_frame, which is the frame containing all the created buttons.
        """
        # Call parent method to create the basic button frame structure
        button_frame = super().create_button_section(parent)
        
        # Save Changes button - primary action button for updating the event
        save_button = tk.Button(
            button_frame,  # Place button in the button frame
            text="Save Changes",  # Button label text indicating update action
            command=self.save_changes,  # Function to call when button is clicked
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))  # Position on left with right padding
        
        # Cancel button - secondary action button for discarding changes
        cancel_button = tk.Button(
            button_frame,  # Place button in the button frame
            text="Cancel",  # Button label text indicating discard action
            # Use back_callback if provided, otherwise quit the frame
            command=self.back_callback if self.back_callback else self.frame.quit,
            font=("Arial", 12),
            width=10,
            height=2
        )
        cancel_button.pack(side=tk.LEFT)  # Position next to save button
        
        return button_frame  # Return the frame for any additional configuration
    
    def save_changes(self):
        """
        Save the modified event information to the database.
        
        This method handles the complete event update process including:
        - Input validation with special handling for the current event
        - Data extraction from form fields
        - Database update through the database manager
        - User feedback via success or error messages
        - Navigation back to dashboard upon success
        
        Only proceeds with updates if all validation checks pass successfully.
        
        The validation excludes the current event from date conflict checks to allow users to save changes without false conflict warnings.
        """
        # Check if all inputs are valid, excluding current event from date conflict check
        # This prevents the system from flagging the current event as conflicting with itself
        if not self.validate_inputs(exclude_event_id=self.event_id):
            return  # Exit early if validation fails - error messages already shown
        
        # Get all values from the form fields using inherited method
        # This extracts and formats all user input into a structured dictionary
        form_data = self.get_form_data()
        
        # Set fixed venue and capacity values (these don't change for this system)
        # These are constant for all events in this particular theatre booking system
        venue = "Castle Hill High School auditorium"  # Fixed venue location
        capacity = 550  # Maximum number of seats available
        
        # Update the event in the database using the database manager
        # The update_event method returns True if successful, False if failed
        success = self.db_manager.update_event(
            event_id=self.event_id,              # Which event to update
            name=form_data['name'],              # Updated event title/name
            description=form_data['description'], # Updated detailed description
            date=form_data['date'],              # Updated event date in YYYY-MM-DD format
            time=form_data['time'],              # Updated start time in HH:MM format
            end_time=form_data['end_time'],      # Updated end time in HH:MM format
            venue=venue,                         # Fixed venue (required by database)
            capacity=capacity,                   # Fixed capacity (required by database)
            price=form_data['price']             # Updated ticket price as decimal
        )
        
        # Check if the event was successfully updated by examining return value
        if success:
            # Show success message to user with event name confirmation
            messagebox.showinfo("Success", f"Event '{form_data['name']}' updated successfully!")
            
            # Return to the main dashboard if callback function was provided
            if self.back_callback:
                self.back_callback()  # Call the function to navigate back
        else:
            # Show error message if database update failed
            messagebox.showerror("Error", "Failed to update event")