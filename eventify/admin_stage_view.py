import tkinter as tk
import tkinter.messagebox as messagebox
import os
from base_stage_view import BaseStageView


class AdminStageView(BaseStageView):
    def __init__(self, root, db_manager, event_id, back_callback=None):
        """
        Initialise the administrative seat view interface.
        """
        # Store the database manager reference for later use
        self.db_manager = db_manager
        
        # Store the event ID we're managing
        self.event_id = event_id
        
        # Define the theatre layout - each tuple contains (row_letter, number_of_seats)
        self.rows = [
            ('A', 24), ('B', 24),           # Front rows with 24 seats each
            ('C', 28), ('D', 28),           # Middle-front rows with 28 seats each
            ('E', 32), ('F', 32),           # Middle rows with 32 seats each
            ('G', 36), ('H', 36), ('I', 36), # Back rows with 36 seats each
            ('J', 36), ('K', 36), ('L', 36), # More back rows
            ('M', 34), ('N', 32)            # Final rows with varying seat counts
        ]
        
        # Get all currently reserved seats from the database
        self.reserved_seats = set(self.get_all_reserved_seats())
        
        # Tracking variable for hover tooltip windows
        self.current_hover_info = None
        
        # Calculate total seats available in the theatre
        self.total_seats = sum(count for _, count in self.rows)
        
        # Count how many seats are currently reserved
        self.reserved_count = len(self.reserved_seats)

        # Call the parent class constructor to set up basic interface
        super().__init__(root, db_manager, event_id, back_callback, title_prefix="Admin Seat View")

        # Update the statistics display after the interface is created
        self.update_stats()

    def get_all_reserved_seats(self):
        """
        Retrieve all reserved seats along with username information from database.
        
        Returns a list of tuples containing (row, seat_number, username) for each reservation
        """
        try:
            # Establish connection to the database
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            # SQL query to get all reservations for this event, ordered by seat position
            cursor.execute(
                "SELECT seat_row, seat_number, username FROM user_reservation WHERE event_id = ? ORDER BY seat_row, seat_number",
                (self.event_id,)
            )
            
            # Fetch all matching records from the database
            results = cursor.fetchall()
            
            # Close database connection to free up resources
            conn.close()
            
            # Convert database results into list of tuples
            return [(row, num, username) for row, num, username in results]
            
        except Exception as e:
            # Print error message if database operation fails
            print(f"Error getting all reserved seats: {e}")
            return []  # Return empty list if error occurs

    def create_seat_button(self, row, col, seat_id):
        """
        Create an individual seat button with admin-specific functionality.
        
        
        The row parameter is the grid row position for the button
        The col parameter is the grid column position for the button
        The seat_id parameter is a tuple containing (row_letter, seat_number) for identification
        """
        # Check if this seat is currently reserved
        is_reserved = False
        username = None
        
        # Loop through all reserved seats to find matches
        for reserved_row, reserved_num, reserved_user in self.reserved_seats:
            if seat_id == (reserved_row, reserved_num):
                is_reserved = True      # Mark seat as reserved
                username = reserved_user # Store the username who reserved it
                break
        
        # Choose appropriate image based on reservation status
        btn_img = self.seat_img_reserved if is_reserved else self.seat_img
        
        # Create the button widget with specific styling
        btn = tk.Button(
            self.frame,  # Parent container
            image=btn_img,  # Image to display on button
            width=24, height=24,
            padx=0, pady=0,
            borderwidth=0,
            highlightthickness=0,  # No highlight border
            relief="flat",  # Flat button appearance
            takefocus=0,  # Button cannot receive keyboard focus
            bg=self.frame["bg"],  # Background matches parent
            activebackground=self.frame["bg"]  # Background when clicked matches parent
        )
        
        # Position the button in the grid layout
        btn.grid(row=row, column=col, padx=0, pady=0)
        
        # Store button information in dictionary for later reference
        self.seat_buttons[seat_id] = {
            "button": btn,
            "reserved": is_reserved,
            "username": username
        }
        
        # Bind left mouse click to show seat information
        btn.bind("<Button-1>", lambda e, sid=seat_id: self.show_seat_info(sid))

    def create_info_panel(self):
        """
        Create the right-hand information panel with statistics and controls.
        
        This panel displays:
        - Overall event statistics (occupancy, available seats)
        - Selected seat details
        - Seat legend
        - Export functionality
        """
        # Create main container for the right panel
        right_panel = tk.Frame(self.master, bd=0)
        right_panel.grid(row=1, column=2, rowspan=4, sticky='nsew', padx=10, pady=10)
        
        # Create header for the information section
        info_header = tk.Label(
            right_panel, 
            text="Seat Information", 
            font=("Arial", 14, "bold")
        )
        info_header.pack(anchor='n', pady=(0, 15))
        
        # Create statistics frame with border and title
        stats_frame = tk.LabelFrame(
            right_panel, 
            text="Event Statistics", 
            font=("Arial", 11, "bold"), 
            padx=10, 
            pady=10
        )
        stats_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Display number of reserved seats
        reserved_label = tk.Label(
            stats_frame, 
            text=f"Reserved Seats: {self.reserved_count} of {self.total_seats}", 
            font=("Arial", 10)
        )
        reserved_label.pack(anchor='w', pady=(0, 5))
        
        # Display number of available seats
        available_label = tk.Label(
            stats_frame, 
            text=f"Available Seats: {self.total_seats - self.reserved_count}", 
            font=("Arial", 10)
        )
        available_label.pack(anchor='w', pady=(0, 5))
        
        # Calculate and display occupancy percentage
        occupancy_percentage = (self.reserved_count / self.total_seats * 100)
        occupancy_label = tk.Label(
            stats_frame, 
            text=f"Occupancy: {occupancy_percentage:.1f}%", 
            font=("Arial", 10)
        )
        occupancy_label.pack(anchor='w', pady=(0, 5))
        
        # Create frame for displaying selected seat information
        self.seat_info_frame = tk.LabelFrame(
            right_panel, 
            text="Selected Seat", 
            font=("Arial", 11, "bold"), 
            padx=10, 
            pady=10
        )
        self.seat_info_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Add the seat legend to explain colour coding
        self.create_seat_legend(right_panel)
        
        # Create frame for export functionality
        export_frame = tk.Frame(right_panel)
        export_frame.pack(fill='x', expand=False, pady=(15, 0))
        
        # Add export button for downloading reservation data
        export_button = tk.Button(
            export_frame, 
            text="Export Reservation Data", 
            command=self.export_reservation_data, 
            font=("Arial", 11)
        )
        export_button.pack(fill='x')

    def create_seat_legend(self, parent):
        """
        Create a visual legend explaining seat colour coding.
        
        The parent parameter is the parent widget to attach the legend to
        """
        # Create bordered frame for the legend
        legend_frame = tk.LabelFrame(
            parent, 
            text="Seat Legend", 
            font=("Arial", 11, "bold"), 
            padx=10, 
            pady=10
        )
        legend_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Check if seat images are loaded successfully
        if self.seat_img and self.seat_img_reserved:
            # Create row for available seat explanation
            available_frame = tk.Frame(legend_frame)
            available_frame.pack(anchor='w', pady=5)
            
            # Display available seat image
            available_img = tk.Label(available_frame, image=self.seat_img)
            available_img.pack(side='left', padx=(0, 10))
            
            # Add text explanation for available seats
            available_label = tk.Label(available_frame, text="Available", font=("Arial", 10))
            available_label.pack(side='left')
            
            # Create row for reserved seat explanation
            reserved_frame = tk.Frame(legend_frame)
            reserved_frame.pack(anchor='w', pady=5)
            
            # Display reserved seat image
            reserved_img = tk.Label(reserved_frame, image=self.seat_img_reserved)
            reserved_img.pack(side='left', padx=(0, 10))
            
            # Add text explanation for reserved seats
            reserved_label = tk.Label(reserved_frame, text="Reserved", font=("Arial", 10))
            reserved_label.pack(side='left')
        else:
            # Fallback text-only legend if images fail to load
            available_label = tk.Label(legend_frame, text="Green: Available", font=("Arial", 10))
            available_label.pack(anchor='w', pady=2)
            
            reserved_label = tk.Label(legend_frame, text="Red: Reserved", font=("Arial", 10))
            reserved_label.pack(anchor='w', pady=2)

    def show_hover_info(self, event, text):
        """
        Display tooltip information when hovering over interface elements.
        
        The event parameter is the mouse event that triggered the hover.
        The text parameter the text to display in the tooltip.
        """
        # Hide any existing hover information first
        self.hide_hover_info()
        
        # Calculate position for tooltip (below the widget that was hovered)
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + 25
        
        # Create new popup window for the tooltip
        hover_window = tk.Toplevel(self.root)
        hover_window.wm_overrideredirect(True)  # Remove window decorations
        hover_window.wm_geometry(f"+{x}+{y}")  # Position the tooltip
        
        # Create label with the tooltip text and styling
        label = tk.Label(
            hover_window, 
            text=text, 
            justify=tk.LEFT,
            background="#ffffe0",  # Light yellow background
            relief=tk.SOLID, 
            borderwidth=1, 
            font=("Arial", 9)
        )
        label.pack(padx=2, pady=2)
        
        # Store reference to tooltip window for later cleanup
        self.current_hover_info = hover_window

    def hide_hover_info(self, event=None):
        """
        Hide any currently displayed hover tooltip.
        
        The event parameter isan optional event parameter (not used but expected by some callers)
        """
        # Check if there's a tooltip currently showing
        if self.current_hover_info:
            # Destroy the tooltip window
            self.current_hover_info.destroy()
            # Clear the reference
            self.current_hover_info = None

    def show_seat_info(self, seat_id):
        """
        Display detailed information about a selected seat in the info panel.
        
        The seat_id parameter is a tuple containing (row_letter, seat_number) for the selected seat.
        """
        # Get seat data from our stored information
        seat_data = self.seat_buttons.get(seat_id)
        if not seat_data:
            return  # Exit if seat data not found
        
        # Extract row and seat number from the seat ID
        row, num = seat_id
        seat_label = f"{row}{num}"  # Create human-readable seat label (e.g., "A12")
        
        # Clear any existing information in the seat info panel
        for widget in self.seat_info_frame.winfo_children():
            widget.destroy()
        
        # Create title showing which seat is selected
        title_label = tk.Label(
            self.seat_info_frame, 
            text=f"Seat {seat_label} Details", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Check if the seat is currently reserved
        if seat_data.get("reserved"):
            # Display reservation status in red text
            status_label = tk.Label(
                self.seat_info_frame, 
                text="Status: Reserved", 
                font=("Arial", 10, "bold"), 
                fg="red"
            )
            status_label.pack(anchor='w', pady=(0, 5))
            
            # Show who reserved the seat
            user_label = tk.Label(
                self.seat_info_frame, 
                text=f"Reserved by: {seat_data.get('username', 'Unknown')}", 
                font=("Arial", 10)
            )
            user_label.pack(anchor='w', pady=(0, 5))
            
            # Button to view detailed user information
            view_user_button = tk.Button(
                self.seat_info_frame, 
                text="View User Details",
                command=lambda username=seat_data.get('username'): self.view_user_details(username), 
                font=("Arial", 10)
            )
            view_user_button.pack(anchor='w', pady=(5, 0))
            
            # Button to cancel the current reservation
            cancel_button = tk.Button(
                self.seat_info_frame, 
                text="Cancel Reservation",
                command=lambda sid=seat_id: self.cancel_reservation(sid), 
                font=("Arial", 10)
            )
            cancel_button.pack(anchor='w', pady=(5, 0))
        else:
            # Display available status in green text
            status_label = tk.Label(
                self.seat_info_frame, 
                text="Status: Available", 
                font=("Arial", 10, "bold"), 
                fg="green"
            )
            status_label.pack(anchor='w', pady=(0, 5))

    def view_user_details(self, username):
        """
        Display detailed information about a user (placeholder implementation).
        """
        # Show basic user information in a message box
        # This could be expanded to show more detailed user data from database
        messagebox.showinfo("User Details", f"Username: {username}")

    def cancel_reservation(self, seat_id):
        """
        Cancel an existing seat reservation after admin confirmation.
        
        The seat_id parameter is a tuple containing (row_letter, seat_number) for the selected seat.
        """
        # Extract seat information
        row, num = seat_id
        seat_data = self.seat_buttons.get(seat_id)
        username = seat_data.get('username') if seat_data else "Unknown"
        seat_label = f"{row}{num}"
        
        # Ask admin to confirm the cancellation
        confirm = messagebox.askyesno(
            "Cancel Reservation", 
            f"Are you sure you want to cancel the reservation for seat {seat_label} by {username}?"
        )
        
        # Proceed only if admin confirms
        if confirm:
            # Attempt to cancel the reservation in the database
            success = self.db_manager.cancel_reservation(username, self.event_id, row, num)
            
            if success:
                # Show success message
                messagebox.showinfo(
                    "Reservation Cancelled", 
                    f"Reservation for seat {seat_label} by {username} has been cancelled."
                )
                
                # Update the seat button to show as available
                seat_data = self.seat_buttons.get(seat_id)
                if seat_data:
                    seat_data["reserved"] = False   # Mark as not reserved
                    seat_data["username"] = None    # Clear username
                    
                    # Change button image to available seat
                    btn = seat_data.get("button")
                    if btn:
                        btn.config(image=self.seat_img)
                
                # Update the reserved seat count
                self.reserved_count -= 1
                
                # Refresh the statistics display
                self.update_stats()
                
                # Clear the seat information panel
                for widget in self.seat_info_frame.winfo_children():
                    widget.destroy()
            else:
                # Show error message if cancellation failed
                messagebox.showerror(
                    "Error", 
                    f"Failed to cancel reservation for seat {seat_label}."
                )

    def update_stats(self):
        """
        Update the statistics display with current seat availability information.
        
        This method recalculates and updates all displayed statistics including total seats, reserved count, available count, and occupancy percentage.
        """
        # Recalculate current statistics
        self.reserved_count = len(self.reserved_seats)
        available = self.total_seats - self.reserved_count
        occupancy_percentage = (self.reserved_count / self.total_seats * 100)
        
        # Create formatted statistics text
        stats_text = (
            f"Total Seats: {self.total_seats} | "
            f"Reserved: {self.reserved_count} | "
            f"Available: {available} | "
            f"Occupancy: {occupancy_percentage:.1f}%"
        )
        
        # Find and update statistics label (search through widget hierarchy)
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    # Look for existing statistics label and update it
                    if isinstance(child, tk.Label) and child.cget("text").startswith("Total Seats:"):
                        child.config(text=stats_text)
                        break

    def export_reservation_data(self):
        """
        Export all reservation data to a CSV file for external analysis.
        
        This method creates a CSV file containing all current reservations with seat positions and usernames, then prompts admin to save it.
        """
        try:
            # Import required modules for CSV export
            import csv
            from datetime import datetime
            import os
            from tkinter import filedialog
            
            # Prepare list to store all reservation data
            all_reservations = []
            
            # Convert reserved seats data into exportable format
            for row, num, username in self.reserved_seats:
                all_reservations.append({
                    'row': row,
                    'seat': num,
                    'seat_id': f"{row}{num}",   # Combined seat identifier
                    'username': username
                })
            
            # Check if there are any reservations to export
            if not all_reservations:
                messagebox.showinfo("No Data", "There are no reservations to export.")
                return
            
            # Sort reservations by row and seat number for logical ordering
            all_reservations.sort(key=lambda x: (x['row'], x['seat']))
            
            # Create default filename based on event and current date/time
            event_name = self.event['name'].replace(' ', '_') if self.event else 'event'
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
            default_filename = f"{event_name}_reservations_{date_str}.csv"
            
            # Ask user where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename
            )
            
            # Exit if user cancels the save dialog
            if not file_path:
                return
            
            # Write data to CSV file
            with open(file_path, 'w', newline='') as csvfile:
                # Define column headers for the CSV
                fieldnames = ['seat_id', 'row', 'seat', 'username']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header row
                writer.writeheader()
                
                # Write each reservation as a row in the CSV
                for reservation in all_reservations:
                    writer.writerow(reservation)
            
            # Show success message with file location
            messagebox.showinfo(
                "Export Successful", 
                f"Reservation data exported to {file_path}"
            )
            
        except Exception as e:
            # Show error message if export fails
            messagebox.showerror(
                "Export Error", 
                f"Failed to export data: {str(e)}"
            )