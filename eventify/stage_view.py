import tkinter as tk
import tkinter.messagebox as messagebox
import os
from base_stage_view import BaseStageView


class StageView(BaseStageView):    
    def __init__(self, root, db_manager, event_id, username, back_callback=None):
        """
        Initialise the StageView with user-specific data and settings.
        """
        # Store the current user's username for personalised features
        self.current_username = username
        
        # Get all seats already reserved by any user for this event
        # This prevents double-booking and shows unavailable seats
        self.reserved_seats = set(db_manager.get_reserved_seats(event_id, username))
        
        # Get seats specifically reserved by the current user
        # These seats can be cancelled by the user
        self.user_reserved_seats = set(db_manager.get_user_reserved_seats(event_id, username))
        
        # Get current count of user's reservations to enforce 4-seat limit
        self.user_reservation_count = db_manager.get_user_reservation_count(event_id, username)
        
        # Set to track seats currently selected (but not yet reserved)
        self.selected_seats = set()

        # Call parent class constructor to set up basic stage layout
        # Must be called after setting user-specific attributes
        super().__init__(root, db_manager, event_id, back_callback, title_prefix="Seat Selection")

        # Update the display panels with current reservation data
        self.update_reserved_display()  # Show user's existing reservations
        self.update_selected_display()  # Show currently selected seats


    def load_images(self):
        """
        Load additional seat images specific to user view.
        
        Extends the parent class image loading to include images for:
        - Selected seats (highlighted for potential booking)
        - User's own reserved seats (different colour to show ownership)
        """
        # Load basic seat images from parent class first
        super().load_images()
        
        try:
            # Get the directory path where this Python file is located
            file_path = os.path.dirname(os.path.abspath(__file__))
            
            # Build full file paths for the additional seat images
            img_seat_selected = os.path.join(file_path, "images/seat_selected.png")
            img_seat_user_reserved = os.path.join(file_path, "images/seat_user_reserved.png")
            
            # Load and resize images to fit seat button size (21x21 pixels)
            self.seat_img_selected = tk.PhotoImage(file=img_seat_selected).subsample(21, 21)
            self.seat_img_user_reserved = tk.PhotoImage(file=img_seat_user_reserved).subsample(21, 21)
            
        except Exception as e:
            # If image loading fails, print error and set images to None
            # This prevents crashes if image files are missing
            print("Error loading additional images:", e)
            self.seat_img_selected = None
            self.seat_img_user_reserved = None


    def create_seat_button(self, row, col, seat_id):
        """
        Create a seat button with user-specific behaviour and appearance.
        
        Each seat button shows different states:
        - Available seats: clickable, normal appearance
        - Reserved by others: disabled, greyed out
        - User's reservations: clickable to cancel, special colour
        - Currently selected: highlighted colour
        
        Args:
            row: Grid row position for the button
            col: Grid column position for the button  
            seat_id: Tuple of (row_letter, seat_number) identifying the seat
        """
        # Determine button appearance and behaviour based on seat status
        if seat_id in self.reserved_seats:
            # Seat is reserved by someone else - show as unavailable
            btn_img = self.seat_img_reserved    # Grey/disabled appearance
            state = "disabled"                  # Cannot be clicked
            command = None                      # No action when clicked
            
        elif seat_id in self.user_reserved_seats:
            # Seat is reserved by current user - allow cancellation
            btn_img = self.seat_img_user_reserved  # Special colour for user's seats
            state = "normal"                       # Can be clicked
            command = lambda sid=seat_id: self.cancel_seat_reservation(sid)  # Cancel reservation action
            
        else:
            # Seat is available for selection
            btn_img = self.seat_img            # Normal available appearance
            state = "normal"                   # Can be clicked
            command = lambda sid=seat_id: self.toggle_seat(sid)  # Toggle selection action

        # Create the actual button widget with specified properties
        btn = tk.Button(
            self.frame,                    # Parent container for the button
            image=btn_img,                 # Image to display on button
            width=24, height=24,           # Button dimensions in pixels
            padx=0, pady=0,                # No internal padding
            borderwidth=0,                 # No border around button
            highlightthickness=0,          # No highlight border when focused
            relief="flat",                 # Flat appearance (no 3D effect)
            takefocus=0,                   # Don't receive keyboard focus
            bg=self.frame["bg"],           # Background matches parent
            activebackground=self.frame["bg"],  # Background when clicked matches parent
            state=state                    # Enable or disable based on seat status
        )
        
        # Attach the command function if one was specified
        if command:
            btn.config(command=command)
            
        # Position the button in the grid layout
        btn.grid(row=row, column=col, padx=0, pady=0)
        
        # Store button reference and selection state for later access
        self.seat_buttons[seat_id] = {
            "button": btn, 
            "selected": seat_id in self.selected_seats
        }


    def create_info_panel(self):
        """
        Create the information panel on the right side of the interface.
        
        This panel contains:
        - Reservation limit display (current/maximum seats)
        - List of user's existing reservations
        - List of currently selected seats
        - Price calculation and booking button
        - Seat legend explaining different seat colours
        """
        # Create main container for the information panel
        right_panel = tk.Frame(self.master, bd=0)  # bd=0 means no border
        right_panel.grid(row=1, column=2, rowspan=4, sticky='nsew', padx=10, pady=10)

        # Create header label for the information section
        info_header = tk.Label(
            right_panel, 
            text="Seat Information", 
            font=("Arial", 14, "bold")
        )
        info_header.pack(anchor='n', pady=(0, 15))  # Anchor to north (top) with bottom padding

        # Display current reservation count and limit
        self.reservation_limit_label = tk.Label(
            right_panel, 
            text=f"Reservation Limit: {self.user_reservation_count}/4 seats",
            font=("Arial", 11, "bold")
        )
        self.reservation_limit_label.pack(anchor='n', pady=(0, 15))

        # Create frame for displaying user's existing reservations
        self.reserved_frame = tk.LabelFrame(
            right_panel, 
            text="Your Reserved Seats", 
            font=("Arial", 11, "bold"), 
            padx=10, pady=10
        )
        self.reserved_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Create scrollable list box for reserved seats
        self.reserved_listbox = tk.Listbox(
            self.reserved_frame, 
            height=6,                    # Show 6 lines at once
            width=20,                    # 20 characters wide
            exportselection=False,       # Don't export selection to clipboard
            font=("Arial", 10)
        )
        self.reserved_listbox.pack(side='left', fill='both', expand=True)
        
        # Add vertical scrollbar for reserved seats list
        reserved_scroll = tk.Scrollbar(
            self.reserved_frame, 
            orient='vertical', 
            command=self.reserved_listbox.yview
        )
        reserved_scroll.pack(side='right', fill='y')
        self.reserved_listbox.config(yscrollcommand=reserved_scroll.set)

        # Create frame for displaying currently selected seats
        self.selected_frame = tk.LabelFrame(
            right_panel, 
            text="Your Selected Seats", 
            font=("Arial", 11, "bold"), 
            padx=10, pady=10
        )
        self.selected_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Create scrollable list box for selected seats
        self.selected_listbox = tk.Listbox(
            self.selected_frame, 
            height=6, 
            width=20, 
            exportselection=False, 
            font=("Arial", 10)
        )
        self.selected_listbox.pack(side='left', fill='both', expand=True)
        
        # Add vertical scrollbar for selected seats list
        selected_scroll = tk.Scrollbar(
            self.selected_frame, 
            orient='vertical', 
            command=self.selected_listbox.yview
        )
        selected_scroll.pack(side='right', fill='y')
        self.selected_listbox.config(yscrollcommand=selected_scroll.set)

        # Create frame for booking controls and price display
        booking_frame = tk.LabelFrame(
            right_panel, 
            text="Booking", 
            font=("Arial", 11, "bold"), 
            padx=10, pady=10
        )
        booking_frame.pack(fill='x', expand=False)
        
        # Display price information if event data is available
        if self.event:
            # Show price per individual seat
            price_label = tk.Label(
                booking_frame, 
                text=f"Price per seat: ${self.event['price']:.2f}", 
                font=("Arial", 10)
            )
            price_label.pack(anchor='w', pady=(0, 10))  # Anchor west (left)
            
            # Show total price for selected seats (updated dynamically)
            self.total_price_label = tk.Label(
                booking_frame, 
                text="Total to be paid upon entry: $0.00", 
                font=("Arial", 10, "bold")
            )
            self.total_price_label.pack(anchor='w', pady=(0, 15))

        # Create button to confirm reservation of selected seats
        self.book_button = tk.Button(
            booking_frame, 
            text="Reserve Selected Seats", 
            font=("Arial", 11, "bold"),
            state='disabled',                        # Initially disabled until seats are selected
            command=self.reserve_selected_seats,     # Function to call when clicked
            width=18, height=2                       # Button dimensions
        )
        self.book_button.pack(pady=5)

        # Create legend explaining what different seat colours mean
        self.create_seat_legend(right_panel)


    def create_seat_legend(self, parent):
        """
        Create a legend explaining the different seat states and colours.
        
        Shows users what each seat colour/image represents:
        - Available seats, selected seats, unavailable seats, user's reservations
        
        Args:
            parent: The parent widget to attach the legend to
        """
        # Create frame container for the legend
        legend_frame = tk.LabelFrame(
            parent, 
            text="Seat Legend", 
            font=("Arial", 11, "bold"), 
            padx=10, pady=10
        )
        legend_frame.pack(fill='x', expand=False, pady=(15, 0))
        
        # Define legend items: (image, description_text)
        legends = [
            (self.seat_img, "Available"),                                    # Normal available seat
            (self.seat_img_selected, "Selected"),                          # Currently selected seat
            (self.seat_img_reserved, "Unavailable"),                       # Reserved by someone else
            (self.seat_img_user_reserved, "Your Reservation (Click to Cancel)")  # User's own reservation
        ]
        
        # Create visual legend items in a 2x2 grid layout
        for i, (img, text) in enumerate(legends):
            row = i // 2  # Integer division to get row (0,0,1,1 becomes 0,0,1,1)
            col = i % 2   # Modulo to get column (0,1,2,3 becomes 0,1,0,1)
            
            # Create container for this legend item
            legend_item = tk.Frame(legend_frame)
            legend_item.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            # Add seat image
            label_img = tk.Label(legend_item, image=img)
            label_img.pack(side='left', padx=(0, 5))
            
            # Add descriptive text
            label_text = tk.Label(legend_item, text=text, font=("Arial", 9))
            label_text.pack(side='left')
        
        # Store reference to images to prevent garbage collection
        self.legend_images = [img for img, _ in legends]


    def update_reserved_display(self):
        """
        Update the display of seats that the user has already reserved.
        
        Refreshes the reserved seats list box and reservation counter
        to show current status after bookings or cancellations.
        """
        # Clear existing items from the reserved seats list
        self.reserved_listbox.delete(0, tk.END)
        
        # Add each reserved seat to the display
        if self.user_reserved_seats:
            # Sort seats by row letter then seat number for consistent display
            for row, num in sorted(self.user_reserved_seats):
                seat_label = f"{row}{num}"  # Format as "A1", "B5", etc.
                self.reserved_listbox.insert(tk.END, seat_label)
        else:
            # Show message when no seats are reserved
            self.reserved_listbox.insert(tk.END, "No reserved seats.")
        
        # Update reservation count from database (in case of changes)
        self.user_reservation_count = self.db_manager.get_user_reservation_count(
            self.event_id, self.current_username
        )
        
        # Update the reservation limit label with current count
        self.reservation_limit_label.config(
            text=f"Reservation Limit: {self.user_reservation_count}/4 seats"
        )


    def update_selected_display(self):
        """
        Update the display of currently selected seats and enable/disable booking button.
        
        Also updates the total price calculation and determines whether
        the user can proceed with booking based on seat limits.
        """
        # Clear existing items from the selected seats list
        self.selected_listbox.delete(0, tk.END)
        
        if self.selected_seats:
            # Add each selected seat to the display (sorted for consistency)
            for row, num in sorted(self.selected_seats):
                seat_label = f"{row}{num}"
                self.selected_listbox.insert(tk.END, seat_label)
            
            # Check if user can book the selected seats (within 4-seat limit)
            remaining_slots = 4 - self.user_reservation_count
            if len(self.selected_seats) <= remaining_slots:
                self.book_button.config(state='normal')    # Enable booking button
            else:
                self.book_button.config(state='disabled')  # Disable if over limit
            
            # Update total price display if event pricing is available
            if self.event and hasattr(self, 'total_price_label'):
                total = len(self.selected_seats) * self.event['price']
                self.total_price_label.config(
                    text=f"Total to be paid upon entry: ${total:.2f}"
                )
        else:
            # No seats selected - show placeholder message
            self.selected_listbox.insert(tk.END, "No seats selected.")
            self.book_button.config(state='disabled')  # Disable booking button
            
            # Reset total price to zero
            if hasattr(self, 'total_price_label'):
                self.total_price_label.config(text="Total to be paid upon entry: $0.00")


    def toggle_seat(self, seat_id):
        """
        Toggle the selection state of a seat (select/deselect).
        
        Handles the logic for selecting and deselecting available seats,
        including enforcement of the 4-seat reservation limit.
        
        Args:
            seat_id: Tuple of (row_letter, seat_number) identifying the seat
        """
        # Get the button data for this seat
        btn_data = self.seat_buttons.get(seat_id)
        if not btn_data:
            return  # Exit if seat doesn't exist
        
        btn = btn_data["button"]         # The actual button widget
        selected = btn_data["selected"]  # Current selection state
        
        # Check if selecting this seat would exceed the 4-seat limit
        if not selected and self.user_reservation_count + len(self.selected_seats) >= 4:
            messagebox.showwarning(
                "Reservation Limit", 
                "You can only reserve a maximum of 4 seats per event."
            )
            return  # Don't allow selection if limit would be exceeded
        
        # Toggle the seat's selection state
        if selected:
            # Deselect the seat
            btn.config(image=self.seat_img)          # Change to normal appearance
            btn_data["selected"] = False             # Update selection state
            self.selected_seats.discard(seat_id)     # Remove from selected set
        else:
            # Select the seat
            btn.config(image=self.seat_img_selected) # Change to selected appearance
            btn_data["selected"] = True              # Update selection state
            self.selected_seats.add(seat_id)         # Add to selected set
        
        # Update the selected seats display and booking controls
        self.update_selected_display()


    def cancel_seat_reservation(self, seat_id):
        """
        Cancel a user's existing seat reservation.
        
        Prompts for confirmation then removes the reservation from the database
        and updates the display accordingly.
        
        Args:
            seat_id: Tuple of (row_letter, seat_number) identifying the seat to cancel
        """
        # Verify that this seat is actually reserved by the user
        if seat_id not in self.user_reserved_seats:
            return  # Exit if seat isn't reserved by this user
        
        # Extract row and seat number for display
        row, num = seat_id
        seat_label = f"{row}{num}"
        
        # Ask user to confirm the cancellation
        confirm = messagebox.askyesno(
            "Cancel Reservation", 
            f"Are you sure you want to cancel your reservation for seat {seat_label}?"
        )
        
        if confirm:
            # Attempt to cancel the reservation in the database
            success = self.db_manager.cancel_reservation(
                self.current_username, self.event_id, row, num
            )
            
            if success:
                # Cancellation successful - update displays
                messagebox.showinfo(
                    "Reservation Cancelled", 
                    f"Your reservation for seat {seat_label} has been cancelled."
                )
                
                # Remove seat from user's reserved seats set
                self.user_reserved_seats.remove(seat_id)
                
                # Update display panels
                self.update_reserved_display()
                
                # Refresh all seat buttons to reflect new availability
                self.refresh_seat_buttons()
            else:
                # Cancellation failed - show error message
                messagebox.showerror(
                    "Error", 
                    f"Failed to cancel reservation for seat {seat_label}."
                )


    def refresh_seat_buttons(self):
        """
        Refresh all seat buttons with updated reservation data from database.
        
        This is called after reservations are made or cancelled to ensure
        the visual display matches the current database state.
        """
        # Get fresh reservation data from the database
        self.reserved_seats = set(self.db_manager.get_reserved_seats(
            self.event_id, self.current_username
        ))
        self.user_reserved_seats = set(self.db_manager.get_user_reserved_seats(
            self.event_id, self.current_username
        ))
        
        # Remove all existing seat buttons from the display
        for seat_id, seat_data in self.seat_buttons.items():
            if "button" in seat_data:
                seat_data["button"].destroy()  # Remove button from GUI
        
        # Clear the seat buttons dictionary
        self.seat_buttons.clear()
        
        # Recreate all seat buttons with updated data
        self.initialise_seats()


    def reserve_selected_seats(self):
        """
        Reserve the currently selected seats in the database.
        
        Performs final validation, attempts to reserve seats, and provides
        feedback to the user about the success or failure of the operation.
        """
        # Get list of seats to reserve
        seats_to_reserve = list(self.selected_seats)
        
        # Check if any seats are actually selected
        if not seats_to_reserve:
            messagebox.showwarning(
                "No Seats Selected", 
                "Please select at least one seat to book."
            )
            return
        
        # Final check against reservation limit
        total_seats_after = self.user_reservation_count + len(seats_to_reserve)
        if total_seats_after > 4:
            remaining_seats = 4 - self.user_reservation_count
            messagebox.showwarning(
                "Reservation Limit Exceeded",
                f"You can only reserve a maximum of 4 seats per event. You have {self.user_reservation_count} "
                f"seats already reserved. Please select no more than {remaining_seats} additional seats."
            )
            return
        
        # Attempt to reserve the selected seats in the database
        result = self.db_manager.reserve_seats(
            self.current_username, self.event_id, seats_to_reserve
        )
        
        if result['success']:
            # Reservation successful
            # Create comma-separated list of successfully reserved seats
            booked_seats = ', '.join([f"{row}{num}" for row, num in result['reserved']])
            
            # Show success message with instructions
            messagebox.showinfo(
                "Booking Successful", 
                f"You have reserved seats: {booked_seats}\n\n"
                f"Go to your dashboard to save the QR Code of your reservation. "
                f"Event staff will verify your QR Code upon entry."
            )
            
            # Update local data to reflect the new reservations
            self.user_reservation_count += len(result['reserved'])
            self.user_reserved_seats = set(self.db_manager.get_user_reserved_seats(
                self.event_id, self.current_username
            ))
            
            # Clear the selected seats since they're now reserved
            self.selected_seats.clear()
            
            # Update all display panels
            self.update_reserved_display()
            self.update_selected_display()
            self.refresh_seat_buttons()
            
        else:
            # Some or all reservations failed
            failed_seats = ', '.join([f"{row}{num}" for row, num in result['failed']])
            
            if failed_seats:
                # Show which specific seats couldn't be reserved
                messagebox.showerror(
                    "Booking Failed", 
                    f"Could not reserve seats: {failed_seats}. "
                    f"They may have been taken by another user."
                )
            else:
                # General error message for unknown failures
                messagebox.showerror(
                    "Booking Failed", 
                    "There was an error booking your seats, please try again."
                )