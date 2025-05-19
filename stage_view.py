import tkinter as tk
import tkinter.messagebox as messagebox
import os

class StageView:
    def __init__(self, root, db_manager, event_id, username, back_callback=None):
        self.db_manager = db_manager
        self.root = root

        # Set the minimum and maximum window sizes
        root.minsize(1280, 720)
        root.maxsize(1920, 1080)
        self.root.resizable(True, True)

        # Store event_id and username as attributes for easy access
        self.event_id = event_id
        self.current_username = username
        self.back_callback = back_callback
        
        # Get event details
        self.event = self.db_manager.get_event_by_id(self.event_id)
        if self.event:
            self.root.title(f"Seat Selection - {self.event['name']}")

        self.rows = [
            ('A', 24), ('B', 24),
            ('C', 28), ('D', 28),
            ('E', 32), ('F', 32),
            ('G', 36), ('H', 36), ('I', 36), ('J', 36), ('K', 36), ('L', 36),
            ('M', 34), ('N', 32)
        ]
        self.label_font = ("Arial", 7, "bold")

        # Load reserved seats from database
        reserved_seats_list = self.db_manager.get_reserved_seats(self.event_id, self.current_username)
        self.reserved_seats = set(reserved_seats_list)

        user_reserved_seats_list = self.db_manager.get_user_reserved_seats(self.event_id, self.current_username)
        self.user_reserved_seats = set(user_reserved_seats_list)

        # Get user's current reservation count
        self.user_reservation_count = self.db_manager.get_user_reservation_count(self.event_id, self.current_username)

        self.selected_seats = set()
        self.seat_buttons = {}  # Changed to dictionary to store seat buttons by seat_id

        self.load_images()
        self.setup_layout()
        self.initialize_seats()
        self.update_reserved_display()
        self.update_selected_display()

    def load_images(self):
        try:
            file_path = os.path.dirname(os.path.abspath(__file__))
            img_seat = os.path.join(file_path, "images/seat.png")
            img_seat_selected = os.path.join(file_path, "images/seat_selected.png")
            img_seat_reserved = os.path.join(file_path, "images/seat_reserved.png")
            img_seat_user_reserved = os.path.join(file_path, "images/seat_user_reserved.png")
            self.seat_img = tk.PhotoImage(file=img_seat).subsample(21, 21)
            self.seat_img_selected = tk.PhotoImage(file=img_seat_selected).subsample(21, 21)
            self.seat_img_reserved = tk.PhotoImage(file=img_seat_reserved).subsample(21, 21)
            self.seat_img_user_reserved = tk.PhotoImage(file=img_seat_user_reserved).subsample(21, 21)
        except Exception as e:
            print("Error loading images:", e)
            self.seat_img = self.seat_img_selected = self.seat_img_reserved = self.seat_img_user_reserved = None

    def setup_layout(self):
        # Main container that will expand to fill the root window
        self.master = tk.Frame(self.root)
        self.master.pack(expand=True, fill='both')
        
        # Configure the master frame with a 3-column layout
        # Left column for margin, center for content, right for info panel
        self.master.grid_columnconfigure(0, weight=1)   # Left margin
        self.master.grid_columnconfigure(1, weight=10)  # Center content - give more weight
        self.master.grid_columnconfigure(2, weight=3)   # Right panel for info - fixed width
        
        self.master.grid_rowconfigure(0, weight=1)      # Top margin
        self.master.grid_rowconfigure(1, minsize=50)    # Event info row
        self.master.grid_rowconfigure(2, minsize=50)    # Stage row
        self.master.grid_rowconfigure(3, weight=1)      # Space before seats
        self.master.grid_rowconfigure(4, weight=5)      # Seats content - main content area
        self.master.grid_rowconfigure(5, weight=1)      # Bottom margin
        
        # Header frame - holds back button and event info
        header_frame = tk.Frame(self.master)
        header_frame.grid(row=1, column=1, sticky='ew')
        header_frame.grid_columnconfigure(0, weight=0)  # Back button
        header_frame.grid_columnconfigure(1, weight=1)  # Event info
        
        # Add back button if back callback exists
        if self.back_callback:
            back_button = tk.Button(
                header_frame, 
                text="Back to Dashboard", 
                command=self.back_callback,
                font=("Arial", 10),
                width=16
            )
            back_button.grid(row=0, column=0, pady=10, padx=10, sticky='w')

        # Display event info
        if hasattr(self, 'event') and self.event:
            event_info = f"{self.event['name']} - {self.event['date']} {self.event['time']}"
            event_label = tk.Label(header_frame, text=event_info, font=("Arial", 12, "bold"))
            event_label.grid(row=0, column=1, pady=10, sticky='ew')

        # Stage area
        self.stage = tk.Label(self.master, text="STAGE", bg="gold", font=("Arial", 16, "bold"), width=50, height=3)
        self.stage.grid(row=2, column=1, pady=(0, 20), sticky='ew')

        # Create a scrollable canvas for the seating area to handle large seat layouts
        self.canvas_container = tk.Frame(self.master)
        self.canvas_container.grid(row=4, column=1, sticky='nsew')
        self.canvas_container.grid_columnconfigure(0, weight=1)
        self.canvas_container.grid_rowconfigure(0, weight=1)
        
        # Add canvas with scrollbars if needed
        self.canvas = tk.Canvas(self.canvas_container)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars for canvas
        v_scrollbar = tk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(self.canvas_container, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Only show scrollbars when needed
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
            
        # Frame inside canvas to hold all seats
        self.frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        
        # Update the scrollregion when the frame size changes
        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Create the info panel on the right side of the main window
        self.create_info_panel()

    def on_frame_configure(self, event):
        """Update the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """When canvas is resized, resize the inner frame to match"""
        # Calculate center position
        canvas_width = event.width
        frame_width = self.frame.winfo_reqwidth()
        
        # Center the frame in the canvas
        if frame_width < canvas_width:
            # If the frame is smaller than the canvas, center it
            new_x = (canvas_width - frame_width) / 2
            self.canvas.coords(self.canvas_window, new_x, 0)
        else:
            # Otherwise keep it at the left edge
            self.canvas.coords(self.canvas_window, 0, 0)

    def initialize_seats(self):
        self.seat_buttons = {}
        
        # Calculate the center column to ensure seats are centered
        max_seats = max(row_info[1] for row_info in self.rows)
        center_col = max_seats + 5  # Provide some extra space
        
        for r, (row_label, total_seats) in enumerate(self.rows):
            left_count = total_seats // 2
            right_count = total_seats - left_count

            # Row labels (left)
            tk.Label(self.frame, text=row_label, font=self.label_font, width=2, anchor='e').grid(
                row=r, column=center_col - left_count - 1, padx=0, pady=0, sticky='e')

            # Left seats
            for c in range(left_count):
                col = center_col - left_count + c
                seat_num = c + 1
                seat_id = (row_label, seat_num)
                self.create_seat_button(r, col, seat_id)

            # Middle aisle
            tk.Label(self.frame, text="", width=2).grid(row=r, column=center_col)

            # Right seats
            for c in range(right_count):
                col = center_col + 1 + c
                seat_num = left_count + c + 1
                seat_id = (row_label, seat_num)
                self.create_seat_button(r, col, seat_id)

            # Row labels (right)
            tk.Label(self.frame, text=row_label, font=self.label_font, width=2, anchor='w').grid(
                row=r, column=center_col + right_count + 1, padx=0, pady=0, sticky='w')

    def create_seat_button(self, row, col, seat_id):
        """Create a seat button with appropriate state and command."""
        if seat_id in self.reserved_seats:
            btn_img = self.seat_img_reserved
            state = "disabled"
            command = None
        elif seat_id in self.user_reserved_seats:
            btn_img = self.seat_img_user_reserved
            state = "normal"  # Enable user's reserved seats for cancellation
            command = lambda sid=seat_id: self.cancel_seat_reservation(sid)
        else:
            btn_img = self.seat_img
            state = "normal"
            command = lambda sid=seat_id: self.toggle_seat(sid)

        btn = tk.Button(
            self.frame, image=btn_img, width=24, height=24,
            padx=0, pady=0, borderwidth=0, highlightthickness=0,
            relief="flat", takefocus=0,
            bg=self.frame["bg"], activebackground=self.frame["bg"],
            state=state
        )

        if command:
            btn.config(command=command)

        btn.grid(row=row, column=col, padx=0, pady=0)
        self.seat_buttons[seat_id] = {"button": btn, "selected": seat_id in self.selected_seats}

    def create_seat_legend(self, parent):
        """Create the seat legend in the right panel."""
        legend_frame = tk.LabelFrame(parent, text="Seat Legend", font=("Arial", 11, "bold"), padx=10, pady=10)
        legend_frame.pack(fill='x', expand=False, pady=(15, 0))
        
        legends = [
            (self.seat_img, "Available"),
            (self.seat_img_selected, "Selected"),
            (self.seat_img_reserved, "Unavailable"),
            (self.seat_img_user_reserved, "Your Reservation (Click to Cancel)")
        ]
        
        # Use a grid layout for the legend items - 2 columns
        for i, (img, text) in enumerate(legends):
            row = i // 2
            col = i % 2
            
            legend_item = tk.Frame(legend_frame)
            legend_item.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            label_img = tk.Label(legend_item, image=img)
            label_img.pack(side='left', padx=(0, 5))
            
            label_text = tk.Label(legend_item, text=text, font=("Arial", 9))
            label_text.pack(side='left')
        
        # Store images reference
        self.legend_images = [img for img, _ in legends]

    def create_info_panel(self):
        """Create the info panel with reserved and selected seats on the right side."""
        # Right side panel container
        right_panel = tk.Frame(self.master, bd=0)
        right_panel.grid(row=1, column=2, rowspan=4, sticky='nsew', padx=10, pady=10)
        
        # Add a header for the right panel
        info_header = tk.Label(right_panel, text="Seat Information", font=("Arial", 14, "bold"))
        info_header.pack(anchor='n', pady=(0, 15))
        
        # Reservation limit information
        self.reservation_limit_label = tk.Label(
            right_panel, 
            text=f"Reservation Limit: {self.user_reservation_count}/4 seats", 
            font=("Arial", 11, "bold")
        )
        self.reservation_limit_label.pack(anchor='n', pady=(0, 15))
        
        # Reserved Seats Section
        self.reserved_frame = tk.LabelFrame(right_panel, text="Your Reserved Seats", font=("Arial", 11, "bold"), padx=10, pady=10)
        self.reserved_frame.pack(fill='x', expand=False, pady=(0, 15))

        self.reserved_listbox = tk.Listbox(self.reserved_frame, height=6, width=20, exportselection=False, font=("Arial", 10))
        self.reserved_listbox.pack(side='left', fill='both', expand=True)
        reserved_scroll = tk.Scrollbar(self.reserved_frame, orient='vertical', command=self.reserved_listbox.yview)
        reserved_scroll.pack(side='right', fill='y')
        self.reserved_listbox.config(yscrollcommand=reserved_scroll.set)
        
        # Selected Seats Section
        self.selected_frame = tk.LabelFrame(right_panel, text="Your Selected Seats", font=("Arial", 11, "bold"), padx=10, pady=10)
        self.selected_frame.pack(fill='x', expand=False, pady=(0, 15))

        self.selected_listbox = tk.Listbox(self.selected_frame, height=6, width=20, exportselection=False, font=("Arial", 10))
        self.selected_listbox.pack(side='left', fill='both', expand=True)
        selected_scroll = tk.Scrollbar(self.selected_frame, orient='vertical', command=self.selected_listbox.yview)
        selected_scroll.pack(side='right', fill='y')
        self.selected_listbox.config(yscrollcommand=selected_scroll.set)

        # Booking section
        booking_frame = tk.LabelFrame(right_panel, text="Booking", font=("Arial", 11, "bold"), padx=10, pady=10)
        booking_frame.pack(fill='x', expand=False)
        
        # Price info (placeholder - you can add real pricing calculation here)
        if hasattr(self, 'event') and self.event:
            price_label = tk.Label(booking_frame, text=f"Price per seat: ${self.event['price']:.2f}", font=("Arial", 10))
            price_label.pack(anchor='w', pady=(0, 10))
            
            # Add a total price label that will be updated
            self.total_price_label = tk.Label(booking_frame, text="Total to be paid upon entry: $0.00", font=("Arial", 10, "bold"))
            self.total_price_label.pack(anchor='w', pady=(0, 15))
        
        # Book button
        self.book_button = tk.Button(booking_frame, text="Reserve Selected Seats", font=("Arial", 11, "bold"),
                                     state='disabled', command=self.reserve_selected_seats, width=18, height=2)
        self.book_button.pack(pady=5)
        
        # Legend section
        self.create_seat_legend(right_panel)

    def update_reserved_display(self):
        self.reserved_listbox.delete(0, tk.END)
        if self.user_reserved_seats:
            for row, num in sorted(self.user_reserved_seats):
                self.reserved_listbox.insert(tk.END, f"{row}{num}")
        else:
            self.reserved_listbox.insert(tk.END, "No reserved seats.")
        
        # Update reservation limit label
        self.user_reservation_count = self.db_manager.get_user_reservation_count(self.event_id, self.current_username)
        self.reservation_limit_label.config(text=f"Reservation Limit: {self.user_reservation_count}/4 seats")

    def update_selected_display(self):
        """Update the selected seats display and total price."""
        self.selected_listbox.delete(0, tk.END)
        if self.selected_seats:
            for row, num in sorted(self.selected_seats):
                self.selected_listbox.insert(tk.END, f"{row}{num}")
            
            # Only enable booking if user won't exceed 4 total reservations
            remaining_slots = 4 - self.user_reservation_count
            if len(self.selected_seats) <= remaining_slots:
                self.book_button.config(state='normal')
            else:
                self.book_button.config(state='disabled')
            
            # Update total price if we have event info
            if hasattr(self, 'event') and self.event and hasattr(self, 'total_price_label'):
                total = len(self.selected_seats) * self.event['price']
                self.total_price_label.config(text=f"Total to be paid upon entry: ${total:.2f}")
        else:
            self.selected_listbox.insert(tk.END, "No seats selected.")
            self.book_button.config(state='disabled')
            
            # Reset total price
            if hasattr(self, 'total_price_label'):
                self.total_price_label.config(text="Total to be paid upon entry: $0.00")

    def toggle_seat(self, seat_id):
        """Toggle selection state of a seat."""
        btn_data = self.seat_buttons.get(seat_id)
        if not btn_data:
            return
        
        btn = btn_data["button"]
        selected = btn_data["selected"]
        
        # Check if adding this seat would exceed the 4-seat limit
        if not selected and self.user_reservation_count + len(self.selected_seats) >= 4:
            messagebox.showwarning("Reservation Limit", 
                                  f"You can only reserve a maximum of 4 seats per event. You currently have "
                                  f"{self.user_reservation_count} reserved seats.")
            return
        
        if selected:
            btn.config(image=self.seat_img)
            btn_data["selected"] = False
            self.selected_seats.discard(seat_id)
        else:
            btn.config(image=self.seat_img_selected)
            btn_data["selected"] = True
            self.selected_seats.add(seat_id)
        
        self.update_selected_display()

    def cancel_seat_reservation(self, seat_id):
        """Cancel a reserved seat."""
        if seat_id not in self.user_reserved_seats:
            return
        
        row, num = seat_id
        seat_label = f"{row}{num}"
        
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Cancel Reservation", 
            f"Are you sure you want to cancel your reservation for seat {seat_label}?"
        )
        
        if confirm:
            success = self.db_manager.cancel_reservation(
                self.current_username, self.event_id, row, num
            )
            
            if success:
                messagebox.showinfo("Reservation Cancelled", f"Your reservation for seat {seat_label} has been cancelled.")
                # Update our data
                self.user_reserved_seats.remove(seat_id)
                # Update display
                self.update_reserved_display()
                # Update button
                self.refresh_seat_buttons()
            else:
                messagebox.showerror("Error", f"Failed to cancel reservation for seat {seat_label}.")

    def refresh_seat_buttons(self):
        # Re-fetch reserved seats 
        reserved_seats_list = self.db_manager.get_reserved_seats(self.event_id, self.current_username)
        self.reserved_seats = set(reserved_seats_list)
        
        user_reserved_seats_list = self.db_manager.get_user_reserved_seats(self.event_id, self.current_username)
        self.user_reserved_seats = set(user_reserved_seats_list)
        
        # Destroy all seat buttons and recreate
        for seat_id, seat_data in self.seat_buttons.items():
            if "button" in seat_data:
                seat_data["button"].destroy()
        
        self.seat_buttons.clear()
        self.initialize_seats()

    def reserve_selected_seats(self):
        seats_to_reserve = list(self.selected_seats)
        if not seats_to_reserve:
            messagebox.showwarning("No Seats Selected", "Please select at least one seat to book.")
            return
        
        # Check if adding these seats would exceed the 4-seat limit
        total_seats_after = self.user_reservation_count + len(seats_to_reserve)
        if total_seats_after > 4:
            messagebox.showwarning(
                "Reservation Limit Exceeded", 
                f"You can only reserve a maximum of 4 seats per event. You have {self.user_reservation_count} "
                f"seats already reserved. Please select no more than {4 - self.user_reservation_count} additional seats."
            )
            return

        result = self.db_manager.reserve_seats(self.current_username, self.event_id, seats_to_reserve)

        if result['success']:
            booked_seats = ', '.join([f"{row}{num}" for row, num in result['reserved']])
            messagebox.showinfo("Booking Successful", f"You have reserved seats: {booked_seats}")
            
            # Refresh reservation data
            self.user_reservation_count += len(result['reserved'])
            user_reserved_seats_list = self.db_manager.get_user_reserved_seats(self.event_id, self.current_username)
            self.user_reserved_seats = set(user_reserved_seats_list)
            
            self.selected_seats.clear()
            self.update_reserved_display()
            self.update_selected_display()
            self.refresh_seat_buttons()
        else:
            failed_seats = ', '.join([f"{row}{num}" for row, num in result['failed']])
            if failed_seats:
                messagebox.showerror("Booking Failed", f"Could not reserve seats: {failed_seats}. They may have been taken by another user.")
            else:
                messagebox.showerror("Booking Failed", "There was an error booking your seats, please try again.")