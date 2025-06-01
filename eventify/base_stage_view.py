import tkinter as tk
import tkinter.messagebox as messagebox
import os


class BaseStageView:
    def __init__(self, root, db_manager, event_id, back_callback=None, title_prefix="Seat View"):
        """
        Initialise the base stage view with all necessary components and functionality shared by user and admin views.
        
        This class creates a theatre seating layout display with a stage at the top and rows of seats below.
    
        It provides the basic structure that can be extended by child classes to add specific booking or management functionality.
        """
        # Store core attributes for use throughout the class
        self.db_manager = db_manager  # Store database connection for later use
        self.root = root  # Store main window reference
        self.event_id = event_id  # Store which event we're displaying seats for
        self.back_callback = back_callback  # Store function to return to previous screen

        # Configure window size and behaviour
        self.root.minsize(1280, 720)  # Set minimum window size (width, height)
        self.root.maxsize(1920, 1080)  # Set maximum window size to prevent over-expansion
        self.root.resizable(True, True)  # Allow user to resize window in both directions

        # Retrieve event details from database and set window title
        self.event = self.db_manager.get_event_by_id(self.event_id)  # Get event info from database
        if self.event:  # Check if event exists before setting title
            self.root.title(f"{title_prefix} - {self.event['name']}")  # Set window title with event name

        # Define theatre layout - each tuple contains (row_letter, number_of_seats)
        # This represents a typical theatre with more seats in middle rows
        self.rows = [
            ('A', 24), ('B', 24),  # Front rows with 24 seats each
            ('C', 28), ('D', 28),  # Next rows with 28 seats each
            ('E', 32), ('F', 32),  # Middle rows with 32 seats each
            ('G', 36), ('H', 36), ('I', 36), ('J', 36), ('K', 36), ('L', 36),  # Main seating area with 36 seats each
            ('M', 34), ('N', 32)   # Back rows with fewer seats due to theatre shape
        ]
        
        # Set font for row labels (small, bold Arial font)
        self.label_font = ("Arial", 7, "bold")

        # Initialise dictionary to store all seat button widgets
        # This will be populated when seats are created
        self.seat_buttons = {}

        # Load images and set up the user interface
        self.load_images()  # Load seat images from files
        self.setup_layout()  # Create the main interface layout
        self.initialise_seats()  # Create all the seat buttons

    def load_images(self):
        """
        Load seat images from files for display on buttons.
        
        This method attempts to load normal and reserved seat images.
        If loading fails, it sets images to None (child classes handle this).
        """
        try:
            # Get the directory where this Python file is located
            file_path = os.path.dirname(os.path.abspath(__file__))
            
            # Create full paths to image files
            img_seat = os.path.join(file_path, "images/seat.png")  # Normal seat image
            img_seat_reserved = os.path.join(file_path, "images/seat_reserved.png")  # Reserved seat image
            
            # Load images and scale them down (subsample makes them smaller)
            self.seat_img = tk.PhotoImage(file=img_seat).subsample(21, 21)  # Scale down by factor of 21
            self.seat_img_reserved = tk.PhotoImage(file=img_seat_reserved).subsample(21, 21)
            
        except Exception as e:  # Catch any errors during image loading
            print("Error loading images:", e)  # Display error message
            # Set images to None if loading fails - child classes must handle this
            self.seat_img = None
            self.seat_img_reserved = None

    def setup_layout(self):
        """
        Set up the main user interface layout with header, stage, and scrollable seat area.
        
        Creates a grid-based layout with:
        - Header area with back button and event information
        - Stage display
        - Scrollable canvas for seat layout
        - Info panel (implemented by child classes)
        """
        # Create main container frame that fills the entire window
        self.master = tk.Frame(self.root)
        self.master.pack(expand=True, fill='both')  # Make frame expand to fill window

        # Configure grid layout with weighted columns and rows
        # Columns: sidebar(1) | main content(10) | info panel(3)
        self.master.grid_columnconfigure(0, weight=1)   # Left sidebar column
        self.master.grid_columnconfigure(1, weight=10)  # Main content column (largest)
        self.master.grid_columnconfigure(2, weight=3)   # Right info panel column
        
        # Rows: top padding | header | stage | padding | seats | bottom padding
        self.master.grid_rowconfigure(0, weight=1)      # Top padding (expandable)
        self.master.grid_rowconfigure(1, minsize=50)    # Header row (fixed height)
        self.master.grid_rowconfigure(2, minsize=50)    # Stage row (fixed height)
        self.master.grid_rowconfigure(3, weight=1)      # Padding between stage and seats
        self.master.grid_rowconfigure(4, weight=5)      # Main seating area (largest)
        self.master.grid_rowconfigure(5, weight=1)      # Bottom padding

        # Create header frame for back button and event information
        header_frame = tk.Frame(self.master)
        header_frame.grid(row=1, column=1, sticky='ew')  # Place in header row, stretch horizontally
        
        # Configure header frame columns
        header_frame.grid_columnconfigure(0, weight=0)  # Back button column (fixed width)
        header_frame.grid_columnconfigure(1, weight=1)  # Event info column (expandable)

        # Create back button if callback function was provided
        if self.back_callback:
            back_button = tk.Button(
                header_frame, 
                text="Back to Dashboard", 
                command=self.back_callback,  # Function to call when clicked
                font=("Arial", 10), 
                width=16
            )
            back_button.grid(row=0, column=0, pady=10, padx=10, sticky='w')  # Position on left

        # Display event information if event data exists
        if self.event:
            # Create formatted string with event details
            event_info = f"{self.event['name']} - {self.event['date']} from {self.event['time']} to {self.event['end_time']}"
            event_label = tk.Label(header_frame, text=event_info, font=("Arial", 12, "bold"))
            event_label.grid(row=0, column=1, pady=10, sticky='w')  # Position after back button

        # Create stage display - gold background to represent theatre stage
        self.stage = tk.Label(
            self.master, 
            text="STAGE", 
            bg="gold",  # Gold background colour
            font=("Arial", 16, "bold"), 
            width=50,   # Wide label to span across seating area
            height=3    # Multiple lines high for visibility
        )
        self.stage.grid(row=2, column=1, pady=(0, 20), sticky='ew')  # Place below header with spacing

        # Create scrollable canvas container for seat layout
        self.canvas_container = tk.Frame(self.master)
        self.canvas_container.grid(row=4, column=1, sticky='nsew')  # Fill main seating area
        
        # Configure container grid to allow canvas expansion
        self.canvas_container.grid_columnconfigure(0, weight=1)  # Canvas column expands
        self.canvas_container.grid_rowconfigure(0, weight=1)     # Canvas row expands

        # Create main canvas for displaying seats (allows scrolling for large layouts)
        self.canvas = tk.Canvas(self.canvas_container)
        self.canvas.grid(row=0, column=0, sticky='nsew')  # Fill container

        # Create scrollbars for navigating large seat layouts
        v_scrollbar = tk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(self.canvas_container, orient="horizontal", command=self.canvas.xview)
        
        # Link scrollbars to canvas scrolling
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Position scrollbars around canvas
        v_scrollbar.grid(row=0, column=1, sticky='ns')  # Vertical scrollbar on right
        h_scrollbar.grid(row=1, column=0, sticky='ew')  # Horizontal scrollbar below

        # Create frame inside canvas to hold all seat buttons
        self.frame = tk.Frame(self.canvas)
        # Create window in canvas to display the frame
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        # Bind events to handle scrolling and resizing
        self.frame.bind("<Configure>", self.on_frame_configure)  # When frame size changes
        self.canvas.bind("<Configure>", self.on_canvas_configure)  # When canvas size changes

        # Create info panel (implementation provided by child classes)
        self.create_info_panel()

    def on_frame_configure(self, event):
        """
        Update scroll region when frame content changes size.
        
        This ensures the scrollbars work correctly when the seat layout
        is larger than the visible canvas area.
        
        The event parameter is the Tkinter event object
        """
        # Update scrollable region to match the size of all content
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """
        Centre the seat layout when canvas is resized.
        
        If the seat layout is smaller than the canvas, this centres it.
        If it's larger, it aligns it to the left edge.
        
        The event parameter is the Tkinter event object containing new canvas dimensions
        """
        canvas_width = event.width  # Get new canvas width
        frame_width = self.frame.winfo_reqwidth()  # Get required width of seat layout
        
        # If seat layout is smaller than canvas, centre it
        if frame_width < canvas_width:
            new_x = (canvas_width - frame_width) / 2  # Calculate centre position
            self.canvas.coords(self.canvas_window, new_x, 0)  # Move to centre
        else:
            # If layout is larger than canvas, align to left edge
            self.canvas.coords(self.canvas_window, 0, 0)

    def initialise_seats(self):
        """
        Create seat buttons arranged in theatre layout.
        
        Creates a realistic theatre layout with:
        - Row labels on both sides
        - Aisle down the middle splitting each row
        - Seats numbered from left to right within each half
        """
        # Reset seat buttons dictionary
        self.seat_buttons = {}
        
        # Find the row with the most seats to determine layout centre
        max_seats = max(row_info[1] for row_info in self.rows)
        center_col = max_seats + 5  # Calculate centre column for aisle

        # Create each row of seats
        for r, (row_label, total_seats) in enumerate(self.rows):
            # Split seats into left and right sections (for centre aisle)
            left_count = total_seats // 2  # Number of seats on left side
            right_count = total_seats - left_count  # Remaining seats on right side

            # Create left row label
            tk.Label(
                self.frame, 
                text=row_label, 
                font=self.label_font, 
                width=2, 
                anchor='e'  # Align text to right edge
            ).grid(row=r, column=center_col - left_count - 1, padx=0, pady=0, sticky='e')

            # Create left section seats
            for c in range(left_count):
                col = center_col - left_count + c  # Calculate grid column position
                seat_num = c + 1  # Seat number (1-based counting)
                seat_id = (row_label, seat_num)  # Unique identifier (row, seat number)
                self.create_seat_button(r, col, seat_id)  # Create the actual button

            # Create centre aisle space (empty column)
            tk.Label(self.frame, text="", width=2).grid(row=r, column=center_col)

            # Create right section seats
            for c in range(right_count):
                col = center_col + 1 + c  # Calculate grid column position (after aisle)
                seat_num = left_count + c + 1  # Continue seat numbering from left section
                seat_id = (row_label, seat_num)  # Unique identifier
                self.create_seat_button(r, col, seat_id)  # Create the actual button

            # Create right row label
            tk.Label(
                self.frame, 
                text=row_label, 
                font=self.label_font, 
                width=2, 
                anchor='w'  # Align text to left edge
            ).grid(row=r, column=center_col + right_count + 1, padx=0, pady=0, sticky='w')

    def create_seat_button(self, row, col, seat_id):
        """
        Create a seat button at specified position.
        
        This method is designed to be overridden by child classes to implement specific seat button behaviour (e.g., booking, management).
        """
        # This method intentionally left empty - child classes will implement
        # specific seat button creation based on their needs
        pass

    def create_info_panel(self):
        """
        Create the information panel on the right side of the interface.
        
        This method is designed to be overridden by child classes to display relevant information (e.g., booking details, seat legends).
        """
        # This method intentionally left empty - child classes will implement
        # specific info panel content based on their needs
        pass