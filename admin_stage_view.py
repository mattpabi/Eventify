import tkinter as tk
import tkinter.messagebox as messagebox
import os

class AdminStageView:
    def __init__(self, root, db_manager, event_id, back_callback=None):
        self.db_manager = db_manager
        self.root = root

        # Set the minimum and maximum window sizes
        root.minsize(1280, 720)
        root.maxsize(1920, 1080)
        self.root.resizable(True, True)

        # Store event_id as attribute for easy access
        self.event_id = event_id
        self.back_callback = back_callback
        
        # Get event details
        self.event = self.db_manager.get_event_by_id(self.event_id)
        if self.event:
            self.root.title(f"Admin Seat View - {self.event['name']}")

        # Define the seating layout
        self.rows = [
            ('A', 24), ('B', 24),
            ('C', 28), ('D', 28),
            ('E', 32), ('F', 32),
            ('G', 36), ('H', 36), ('I', 36), ('J', 36), ('K', 36), ('L', 36),
            ('M', 34), ('N', 32)
        ]
        self.label_font = ("Arial", 7, "bold")

        # Get all reserved seats for this event
        self.reserved_seats = set(self.get_all_reserved_seats())
        
        # For hover info
        self.current_hover_info = None
        
        # Initialize seat states
        self.seat_buttons = {}  # Store seat buttons by seat_id
        
        # Track statistics
        self.total_seats = sum(count for _, count in self.rows)
        self.reserved_count = len(self.reserved_seats)

        self.load_images()
        self.setup_layout()
        self.initialize_seats()

    def load_images(self):
        try:
            file_path = os.path.dirname(os.path.abspath(__file__))
            img_seat = os.path.join(file_path, "images/seat.png")
            img_seat_reserved = os.path.join(file_path, "images/seat_reserved.png")
            self.seat_img = tk.PhotoImage(file=img_seat).subsample(21, 21)
            self.seat_img_reserved = tk.PhotoImage(file=img_seat_reserved).subsample(21, 21)
        except Exception as e:
            print("Error loading images:", e)
            # Create backup colors in case images fail to load
            self.seat_img = None
            self.seat_img_reserved = None

    def get_all_reserved_seats(self):
        """Get all reserved seats for the event."""
        try:
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT seat_row, seat_number, username FROM user_reservation
                WHERE event_id = ?
                ORDER BY seat_row, seat_number
                """,
                (self.event_id,)
            )
            results = cursor.fetchall()
            conn.close()
            
            # Return the results with username included
            return [(row, num, username) for row, num, username in results]
        except Exception as e:
            print(f"Error getting all reserved seats: {e}")
            return []

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

        # Display event info and statistics
        if hasattr(self, 'event') and self.event:
            event_info = f"{self.event['name']} - {self.event['date']} from {self.event['time']} to {self.event['end_time']}"
            event_label = tk.Label(header_frame, text=event_info, font=("Arial", 12, "bold"))
            event_label.grid(row=0, column=1, pady=10, sticky='w')
            
            # Add reservation statistics
            stats_text = f"Total Seats: {self.total_seats} | Reserved: {self.reserved_count} | " \
                        f"Available: {self.total_seats - self.reserved_count} | " \
                        f"Occupancy: {(self.reserved_count / self.total_seats * 100):.1f}%"
            stats_label = tk.Label(header_frame, text=stats_text, font=("Arial", 10))
            stats_label.grid(row=1, column=1, pady=(0, 10), sticky='w')

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
        """Initialize all seat buttons."""
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
        """Create a seat button with appropriate state based on reservation status."""
        # Check if this seat is reserved
        is_reserved = False
        username = None
        
        for reserved_row, reserved_num, reserved_user in self.reserved_seats:
            if seat_id == (reserved_row, reserved_num):
                is_reserved = True
                username = reserved_user
                break
        
        if is_reserved:
            btn_img = self.seat_img_reserved
        else:
            btn_img = self.seat_img
        
        # Create the button
        btn = tk.Button(
            self.frame, image=btn_img, width=24, height=24,
            padx=0, pady=0, borderwidth=0, highlightthickness=0,
            relief="flat", takefocus=0,
            bg=self.frame["bg"], activebackground=self.frame["bg"]
        )
        
        btn.grid(row=row, column=col, padx=0, pady=0)
        
        # Store seat information
        self.seat_buttons[seat_id] = {
            "button": btn,
            "reserved": is_reserved,
            "username": username
        }
        
        # Bind click to show detailed info in the side panel
        btn.bind("<Button-1>", lambda e, sid=seat_id: self.show_seat_info(sid))

    def show_hover_info(self, event, text):
        """Show hover information near the mouse cursor."""
        # Hide any existing hover info
        self.hide_hover_info()
        
        # Calculate position relative to the main window
        x, y = event.widget.winfo_rootx(), event.widget.winfo_rooty() + 25
        
        # Create tooltip-like window
        hover_window = tk.Toplevel(self.root)
        hover_window.wm_overrideredirect(True)  # Remove window decorations
        hover_window.wm_geometry(f"+{x}+{y}")
        
        # Create label with text
        label = tk.Label(hover_window, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 9))
        label.pack(padx=2, pady=2)
        
        # Store the hover window reference
        self.current_hover_info = hover_window

    def hide_hover_info(self, event=None):
        """Hide the hover information."""
        if self.current_hover_info:
            self.current_hover_info.destroy()
            self.current_hover_info = None

    def show_seat_info(self, seat_id):
        """Show detailed seat information in the side panel."""
        seat_data = self.seat_buttons.get(seat_id)
        if not seat_data:
            return
        
        row, num = seat_id
        seat_label = f"{row}{num}"
        
        # Clear the info display
        for widget in self.seat_info_frame.winfo_children():
            widget.destroy()
        
        # Show seat details
        title_label = tk.Label(self.seat_info_frame, text=f"Seat {seat_label} Details", font=("Arial", 12, "bold"))
        title_label.pack(anchor='w', pady=(0, 10))
        
        if seat_data.get("reserved"):
            status_text = "Status: Reserved"
            status_label = tk.Label(self.seat_info_frame, text=status_text, font=("Arial", 10, "bold"), fg="red")
            status_label.pack(anchor='w', pady=(0, 5))
            
            user_text = f"Reserved by: {seat_data.get('username', 'Unknown')}"
            user_label = tk.Label(self.seat_info_frame, text=user_text, font=("Arial", 10))
            user_label.pack(anchor='w', pady=(0, 5))
            
            # Option to view more user details or cancel reservation
            view_user_button = tk.Button(
                self.seat_info_frame, 
                text="View User Details", 
                command=lambda username=seat_data.get('username'): self.view_user_details(username),
                font=("Arial", 10)
            )
            view_user_button.pack(anchor='w', pady=(5, 0))
            
            cancel_button = tk.Button(
                self.seat_info_frame, 
                text="Cancel Reservation", 
                command=lambda sid=seat_id: self.cancel_reservation(sid),
                font=("Arial", 10)
            )
            cancel_button.pack(anchor='w', pady=(5, 0))
        else:
            status_text = "Status: Available"
            status_label = tk.Label(self.seat_info_frame, text=status_text, font=("Arial", 10, "bold"), fg="green")
            status_label.pack(anchor='w', pady=(0, 5))
            
            # No additional options for available seats

    def view_user_details(self, username):
        """View details about a user (placeholder function)."""
        messagebox.showinfo("User Details", f"Username: {username}")

    def cancel_reservation(self, seat_id):
        """Cancel a reservation as administrator."""
        row, num = seat_id
        seat_data = self.seat_buttons.get(seat_id)
        username = seat_data.get('username') if seat_data else "Unknown"
        
        seat_label = f"{row}{num}"
        
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Cancel Reservation", 
            f"Are you sure you want to cancel the reservation for seat {seat_label} by {username}?"
        )
        
        if confirm:
            success = self.db_manager.cancel_reservation(
                username, self.event_id, row, num
            )
            
            if success:
                messagebox.showinfo("Reservation Cancelled", f"Reservation for seat {seat_label} by {username} has been cancelled.")
                # Update seat data
                seat_data = self.seat_buttons.get(seat_id)
                if seat_data:
                    seat_data["reserved"] = False
                    seat_data["username"] = None
                    
                    # Update button appearance
                    btn = seat_data.get("button")
                    if btn:
                        btn.config(image=self.seat_img)
                
                # Update reservation count
                self.reserved_count -= 1
                self.update_stats()
                
                # Clear the seat info display
                for widget in self.seat_info_frame.winfo_children():
                    widget.destroy()
            else:
                messagebox.showerror("Error", f"Failed to cancel reservation for seat {seat_label}.")

    def update_stats(self):
            """Update the reservation statistics in the header."""
            if hasattr(self, 'event') and self.event:
                # Recalculate stats
                self.reserved_count = len(self.reserved_seats)
                available = self.total_seats - self.reserved_count
                occupancy_percentage = (self.reserved_count / self.total_seats * 100)
                
                # Update stats label in the header frame
                stats_text = f"Total Seats: {self.total_seats} | Reserved: {self.reserved_count} | " \
                            f"Available: {available} | " \
                            f"Occupancy: {occupancy_percentage:.1f}%"
                
                # Find the stats label in header_frame
                for widget in self.master.winfo_children():
                    if isinstance(widget, tk.Frame):  # This should be the header_frame
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Label) and child.cget("text").startswith("Total Seats:"):
                                child.config(text=stats_text)
                                break

    def create_info_panel(self):
        """Create the info panel on the right side of the main window."""
        # Right side panel container
        right_panel = tk.Frame(self.master, bd=0)
        right_panel.grid(row=1, column=2, rowspan=4, sticky='nsew', padx=10, pady=10)
        
        # Add a header for the right panel
        info_header = tk.Label(right_panel, text="Seat Information", font=("Arial", 14, "bold"))
        info_header.pack(anchor='n', pady=(0, 15))
        
        # Event statistics
        stats_frame = tk.LabelFrame(right_panel, text="Event Statistics", font=("Arial", 11, "bold"), padx=10, pady=10)
        stats_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Display statistics in the frame
        reserved_label = tk.Label(
            stats_frame, 
            text=f"Reserved Seats: {self.reserved_count} of {self.total_seats}", 
            font=("Arial", 10)
        )
        reserved_label.pack(anchor='w', pady=(0, 5))
        
        available_label = tk.Label(
            stats_frame, 
            text=f"Available Seats: {self.total_seats - self.reserved_count}", 
            font=("Arial", 10)
        )
        available_label.pack(anchor='w', pady=(0, 5))
        
        occupancy_label = tk.Label(
            stats_frame, 
            text=f"Occupancy: {(self.reserved_count / self.total_seats * 100):.1f}%", 
            font=("Arial", 10)
        )
        occupancy_label.pack(anchor='w', pady=(0, 5))
        
        # Seat information frame - will be populated when a seat is clicked
        self.seat_info_frame = tk.LabelFrame(right_panel, text="Selected Seat", font=("Arial", 11, "bold"), padx=10, pady=10)
        self.seat_info_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Add seat legend
        self.create_seat_legend(right_panel)
        
        # Export button for reports
        export_frame = tk.Frame(right_panel)
        export_frame.pack(fill='x', expand=False, pady=(15, 0))
        
        export_button = tk.Button(
            export_frame, 
            text="Export Reservation Data", 
            command=self.export_reservation_data,
            font=("Arial", 11)
        )
        export_button.pack(fill='x')

    def create_seat_legend(self, parent):
        """Create the seat legend in the right panel."""
        legend_frame = tk.LabelFrame(parent, text="Seat Legend", font=("Arial", 11, "bold"), padx=10, pady=10)
        legend_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Create legend items
        if self.seat_img and self.seat_img_reserved:
            # Available seats
            available_frame = tk.Frame(legend_frame)
            available_frame.pack(anchor='w', pady=5)
            
            available_img = tk.Label(available_frame, image=self.seat_img)
            available_img.pack(side='left', padx=(0, 10))
            
            available_label = tk.Label(available_frame, text="Available", font=("Arial", 10))
            available_label.pack(side='left')
            
            # Reserved seats
            reserved_frame = tk.Frame(legend_frame)
            reserved_frame.pack(anchor='w', pady=5)
            
            reserved_img = tk.Label(reserved_frame, image=self.seat_img_reserved)
            reserved_img.pack(side='left', padx=(0, 10))
            
            reserved_label = tk.Label(reserved_frame, text="Reserved", font=("Arial", 10))
            reserved_label.pack(side='left')
        else:
            # Fallback if images failed to load
            available_label = tk.Label(legend_frame, text="Green: Available", font=("Arial", 10))
            available_label.pack(anchor='w', pady=2)
            
            reserved_label = tk.Label(legend_frame, text="Red: Reserved", font=("Arial", 10))
            reserved_label.pack(anchor='w', pady=2)

    def export_reservation_data(self):
        """Export reservation data to a CSV file."""
        try:
            import csv
            from datetime import datetime
            import os
            from tkinter import filedialog
            
            # Get all reservations for this event
            all_reservations = []
            for row, num, username in self.reserved_seats:
                all_reservations.append({
                    'row': row,
                    'seat': num,
                    'seat_id': f"{row}{num}",
                    'username': username
                })
            
            if not all_reservations:
                messagebox.showinfo("No Data", "There are no reservations to export.")
                return
                
            # Sort by row and seat number
            all_reservations.sort(key=lambda x: (x['row'], x['seat']))
            
            # Generate default filename with date and event name
            event_name = self.event['name'].replace(' ', '_') if self.event else 'event'
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{event_name}_reservations_{date_str}.csv"
            
            # Ask user where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename
            )
            
            if not file_path:  # User cancelled
                return
                
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['seat_id', 'row', 'seat', 'username']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for reservation in all_reservations:
                    writer.writerow(reservation)
                    
            messagebox.showinfo("Export Successful", f"Reservation data exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")