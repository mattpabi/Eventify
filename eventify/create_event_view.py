import tkinter as tk
from tkinter import messagebox
from base_event_view import BaseEventView


class CreateEventView(BaseEventView):
    def __init__(self, root, db_manager, back_callback=None):
        """
        Initialise the event creation view with all necessary components.
        
        Sets up the complete interface for creating new events, including all form fields, validation, and button controls. Inherits common functionality from the parent BaseEventView class.
        """
        # Initialise the parent class with appropriate title for event creation
        # This sets up all the common form elements and layout
        super().__init__(root, db_manager, back_callback, title="Create New Event")
        
        # Call the method that creates all the form elements and layout
        # This includes input fields, labels, and validation setup
        self.setup_ui()
        
        # Set default values for new event creation (empty fields with sensible defaults)
        # This ensures the form starts in a clean, ready-to-use state
        self.set_default_values()
    
    def create_button_section(self, parent):
        """
        Create the button section specific to event creation.
        
        Overrides the parent method to provide buttons appropriate for creating new events (Create Event and Clear Form) rather than editing existing ones.
        
        The parent parameter is the parent widget to contain the button section
            
        Returns button_frame, which is the frame containing all the created buttons
        """
        # Call parent method to create the basic button frame structure
        button_frame = super().create_button_section(parent)
        
        # Create Event button - primary action button for submitting the form
        create_button = tk.Button(
            button_frame,  # Place button in the button frame
            text="Create Event",  # Button label text
            command=self.create_event,  # Function to call when button is clicked
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        create_button.pack(side=tk.LEFT, padx=(0, 10))  # Position on left with right padding
        
        # Clear Form button - secondary action button for resetting the form
        clear_button = tk.Button(
            button_frame,  # Place button in the button frame
            text="Clear Form",  # Button label text
            command=self.clear_form,  # Function to call when button is clicked
            font=("Arial", 12),
            width=10,
            height=2
        )
        clear_button.pack(side=tk.LEFT)  # Position next to create button
        
        return button_frame  # Return the frame for any additional configuration
    
    def create_event(self):
        """
        Create a new event with the information provided in the form.
        
        This method handles the complete event creation process including:
        - Input validation to ensure data quality
        - Data extraction from form fields
        - Database insertion through the database manager
        - User feedback via success or error messages
        - Navigation back to dashboard upon success
        
        Only proceeds with creation if all validation checks pass successfully.
        """
        # First check if all inputs are valid using inherited validation method
        # This includes checking for required fields, date formats, time formats, etc.
        if not self.validate_inputs():
            return  # Exit early if validation fails - error messages already shown
        
        # Get all values from the form fields using inherited method
        # This extracts and formats all user input into a structured dictionary
        form_data = self.get_form_data()
        
        # Save the event to the database using the database manager
        # The create_event method returns the new event's ID if successful, None if failed
        event_id = self.db_manager.create_event(
            name=form_data['name'],              # Event title/name
            description=form_data['description'], # Detailed event description
            date=form_data['date'],              # Event date in YYYY-MM-DD format
            time=form_data['time'],              # Start time in HH:MM format
            end_time=form_data['end_time'],      # End time in HH:MM format
            price=form_data['price']             # Ticket price as decimal number
        )
        
        # Check if the event was successfully created by examining return value
        if event_id:
            # Show success message to user with event name confirmation
            messagebox.showinfo("Success", f"Event '{form_data['name']}' created successfully!")
            
            # Return to the main dashboard if callback function was provided
            if self.back_callback:
                self.back_callback()  # Call the function to navigate back
        else:
            # Show error message if database insertion failed
            messagebox.showerror("Error", "Failed to create event")
    
    def clear_form(self):
        """
        Reset all form fields to their default values.
        
        This method provides a quick way for users to clear the entire form and start over.
        
        Particularly useful for users when creating multiple similar events or when wanting to correct multiple input errors.
        
        Clears all text inputs and resets character counters to ensure the form returns to its initial state.
        """
        # Clear all single-line text entry fields by deleting all content
        self.name_entry.delete(0, tk.END)      # Clear event name field
        self.date_entry.delete(0, tk.END)      # Clear date field
        self.time_entry.delete(0, tk.END)      # Clear start time field
        self.end_time_entry.delete(0, tk.END)  # Clear end time field
        self.price_entry.delete(0, tk.END)     # Clear price field
        
        # Clear multi-line text area by deleting from start ("1.0") to end
        # Text widgets use "line.character" addressing, so "1.0" means line 1, character 0
        self.description_text.delete("1.0", tk.END)  # Clear description text area
        
        # Reset all fields to their default values using inherited method
        # This ensures consistent starting state for new event creation
        self.set_default_values()
        
        # Update the character count displays to reflect cleared fields
        # These methods recalculate and display current character usage
        self.update_name_char_count()         # Update name field character counter
        self.update_description_char_count()  # Update description field character counter