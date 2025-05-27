import tkinter as tk
import tkinter.messagebox as messagebox
import os

class StageView: 
    def __init__(self, root, db_manager, event_id, username, back_callback=None):
        """
        Initialise the stage view with necessary parameters.
        
        - The event_id parameter is the ID of the event to edit
        - The back_callback parameter is the function to call when user wants to go back
        """
        # Store database manager for later use in seat operations
        self.db_manager = db_manager
        # Store reference to the main window
        self.root = root

        # Set the minimum and maximum window sizes to ensure proper display
        root.minsize(1280, 720)  # Minimum size for readable interface
        root.maxsize(1920, 1080)  # Maximum size to prevent oversizing
        self.root.resizable(True, True)  # Allow user to resize window

        # Store event_id and username as class attributes for easy access throughout methods
        self.event_id = event_id
        self.current_username = username
        self.back_callback = back_callback  # Function to return to previous screen
        
        # Get event details from database using the event ID
        self.event = self.db_manager.get_event_by_id(self.event_id)
        # Set window title to include event name if event exists
        if self.event:
            self.root.title(f"Seat Selection - {self.event['name']}")

        # Define the theatre layout with row labels and number of seats per row
        # Format: (row_letter, number_of_seats_in_row)
        self.rows = [
            ('A', 24), ('B', 24),  # Front rows with fewer seats
            ('C', 28), ('D', 28),  # Slightly more seats
            ('E', 32), ('F', 32),  # Middle section
            ('G', 36), ('H', 36), ('I', 36), ('J', 36), ('K', 36), ('L', 36),  # Back section with most seats
            ('M', 34), ('N', 32)   # Very back rows
        ]
        # Font styling for row labels
        self.label_font = ("Arial", 7, "bold")

        # Load reserved seats from database - seats taken by other users
        reserved_seats_list = self.db_manager.get_reserved_seats(self.event_id, self.current_username)
        self.reserved_seats = set(reserved_seats_list)  # Convert to set for faster lookup

        # Load current user's reserved seats from database
        user_reserved_seats_list = self.db_manager.get_user_reserved_seats(self.event_id, self.current_username)
        self.user_reserved_seats = set(user_reserved_seats_list)  # Convert to set for faster lookup

        # Get user's current reservation count to enforce 4-seat limit
        self.user_reservation_count = self.db_manager.get_user_reservation_count(self.event_id, self.current_username)

        # Initialise sets to track user interactions
        self.selected_seats = set()  # Seats currently selected but not yet booked
        self.seat_buttons = {}  # Dictionary to store seat button references by seat ID

        # Execute setup methods in correct order
        self.load_images()  # Load seat images first
        self.setup_layout()  # Create the main interface layout
        self.initialize_seats()  # Create all seat buttons
        self.update_reserved_display()  # Show user's current reservations
        self.update_selected_display()  # Show currently selected seats

    def load_images(self):
        """
        Load all seat images from the images folder.
        Each seat state has a different image: available, selected, reserved, user's reservation.
        """
        try:
            # Get the directory path where this script is located
            file_path = os.path.dirname(os.path.abspath(__file__))
            
            # Build full paths to each image file
            img_seat = os.path.join(file_path, "images/seat.png")  # Available seat
            img_seat_selected = os.path.join(file_path, "images/seat_selected.png")  # User selected
            img_seat_reserved = os.path.join(file_path, "images/seat_reserved.png")  # Taken by others
            img_seat_user_reserved = os.path.join(file_path, "images/seat_user_reserved.png")  # User's bookings
            
            # Load images and scale them down by factor of 21 to fit buttons
            self.seat_img = tk.PhotoImage(file=img_seat).subsample(21, 21)
            self.seat_img_selected = tk.PhotoImage(file=img_seat_selected).subsample(21, 21)
            self.seat_img_reserved = tk.PhotoImage(file=img_seat_reserved).subsample(21, 21)
            self.seat_img_user_reserved = tk.PhotoImage(file=img_seat_user_reserved).subsample(21, 21)
        except Exception as e:
            # Print error message if images can't be loaded
            print("Error loading images:", e)
            # Set all images to None if loading fails
            self.seat_img = self.seat_img_selected = self.seat_img_reserved = self.seat_img_user_reserved = None

    def setup_layout(self):
        """
        Create the main layout structure with proper spacing and organisation.
        Uses a grid system with three main columns: left margin, centre content, right info panel.
        """
        # Main container frame that expands to fill the entire window
        self.master = tk.Frame(self.root)
        self.master.pack(expand=True, fill='both')  # Expand in all directions
        
        # Configure the master frame with a 3-column grid layout
        self.master.grid_columnconfigure(0, weight=1)   # Left margin - expands to centre content
        self.master.grid_columnconfigure(1, weight=10)  # Centre content - gets most space
        self.master.grid_columnconfigure(2, weight=3)   # Right panel - fixed proportion
        
        # Configure rows with different weights and minimum sizes
        self.master.grid_rowconfigure(0, weight=1)      # Top margin - flexible space
        self.master.grid_rowconfigure(1, minsize=50)    # Event info row - fixed height
        self.master.grid_rowconfigure(2, minsize=50)    # Stage row - fixed height
        self.master.grid_rowconfigure(3, weight=1)      # Space before seats - flexible
        self.master.grid_rowconfigure(4, weight=5)      # Seats content - main area gets most space
        self.master.grid_rowconfigure(5, weight=1)      # Bottom margin - flexible space
        
        # Header frame - contains back button and event information
        header_frame = tk.Frame(self.master)
        header_frame.grid(row=1, column=1, sticky='ew')  # Stick to east-west (full width)
        header_frame.grid_columnconfigure(0, weight=0)  # Back button - fixed width
        header_frame.grid_columnconfigure(1, weight=1)  # Event info - expands to fill
        
        # Add back button if callback function was provided
        if self.back_callback:
            back_button = tk.Button(
                header_frame, 
                text="Back to Dashboard",  # Button text
                command=self.back_callback,  # Function to call when clicked
                font=("Arial", 10),  # Font styling
                width=16  # Fixed width in characters
            )
            # Position button in top-left with padding
            back_button.grid(row=0, column=0, pady=10, padx=10, sticky='w')

        # Display event information if event data exists
        if hasattr(self, 'event') and self.event:
            # Format event details into readable string
            event_info = f"{self.event['name']} - {self.event['date']} from {self.event['time']} to {self.event['end_time']}"
            # Create label with event information
            event_label = tk.Label(header_frame, text=event_info, font=("Arial", 12, "bold"))
            # Position label to fill remaining header space
            event_label.grid(row=0, column=1, pady=10, sticky='ew')

        # Stage area - visual representation of the theatre stage
        self.stage = tk.Label(
            self.master, 
            text="STAGE",  # Display text
            bg="gold",  # Gold background colour
            font=("Arial", 16, "bold"),  # Large bold font
            width=50,  # Width in characters
            height=3   # Height in lines
        )
        # Position stage above seating area with bottom padding
        self.stage.grid(row=2, column=1, pady=(0, 20), sticky='ew')

        # Create a scrollable canvas container for the seating area
        # This allows handling of large seat layouts that might not fit on screen
        self.canvas_container = tk.Frame(self.master)
        self.canvas_container.grid(row=4, column=1, sticky='nsew')  # Fill entire cell
        self.canvas_container.grid_columnconfigure(0, weight=1)  # Canvas column expands
        self.canvas_container.grid_rowconfigure(0, weight=1)     # Canvas row expands
        
        # Add canvas widget for scrollable seat area
        self.canvas = tk.Canvas(self.canvas_container)
        self.canvas.grid(row=0, column=0, sticky='nsew')  # Fill container
        
        # Create scrollbars for canvas navigation
        v_scrollbar = tk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(self.canvas_container, orient="horizontal", command=self.canvas.xview)
        # Link scrollbars to canvas
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Position scrollbars (only show when needed)
        v_scrollbar.grid(row=0, column=1, sticky='ns')   # Vertical scrollbar on right
        h_scrollbar.grid(row=1, column=0, sticky='ew')   # Horizontal scrollbar on bottom
            
        # Frame inside canvas to hold all seat buttons
        self.frame = tk.Frame(self.canvas)
        # Create window inside canvas to hold the frame
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        
        # Bind events to update scrolling when content changes
        self.frame.bind("<Configure>", self.on_frame_configure)      # When frame size changes
        self.canvas.bind("<Configure>", self.on_canvas_configure)    # When canvas size changes
        
        # Create the information panel on the right side
        self.create_info_panel()

    def on_frame_configure(self, event):
        """
        Update the scroll region when the frame content changes size.
        This ensures scrollbars work correctly with the seat layout.
        """
        # Update scroll region to encompass all content in the frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """
        Centre the seat layout when the canvas is resized.
        This keeps seats centred even when window is resized.
        """
        # Get current canvas width from the resize event
        canvas_width = event.width
        # Get required width of the frame containing seats
        frame_width = self.frame.winfo_reqwidth()
        
        # Centre the frame in the canvas if it's smaller than canvas
        if frame_width < canvas_width:
            # Calculate centre position
            new_x = (canvas_width - frame_width) / 2
            # Move the frame to centre position
            self.canvas.coords(self.canvas_window, new_x, 0)
        else:
            # If frame is larger than canvas, keep it at left edge
            self.canvas.coords(self.canvas_window, 0, 0)

    def initialize_seats(self):
        """
        Create all seat buttons according to the theatre layout.
        Each row has seats split into left and right sections with an aisle in the middle.
        """
        # Clear any existing seat buttons
        self.seat_buttons = {}
        
        # Calculate centre column position based on largest row
        max_seats = max(row_info[1] for row_info in self.rows)  # Find row with most seats
        center_col = max_seats + 5  # Add extra space for centring
        
        # Loop through each row in the theatre layout
        for r, (row_label, total_seats) in enumerate(self.rows):
            # Split seats into left and right sections (left gets extra seat if odd number)
            left_count = total_seats // 2      # Integer division for left side
            right_count = total_seats - left_count  # Remaining seats for right side

            # Create row label on the left side
            tk.Label(
                self.frame, 
                text=row_label,  # Row letter (A, B, C, etc.)
                font=self.label_font, 
                width=2, 
                anchor='e'  # Right-align text
            ).grid(row=r, column=center_col - left_count - 1, padx=0, pady=0, sticky='e')

            # Create left section seats
            for c in range(left_count):
                col = center_col - left_count + c  # Calculate column position
                seat_num = c + 1  # Seat numbers start from 1
                seat_id = (row_label, seat_num)  # Tuple identifier for seat
                self.create_seat_button(r, col, seat_id)  # Create the actual button

            # Create middle aisle space
            tk.Label(self.frame, text="", width=2).grid(row=r, column=center_col)

            # Create right section seats
            for c in range(right_count):
                col = center_col + 1 + c  # Calculate column position after aisle
                seat_num = left_count + c + 1  # Continue seat numbering from left section
                seat_id = (row_label, seat_num)  # Tuple identifier for seat
                self.create_seat_button(r, col, seat_id)  # Create the actual button

            # Create row label on the right side
            tk.Label(
                self.frame, 
                text=row_label,  # Same row letter
                font=self.label_font, 
                width=2, 
                anchor='w'  # Left-align text
            ).grid(row=r, column=center_col + right_count + 1, padx=0, pady=0, sticky='w')

    def create_seat_button(self, row, col, seat_id):
        """
        Create a single seat button with appropriate appearance and behaviour.
        The button's image and functionality depend on the seat's current status.
        """
        # Determine button appearance and behaviour based on seat status
        if seat_id in self.reserved_seats:
            # Seat is taken by another user
            btn_img = self.seat_img_reserved  # Grey/unavailable image
            state = "disabled"  # Cannot be clicked
            command = None  # No action when clicked
        elif seat_id in self.user_reserved_seats:
            # Seat is reserved by current user
            btn_img = self.seat_img_user_reserved  # User's reservation image
            state = "normal"  # Can be clicked
            command = lambda sid=seat_id: self.cancel_seat_reservation(sid)  # Click to cancel
        else:
            # Seat is available
            btn_img = self.seat_img  # Available seat image
            state = "normal"  # Can be clicked
            command = lambda sid=seat_id: self.toggle_seat(sid)  # Click to select/deselect

        # Create the button widget with styling
        btn = tk.Button(
            self.frame, 
            image=btn_img,  # Seat image
            width=24, height=24,  # Fixed size
            padx=0, pady=0,  # No internal padding
            borderwidth=0,  # No border
            highlightthickness=0,  # No highlight border
            relief="flat",  # Flat appearance
            takefocus=0,  # Don't receive keyboard focus
            bg=self.frame["bg"],  # Match frame background
            activebackground=self.frame["bg"],  # Same background when clicked
            state=state  # Set enabled/disabled state
        )

        # Add click command if one was defined
        if command:
            btn.config(command=command)

        # Position button in the grid
        btn.grid(row=row, column=col, padx=0, pady=0)
        # Store button reference and selection state
        self.seat_buttons[seat_id] = {"button": btn, "selected": seat_id in self.selected_seats}

    def create_seat_legend(self, parent):
        """
        Create a visual legend showing what each seat image means.
        This helps users understand the different seat states.
        """
        # Create a labelled frame for the legend
        legend_frame = tk.LabelFrame(parent, text="Seat Legend", font=("Arial", 11, "bold"), padx=10, pady=10)
        legend_frame.pack(fill='x', expand=False, pady=(15, 0))
        
        # Define legend items with image and description
        legends = [
            (self.seat_img, "Available"),
            (self.seat_img_selected, "Selected"),
            (self.seat_img_reserved, "Unavailable"),
            (self.seat_img_user_reserved, "Your Reservation (Click to Cancel)")
        ]
        
        # Arrange legend items in a 2-column grid layout
        for i, (img, text) in enumerate(legends):
            row = i // 2  # Calculate row (0 or 1)
            col = i % 2   # Calculate column (0 or 1)
            
            # Create container for each legend item
            legend_item = tk.Frame(legend_frame)
            legend_item.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            # Add image label
            label_img = tk.Label(legend_item, image=img)
            label_img.pack(side='left', padx=(0, 5))
            
            # Add text description
            label_text = tk.Label(legend_item, text=text, font=("Arial", 9))
            label_text.pack(side='left')
        
        # Store reference to images to prevent garbage collection
        self.legend_images = [img for img, _ in legends]

    def create_info_panel(self):
        """
        Create the information panel on the right side of the interface.
        Shows reservation limits, user's bookings, selected seats, and booking controls.
        """
        # Right side panel container
        right_panel = tk.Frame(self.master, bd=0)  # No border
        # Position panel spanning multiple rows on the right
        right_panel.grid(row=1, column=2, rowspan=4, sticky='nsew', padx=10, pady=10)
        
        # Add header for the information panel
        info_header = tk.Label(right_panel, text="Seat Information", font=("Arial", 14, "bold"))
        info_header.pack(anchor='n', pady=(0, 15))  # Anchor to north (top)
        
        # Display reservation limit information
        self.reservation_limit_label = tk.Label(
            right_panel, 
            text=f"Reservation Limit: {self.user_reservation_count}/4 seats",  # Show current count
            font=("Arial", 11, "bold")
        )
        self.reservation_limit_label.pack(anchor='n', pady=(0, 15))
        
        # Section for showing user's already reserved seats
        self.reserved_frame = tk.LabelFrame(
            right_panel, 
            text="Your Reserved Seats", 
            font=("Arial", 11, "bold"), 
            padx=10, pady=10
        )
        self.reserved_frame.pack(fill='x', expand=False, pady=(0, 15))

        # Listbox to display reserved seats
        self.reserved_listbox = tk.Listbox(
            self.reserved_frame, 
            height=6, width=20,  # Size settings
            exportselection=False,  # Prevent selection conflicts
            font=("Arial", 10)
        )
        self.reserved_listbox.pack(side='left', fill='both', expand=True)
        
        # Scrollbar for reserved seats list
        reserved_scroll = tk.Scrollbar(self.reserved_frame, orient='vertical', command=self.reserved_listbox.yview)
        reserved_scroll.pack(side='right', fill='y')
        self.reserved_listbox.config(yscrollcommand=reserved_scroll.set)  # Link scrollbar to listbox
        
        # Section for showing currently selected seats
        self.selected_frame = tk.LabelFrame(
            right_panel, 
            text="Your Selected Seats", 
            font=("Arial", 11, "bold"), 
            padx=10, pady=10
        )
        self.selected_frame.pack(fill='x', expand=False, pady=(0, 15))

        # Listbox to display selected seats
        self.selected_listbox = tk.Listbox(
            self.selected_frame, 
            height=6, width=20,  # Size settings
            exportselection=False,  # Prevent selection conflicts
            font=("Arial", 10)
        )
        self.selected_listbox.pack(side='left', fill='both', expand=True)
        
        # Scrollbar for selected seats list
        selected_scroll = tk.Scrollbar(self.selected_frame, orient='vertical', command=self.selected_listbox.yview)
        selected_scroll.pack(side='right', fill='y')
        self.selected_listbox.config(yscrollcommand=selected_scroll.set)  # Link scrollbar to listbox

        # Booking section with pricing and reserve button
        booking_frame = tk.LabelFrame(right_panel, text="Booking", font=("Arial", 11, "bold"), padx=10, pady=10)
        booking_frame.pack(fill='x', expand=False)
        
        # Display price information if event data is available
        if hasattr(self, 'event') and self.event:
            # Show price per seat
            price_label = tk.Label(booking_frame, text=f"Price per seat: £{self.event['price']:.2f}", font=("Arial", 10))
            price_label.pack(anchor='w', pady=(0, 10))
            
            # Label for total price (updated when seats are selected)
            self.total_price_label = tk.Label(
                booking_frame, 
                text="Total to be paid upon entry: £0.00", 
                font=("Arial", 10, "bold")
            )
            self.total_price_label.pack(anchor='w', pady=(0, 15))
        
        # Button to confirm seat reservations
        self.book_button = tk.Button(
            booking_frame, 
            text="Reserve Selected Seats", 
            font=("Arial", 11, "bold"),
            state='disabled',  # Initially disabled until seats are selected
            command=self.reserve_selected_seats,  # Function to call when clicked
            width=18, height=2  # Button size
        )
        self.book_button.pack(pady=5)
        
        # Add the seat legend at the bottom
        self.create_seat_legend(right_panel)

    def update_reserved_display(self):
        """
        Update the display of user's currently reserved seats.
        Refreshes the listbox and reservation count label.
        """
        # Clear existing items from the listbox
        self.reserved_listbox.delete(0, tk.END)
        
        # Add user's reserved seats to the listbox
        if self.user_reserved_seats:
            # Sort seats by row letter then seat number for consistent display
            for row, num in sorted(self.user_reserved_seats):
                self.reserved_listbox.insert(tk.END, f"{row}{num}")  # Format as "A1", "B5", etc.
        else:
            # Show message if no seats are reserved
            self.reserved_listbox.insert(tk.END, "No reserved seats.")
        
        # Update reservation limit label with current count
        self.user_reservation_count = self.db_manager.get_user_reservation_count(self.event_id, self.current_username)
        self.reservation_limit_label.config(text=f"Reservation Limit: {self.user_reservation_count}/4 seats")

    def update_selected_display(self):
        """
        Update the display of currently selected seats and total price.
        Also controls whether the booking button is enabled.
        """
        # Clear existing items from the selected seats listbox
        self.selected_listbox.delete(0, tk.END)
        
        # Check if any seats are currently selected
        if self.selected_seats:
            # Add selected seats to the listbox in sorted order
            for row, num in sorted(self.selected_seats):
                self.selected_listbox.insert(tk.END, f"{row}{num}")  # Format as "A1", "B5", etc.
            
            # Check if booking these seats would exceed the 4-seat limit
            remaining_slots = 4 - self.user_reservation_count  # Calculate remaining capacity
            if len(self.selected_seats) <= remaining_slots:
                self.book_button.config(state='normal')  # Enable booking button
            else:
                self.book_button.config(state='disabled')  # Disable if over limit
            
            # Update total price display if event information is available
            if hasattr(self, 'event') and self.event and hasattr(self, 'total_price_label'):
                total = len(self.selected_seats) * self.event['price']  # Calculate total cost
                self.total_price_label.config(text=f"Total to be paid upon entry: £{total:.2f}")
        else:
            # No seats selected - show appropriate message and disable booking
            self.selected_listbox.insert(tk.END, "No seats selected.")
            self.book_button.config(state='disabled')  # Disable booking button
            
            # Reset total price display
            if hasattr(self, 'total_price_label'):
                self.total_price_label.config(text="Total to be paid upon entry: £0.00")

    def toggle_seat(self, seat_id):
        """
        Toggle the selection state of an available seat.
        Changes between selected and unselected, with visual feedback.
        """
        # Get button data for this seat
        btn_data = self.seat_buttons.get(seat_id)
        if not btn_data:
            return  # Exit if seat button doesn't exist
        
        # Get button widget and current selection state
        btn = btn_data["button"]
        selected = btn_data["selected"]
        
        # Check if selecting this seat would exceed the 4-seat limit
        if not selected and self.user_reservation_count + len(self.selected_seats) >= 4:
            # Show warning message if limit would be exceeded
            messagebox.showwarning("Reservation Limit", 
                                  f"You can only reserve a maximum of 4 seats per event.")
            return  # Exit without selecting the seat
        
        # Toggle the seat selection
        if selected:
            # Deselect the seat
            btn.config(image=self.seat_img)  # Change to available seat image
            btn_data["selected"] = False  # Update selection state
            self.selected_seats.discard(seat_id)  # Remove from selected set
        else:
            # Select the seat
            btn.config(image=self.seat_img_selected)  # Change to selected seat image
            btn_data["selected"] = True  # Update selection state
            self.selected_seats.add(seat_id)  # Add to selected set
        
        # Update the display to show current selections
        self.update_selected_display()

    def cancel_seat_reservation(self, seat_id):
        """
        Cancel a seat reservation that belongs to the current user.
        Shows confirmation dialog before cancelling.
        """
        # Check if this seat is actually reserved by the user
        if seat_id not in self.user_reserved_seats:
            return  # Exit if seat is not user's reservation
        
        # Get seat details for display
        row, num = seat_id
        seat_label = f"{row}{num}"  # Format as "A1", "B5", etc.
        
        # Ask user for confirmation before cancelling
        confirm = messagebox.askyesno(
            "Cancel Reservation", 
            f"Are you sure you want to cancel your reservation for seat {seat_label}?"
        )
        
        # Proceed with cancellation if user confirmed
        if confirm:
            # Attempt to cancel the reservation in the database
            success = self.db_manager.cancel_reservation(
                self.current_username, self.event_id, row, num
            )
            
            # Handle the result of the cancellation attempt
            if success:
                # Show success message
                messagebox.showinfo("Reservation Cancelled", 
                                   f"Your reservation for seat {seat_label} has been cancelled.")
                # Update local data structures
                self.user_reserved_seats.remove(seat_id)  # Remove from user's reservations
                self.update_reserved_display()  # Refresh the reserved seats display
                self.refresh_seat_buttons()  # Update all seat button states
            else:
                # Show error message if cancellation failed
                messagebox.showerror("Error", f"Failed to cancel reservation for seat {seat_label}.")

    def refresh_seat_buttons(self):
        """
        Refresh all seat buttons by reloading data from database and recreating buttons.
        This ensures the display is consistent with the current database state.
        """
        # Re-fetch reserved seats data from database
        reserved_seats_list = self.db_manager.get_reserved_seats(self.event_id, self.current_username)
        self.reserved_seats = set(reserved_seats_list)  # Convert to set
        
        # Re-fetch user's reserved seats from database
        user_reserved_seats_list = self.db_manager.get_user_reserved_seats(self.event_id, self.current_username)
        self.user_reserved_seats = set(user_reserved_seats_list)  # Convert to set
        
        # Destroy all existing seat buttons to recreate them
        for seat_id, seat_data in self.seat_buttons.items():
            if "button" in seat_data:
                seat_data["button"].destroy()  # Remove button from interface
        
        # Clear the seat buttons dictionary
        self.seat_buttons.clear()
        # Recreate all seat buttons with updated states
        self.initialize_seats()

    def reserve_selected_seats(self):
        """
        Reserve all currently selected seats for the user.
        Validates seat count limits and handles booking confirmation.
        """
        # Get list of seats to reserve
        seats_to_reserve = list(self.selected_seats)
        
        # Check if any seats are selected
        if not seats_to_reserve:
            messagebox.showwarning("No Seats Selected", "Please select at least one seat to book.")
            return  # Exit if no seats selected
        
        # Check if adding these seats would exceed the 4-seat limit
        total_seats_after = self.user_reservation_count + len(seats_to_reserve)
        if total_seats_after > 4:
            # Calculate how many more seats the user can book
            remaining_seats = 4 - self.user_reservation_count
            messagebox.showwarning(
                "Reservation Limit Exceeded", 
                f"You can only reserve a maximum of 4 seats per event. You have {self.user_reservation_count} "
                f"seats already reserved. Please select no more than {remaining_seats} additional seats."
            )
            return  # Exit without booking

        # Attempt to reserve seats in the database
        result = self.db_manager.reserve_seats(self.current_username, self.event_id, seats_to_reserve)

        # Handle the booking result
        if result['success']:
            # Create readable list of successfully booked seats
            booked_seats = ', '.join([f"{row}{num}" for row, num in result['reserved']])
            messagebox.showinfo("Booking Successful", f"You have reserved seats: {booked_seats}\n\n Go to your dashboard to save the QR Code of your reservation. Event staff will verify your QR Code upon entry.")
            
            # Update local reservation data
            self.user_reservation_count += len(result['reserved'])  # Update count
            # Refresh user's reserved seats from database
            user_reserved_seats_list = self.db_manager.get_user_reserved_seats(self.event_id, self.current_username)
            self.user_reserved_seats = set(user_reserved_seats_list)
            
            # Clear selected seats and update displays
            self.selected_seats.clear()  # Clear current selections
            self.update_reserved_display()  # Refresh reserved seats display
            self.update_selected_display()  # Refresh selected seats display
            self.refresh_seat_buttons()  # Update all seat button states
        else:
            # Handle booking failure
            failed_seats = ', '.join([f"{row}{num}" for row, num in result['failed']])
            if failed_seats:
                # Show specific seats that failed to book
                messagebox.showerror("Booking Failed", 
                                   f"Could not reserve seats: {failed_seats}. They may have been taken by another user.")
            else:
                # Show generic error message
                messagebox.showerror("Booking Failed", "There was an error booking your seats, please try again.")