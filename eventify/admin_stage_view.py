import tkinter as tk
import tkinter.messagebox as messagebox
import os

class AdminStageView:    
    def __init__(self, root, db_manager, event_id, back_callback=None):
        """
        Initialise the administrator stage view

        - The event_id parameter is the ID of the event to edit
        - The back_callback parameter is the function to call when user wants to go back
        """
        # Store database manager for accessing reservation data
        self.db_manager = db_manager
        # Store reference to main application window
        self.root = root

        # Configure window size constraints for optimal viewing
        root.minsize(1280, 720)  # Set minimum window dimensions
        root.maxsize(1920, 1080)  # Set maximum window dimensions
        self.root.resizable(True, True)  # Allow window to be resized by user

        # Store event identifier and navigation callback function
        self.event_id = event_id
        self.back_callback = back_callback
        
        # Retrieve event information from database using the event ID
        self.event = self.db_manager.get_event_by_id(self.event_id)
        if self.event:
            # Set window title to include event name for clarity
            self.root.title(f"Admin Seat View - {self.event['name']}")

        # Define the theatre seating layout structure
        # Each tuple contains (row_letter, number_of_seats_in_row)
        self.rows = [
            ('A', 24), ('B', 24),  # Front rows with 24 seats each
            ('C', 28), ('D', 28),  # Next rows with 28 seats each
            ('E', 32), ('F', 32),  # Middle rows with 32 seats each
            ('G', 36), ('H', 36), ('I', 36), ('J', 36), ('K', 36), ('L', 36),  # Main seating area with 36 seats each
            ('M', 34), ('N', 32)   # Back rows with fewer seats due to theatre shape
        ]
        # Font styling for row labels displayed on screen
        self.label_font = ("Arial", 7, "bold")

        # Fetch all reserved seats for this event from database
        self.reserved_seats = set(self.get_all_reserved_seats())
        
        # Variable to track currently displayed hover information
        self.current_hover_info = None
        
        # Dictionary to store seat button widgets organised by seat identifier
        self.seat_buttons = {}
        
        # Calculate seating statistics for display
        self.total_seats = sum(count for _, count in self.rows)  # Total available seats
        self.reserved_count = len(self.reserved_seats)  # Number of reserved seats

        # Load seat images and set up the user interface
        self.load_images()
        self.setup_layout()
        self.initialize_seats()

    def load_images(self):
        """
        Load seat icon images from the images directory
        Handles file loading errors gracefully with fallback options
        """
        try:
            # Get the directory path where this script is located
            file_path = os.path.dirname(os.path.abspath(__file__))
            # Construct full paths to seat image files
            img_seat = os.path.join(file_path, "images/seat.png")
            img_seat_reserved = os.path.join(file_path, "images/seat_reserved.png")
            # Load images and resize them to appropriate size for display
            self.seat_img = tk.PhotoImage(file=img_seat).subsample(21, 21)
            self.seat_img_reserved = tk.PhotoImage(file=img_seat_reserved).subsample(21, 21)
        except Exception as e:
            # Print error message if images fail to load
            print("Error loading images:", e)
            # Set image variables to None as fallback
            self.seat_img = None
            self.seat_img_reserved = None

    def get_all_reserved_seats(self):
        """
        Retrieve all reserved seats for the current event from database
        
        Returns a list of tuples containing (row, seat_number, username)
        """
        try:
            # Establish database connection
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            # SQL query to get all reservations for this event
            cursor.execute(
                """
                SELECT seat_row, seat_number, username FROM user_reservation
                WHERE event_id = ?
                ORDER BY seat_row, seat_number
                """,
                (self.event_id,)  # Parameter tuple for SQL query
            )
            # Fetch all matching records
            results = cursor.fetchall()
            # Close database connection to free resources
            conn.close()
            
            # Return formatted results with username information
            return [(row, num, username) for row, num, username in results]
        except Exception as e:
            # Print error message and return empty list if database query fails
            print(f"Error getting all reserved seats: {e}")
            return []

    def setup_layout(self):
        """
        Create and configure the main user interface layout
        Sets up a three-column layout with seating area and information panel
        """
        # Create main container frame that expands to fill entire window
        self.master = tk.Frame(self.root)
        self.master.pack(expand=True, fill='both')
        
        # Configure grid layout with three columns
        self.master.grid_columnconfigure(0, weight=1)   # Left margin space
        self.master.grid_columnconfigure(1, weight=10)  # Centre content area (main focus)
        self.master.grid_columnconfigure(2, weight=3)   # Right information panel
        
        # Configure grid layout with six rows
        self.master.grid_rowconfigure(0, weight=1)      # Top margin space
        self.master.grid_rowconfigure(1, minsize=50)    # Event information header
        self.master.grid_rowconfigure(2, minsize=50)    # Stage representation
        self.master.grid_rowconfigure(3, weight=1)      # Space before seating area
        self.master.grid_rowconfigure(4, weight=5)      # Main seating display area
        self.master.grid_rowconfigure(5, weight=1)      # Bottom margin space
        
        # Create header frame to hold navigation and event information
        header_frame = tk.Frame(self.master)
        header_frame.grid(row=1, column=1, sticky='ew')  # Stretch horizontally
        header_frame.grid_columnconfigure(0, weight=0)  # Back button column (fixed width)
        header_frame.grid_columnconfigure(1, weight=1)  # Event info column (expandable)
        
        # Add back navigation button if callback function provided
        if self.back_callback:
            back_button = tk.Button(
                header_frame, 
                text="Back to Dashboard",  # Button label text
                command=self.back_callback,  # Function to call when clicked
                font=("Arial", 10),  # Font styling
                width=16  # Button width in characters
            )
            # Position button in grid with padding
            back_button.grid(row=0, column=0, pady=10, padx=10, sticky='w')

        # Display event information and booking statistics
        if hasattr(self, 'event') and self.event:
            # Format event details string
            event_info = f"{self.event['name']} - {self.event['date']} from {self.event['time']} to {self.event['end_time']}"
            # Create label to display event information
            event_label = tk.Label(header_frame, text=event_info, font=("Arial", 12, "bold"))
            event_label.grid(row=0, column=1, pady=10, sticky='w')
            
            # Calculate and format reservation statistics
            stats_text = f"Total Seats: {self.total_seats} | Reserved: {self.reserved_count} | " \
                        f"Available: {self.total_seats - self.reserved_count} | " \
                        f"Occupancy: {(self.reserved_count / self.total_seats * 100):.1f}%"
            # Create label to display statistics
            stats_label = tk.Label(header_frame, text=stats_text, font=("Arial", 10))
            stats_label.grid(row=1, column=1, pady=(0, 10), sticky='w')

        # Create stage representation at top of seating area
        self.stage = tk.Label(self.master, text="STAGE", bg="gold", font=("Arial", 16, "bold"), width=50, height=3)
        self.stage.grid(row=2, column=1, pady=(0, 20), sticky='ew')

        # Create scrollable container for seating area to handle large layouts
        self.canvas_container = tk.Frame(self.master)
        self.canvas_container.grid(row=4, column=1, sticky='nsew')  # Fill available space
        self.canvas_container.grid_columnconfigure(0, weight=1)  # Canvas column expandable
        self.canvas_container.grid_rowconfigure(0, weight=1)  # Canvas row expandable
        
        # Create canvas widget for scrollable seating display
        self.canvas = tk.Canvas(self.canvas_container)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        
        # Add scrollbars for canvas navigation
        v_scrollbar = tk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(self.canvas_container, orient="horizontal", command=self.canvas.xview)
        # Connect scrollbars to canvas scrolling functions
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Position scrollbars (only visible when needed)
        v_scrollbar.grid(row=0, column=1, sticky='ns')  # Vertical scrollbar on right
        h_scrollbar.grid(row=1, column=0, sticky='ew')  # Horizontal scrollbar at bottom
            
        # Create frame inside canvas to contain all seat widgets
        self.frame = tk.Frame(self.canvas)
        # Add frame to canvas as a scrollable window
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        
        # Bind events to update canvas scroll region when content size changes
        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Create information panel on right side of interface
        self.create_info_panel()

    def on_frame_configure(self, event):
        """
        Update canvas scroll region when frame content size changes
        This ensures scrollbars appear when content exceeds visible area
        """
        # Set scroll region to encompass all content in frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """
        Adjust frame positioning when canvas is resized
        Centres the seating layout when window is larger than content
        """
        # Get current canvas width from resize event
        canvas_width = event.width
        # Get required width for frame content
        frame_width = self.frame.winfo_reqwidth()
        
        # Centre frame in canvas if canvas is wider than frame
        if frame_width < canvas_width:
            # Calculate centre position
            new_x = (canvas_width - frame_width) / 2
            # Move frame to centre position
            self.canvas.coords(self.canvas_window, new_x, 0)
        else:
            # Keep frame at left edge if it's wider than canvas
            self.canvas.coords(self.canvas_window, 0, 0)

    def initialize_seats(self):
        """
        Create all seat buttons and arrange them in theatre layout
        Organises seats in rows with centre aisle and row labels
        """
        # Clear any existing seat button references
        self.seat_buttons = {}
        
        # Calculate centre column position for symmetrical layout
        max_seats = max(row_info[1] for row_info in self.rows)  # Find widest row
        center_col = max_seats + 5  # Add extra space for labels and aisle
        
        # Create each row of seats
        for r, (row_label, total_seats) in enumerate(self.rows):
            # Calculate seats on each side of centre aisle
            left_count = total_seats // 2  # Integer division for left side
            right_count = total_seats - left_count  # Remaining seats for right side

            # Create row label on left side
            tk.Label(self.frame, text=row_label, font=self.label_font, width=2, anchor='e').grid(
                row=r, column=center_col - left_count - 1, padx=0, pady=0, sticky='e')

            # Create left side seats
            for c in range(left_count):
                col = center_col - left_count + c  # Calculate grid column position
                seat_num = c + 1  # Seat numbers start from 1
                seat_id = (row_label, seat_num)  # Create unique seat identifier
                self.create_seat_button(r, col, seat_id)  # Create button widget

            # Create centre aisle space
            tk.Label(self.frame, text="", width=2).grid(row=r, column=center_col)

            # Create right side seats
            for c in range(right_count):
                col = center_col + 1 + c  # Calculate grid column position
                seat_num = left_count + c + 1  # Continue seat numbering from left side
                seat_id = (row_label, seat_num)  # Create unique seat identifier
                self.create_seat_button(r, col, seat_id)  # Create button widget

            # Create row label on right side
            tk.Label(self.frame, text=row_label, font=self.label_font, width=2, anchor='w').grid(
                row=r, column=center_col + right_count + 1, padx=0, pady=0, sticky='w')

    def create_seat_button(self, row, col, seat_id):
        """
        Create individual seat button with appropriate appearance based on reservation status
        Args:
            row: Grid row position for button
            col: Grid column position for button
            seat_id: Tuple of (row_letter, seat_number) for identification
        """
        # Check if this seat is currently reserved
        is_reserved = False
        username = None
        
        # Search through reserved seats to find matching seat
        for reserved_row, reserved_num, reserved_user in self.reserved_seats:
            if seat_id == (reserved_row, reserved_num):
                is_reserved = True  # Mark seat as reserved
                username = reserved_user  # Store username who reserved it
                break
        
        # Select appropriate image based on reservation status
        if is_reserved:
            btn_img = self.seat_img_reserved  # Red image for reserved seats
        else:
            btn_img = self.seat_img  # Green image for available seats
        
        # Create button widget with seat image
        btn = tk.Button(
            self.frame, image=btn_img, width=24, height=24,  # Set image and size
            padx=0, pady=0, borderwidth=0, highlightthickness=0,  # Remove padding and borders
            relief="flat", takefocus=0,  # Flat appearance, no keyboard focus
            bg=self.frame["bg"], activebackground=self.frame["bg"]  # Match background colours
        )
        
        # Position button in grid layout
        btn.grid(row=row, column=col, padx=0, pady=0)
        
        # Store seat information in dictionary for later reference
        self.seat_buttons[seat_id] = {
            "button": btn,  # Widget reference
            "reserved": is_reserved,  # Reservation status
            "username": username  # Username if reserved
        }
        
        # Bind click event to show seat details in information panel
        btn.bind("<Button-1>", lambda e, sid=seat_id: self.show_seat_info(sid))

    def show_hover_info(self, event, text):
        """
        Display tooltip-style information near mouse cursor

        - The event parameter is the mouse event which contains the cursor position
        - The text parameter is the information text to display on hover
        """
        # Hide any existing hover information
        self.hide_hover_info()
        
        # Calculate tooltip position relative to main window
        x, y = event.widget.winfo_rootx(), event.widget.winfo_rooty() + 25
        
        # Create new tooltip window
        hover_window = tk.Toplevel(self.root)
        hover_window.wm_overrideredirect(True)  # Remove window decorations
        hover_window.wm_geometry(f"+{x}+{y}")  # Position at calculated coordinates
        
        # Create label with information text
        label = tk.Label(hover_window, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 9))
        label.pack(padx=2, pady=2)
        
        # Store reference to tooltip window for later cleanup
        self.current_hover_info = hover_window

    def hide_hover_info(self, event=None):
        """
        Remove currently displayed hover information tooltip
        """
        # Check if tooltip window exists
        if self.current_hover_info:
            # Destroy tooltip window
            self.current_hover_info.destroy()
            # Clear reference
            self.current_hover_info = None

    def show_seat_info(self, seat_id):
        """
        Display detailed seat information in the side panel

        The seat_id parameter is a tuple of (row_letter, seat_number) to display
        """
        # Get seat data from stored information
        seat_data = self.seat_buttons.get(seat_id)
        if not seat_data:
            return  # Exit if seat data not found
        
        # Extract row and seat number for display
        row, num = seat_id
        seat_label = f"{row}{num}"  # Format as readable seat identifier
        
        # Clear existing information display
        for widget in self.seat_info_frame.winfo_children():
            widget.destroy()
        
        # Create title label for seat details
        title_label = tk.Label(self.seat_info_frame, text=f"Seat {seat_label} Details", font=("Arial", 12, "bold"))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Display information based on reservation status
        if seat_data.get("reserved"):
            # Show reserved seat information
            status_text = "Status: Reserved"
            status_label = tk.Label(self.seat_info_frame, text=status_text, font=("Arial", 10, "bold"), fg="red")
            status_label.pack(anchor='w', pady=(0, 5))
            
            # Show username who reserved the seat
            user_text = f"Reserved by: {seat_data.get('username', 'Unknown')}"
            user_label = tk.Label(self.seat_info_frame, text=user_text, font=("Arial", 10))
            user_label.pack(anchor='w', pady=(0, 5))
            
            # Add button to view user details
            view_user_button = tk.Button(
                self.seat_info_frame, 
                text="View User Details", 
                command=lambda username=seat_data.get('username'): self.view_user_details(username),
                font=("Arial", 10)
            )
            view_user_button.pack(anchor='w', pady=(5, 0))
            
            # Add button to cancel reservation (admin function)
            cancel_button = tk.Button(
                self.seat_info_frame, 
                text="Cancel Reservation", 
                command=lambda sid=seat_id: self.cancel_reservation(sid),
                font=("Arial", 10)
            )
            cancel_button.pack(anchor='w', pady=(5, 0))
        else:
            # Show available seat information
            status_text = "Status: Available"
            status_label = tk.Label(self.seat_info_frame, text=status_text, font=("Arial", 10, "bold"), fg="green")
            status_label.pack(anchor='w', pady=(0, 5))

    def view_user_details(self, username):
        """
        Display user information in a popup window

        The username parameter is the username of the person who reserved the seat.
        """
        # Show basic user information in message box
        messagebox.showinfo("User Details", f"Username: {username}")

    def cancel_reservation(self, seat_id):
        """
        Cancel a seat reservation as administrator

        The seat_id parameter is the tuple of (row_letter, seat_number) to cancel.
        """
        # Extract seat information
        row, num = seat_id
        seat_data = self.seat_buttons.get(seat_id)
        username = seat_data.get('username') if seat_data else "Unknown"
        
        # Format seat identifier for display
        seat_label = f"{row}{num}"
        
        # Ask administrator for confirmation before cancelling
        confirm = messagebox.askyesno(
            "Cancel Reservation", 
            f"Are you sure you want to cancel the reservation for seat {seat_label} by {username}?"
        )
        
        # Proceed with cancellation if confirmed
        if confirm:
            # Attempt to cancel reservation in database
            success = self.db_manager.cancel_reservation(
                username, self.event_id, row, num
            )
            
            # Handle cancellation result
            if success:
                # Show success message
                messagebox.showinfo("Reservation Cancelled", f"Reservation for seat {seat_label} by {username} has been cancelled.")
                # Update local seat data
                seat_data = self.seat_buttons.get(seat_id)
                if seat_data:
                    seat_data["reserved"] = False  # Mark as available
                    seat_data["username"] = None  # Clear username
                    
                    # Update button appearance to show availability
                    btn = seat_data.get("button")
                    if btn:
                        btn.config(image=self.seat_img)  # Change to available image
                
                # Update reservation statistics
                self.reserved_count -= 1
                self.update_stats()
                
                # Clear seat information display
                for widget in self.seat_info_frame.winfo_children():
                    widget.destroy()
            else:
                # Show error message if cancellation failed
                messagebox.showerror("Error", f"Failed to cancel reservation for seat {seat_label}.")

    def update_stats(self):
        """
        Update reservation statistics display in header area
        Recalculates and refreshes occupancy information
        """
        if hasattr(self, 'event') and self.event:
            # Recalculate current statistics
            self.reserved_count = len(self.reserved_seats)
            available = self.total_seats - self.reserved_count
            occupancy_percentage = (self.reserved_count / self.total_seats * 100)
            
            # Format updated statistics text
            stats_text = f"Total Seats: {self.total_seats} | Reserved: {self.reserved_count} | " \
                        f"Available: {available} | " \
                        f"Occupancy: {occupancy_percentage:.1f}%"
            
            # Find and update statistics label in header
            for widget in self.master.winfo_children():
                if isinstance(widget, tk.Frame):  # Look for header frame
                    for child in widget.winfo_children():
                        # Find statistics label by checking text content
                        if isinstance(child, tk.Label) and child.cget("text").startswith("Total Seats:"):
                            child.config(text=stats_text)  # Update with new statistics
                            break

    def create_info_panel(self):
        """
        Create comprehensive information panel on right side of interface
        Includes statistics, seat details, legend, and export functionality
        """
        # Create main container for right panel
        right_panel = tk.Frame(self.master, bd=0)
        right_panel.grid(row=1, column=2, rowspan=4, sticky='nsew', padx=10, pady=10)
        
        # Add header title for information panel
        info_header = tk.Label(right_panel, text="Seat Information", font=("Arial", 14, "bold"))
        info_header.pack(anchor='n', pady=(0, 15))
        
        # Create statistics section with border
        stats_frame = tk.LabelFrame(right_panel, text="Event Statistics", font=("Arial", 11, "bold"), padx=10, pady=10)
        stats_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Display reservation statistics
        reserved_label = tk.Label(
            stats_frame, 
            text=f"Reserved Seats: {self.reserved_count} of {self.total_seats}", 
            font=("Arial", 10)
        )
        reserved_label.pack(anchor='w', pady=(0, 5))
        
        # Display available seats count
        available_label = tk.Label(
            stats_frame, 
            text=f"Available Seats: {self.total_seats - self.reserved_count}", 
            font=("Arial", 10)
        )
        available_label.pack(anchor='w', pady=(0, 5))
        
        # Display occupancy percentage
        occupancy_label = tk.Label(
            stats_frame, 
            text=f"Occupancy: {(self.reserved_count / self.total_seats * 100):.1f}%", 
            font=("Arial", 10)
        )
        occupancy_label.pack(anchor='w', pady=(0, 5))
        
        # Create seat information section (populated when seat is clicked)
        self.seat_info_frame = tk.LabelFrame(right_panel, text="Selected Seat", font=("Arial", 11, "bold"), padx=10, pady=10)
        self.seat_info_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Add seat colour legend
        self.create_seat_legend(right_panel)
        
        # Create export functionality section
        export_frame = tk.Frame(right_panel)
        export_frame.pack(fill='x', expand=False, pady=(15, 0))
        
        # Add button to export reservation data to file
        export_button = tk.Button(
            export_frame, 
            text="Export Reservation Data", 
            command=self.export_reservation_data,  # Function to handle export
            font=("Arial", 11)
        )
        export_button.pack(fill='x')

    def create_seat_legend(self, parent):
        """
        Create visual legend showing seat colour meanings

        The parent parameter is the parent widget to contain the seat legend.
        """
        # Create legend section with border
        legend_frame = tk.LabelFrame(parent, text="Seat Legend", font=("Arial", 11, "bold"), padx=10, pady=10)
        legend_frame.pack(fill='x', expand=False, pady=(0, 15))
        
        # Create legend items if images loaded successfully
        if self.seat_img and self.seat_img_reserved:
            # Available seats legend item
            available_frame = tk.Frame(legend_frame)
            available_frame.pack(anchor='w', pady=5)
            
            # Show available seat image
            available_img = tk.Label(available_frame, image=self.seat_img)
            available_img.pack(side='left', padx=(0, 10))
            
            # Add text explanation
            available_label = tk.Label(available_frame, text="Available", font=("Arial", 10))
            available_label.pack(side='left')
            
            # Reserved seats legend item
            reserved_frame = tk.Frame(legend_frame)
            reserved_frame.pack(anchor='w', pady=5)
            
            # Show reserved seat image
            reserved_img = tk.Label(reserved_frame, image=self.seat_img_reserved)
            reserved_img.pack(side='left', padx=(0, 10))
            
            # Add text explanation
            reserved_label = tk.Label(reserved_frame, text="Reserved", font=("Arial", 10))
            reserved_label.pack(side='left')
        else:
            # Fallback text-only legend if images failed to load
            available_label = tk.Label(legend_frame, text="Green: Available", font=("Arial", 10))
            available_label.pack(anchor='w', pady=2)
            
            reserved_label = tk.Label(legend_frame, text="Red: Reserved", font=("Arial", 10))
            reserved_label.pack(anchor='w', pady=2)

    def export_reservation_data(self):
        """
        Export all reservation data to a CSV file for external use
        Allows administrators to save booking information for records
        """
        try:
            # Import required modules for file operations
            import csv
            from datetime import datetime
            import os
            from tkinter import filedialog
            
            # Prepare reservation data for export
            all_reservations = []
            for row, num, username in self.reserved_seats:
                # Create dictionary for each reservation
                all_reservations.append({
                    'row': row,  # Seat row letter
                    'seat': num,  # Seat number
                    'seat_id': f"{row}{num}",  # Combined seat identifier
                    'username': username  # Person who made reservation
                })
            
            # Check if there are any reservations to export
            if not all_reservations:
                messagebox.showinfo("No Data", "There are no reservations to export.")
                return
                
            # Sort reservations by row and seat number for organised output
            all_reservations.sort(key=lambda x: (x['row'], x['seat']))
            
            # Generate default filename with timestamp and event name
            event_name = self.event['name'].replace(' ', '_') if self.event else 'event'
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")  # Current date and time
            default_filename = f"{event_name}_reservations_{date_str}.csv"
            
            # Ask user where to save the export file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",  # Default file extension
                filetypes=[("CSV files", "*.csv")],  # File type filter
                initialfile=default_filename  # Suggested filename
            )
            
            # Exit if user cancelled file selection
            if not file_path:
                return
                
            # Write reservation data to CSV file
            with open(file_path, 'w', newline='') as csvfile:
                # Define column headers for CSV file
                fieldnames = ['seat_id', 'row', 'seat', 'username']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header row
                writer.writeheader()
                # Write each
                for reservation in all_reservations:
                    writer.writerow(reservation)
                    
            messagebox.showinfo("Export Successful", f"Reservation data exported to {file_path}")
            
        except Exception as e:
            # Print error message if the data export does not work
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")