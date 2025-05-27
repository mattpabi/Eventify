import sys
import os

# Point to qrcode package directory for importing
sys.path.append(os.path.join(os.path.dirname(__file__), "qrcode", "qrcode"))

import qrcode  # These are the only two non-default code libraries used in my project
import qrcode.image.base  # These are the only two non-default code libraries used in my project
import tkinter as tk
from tkinter import messagebox

class PPMImage(qrcode.image.base.BaseImage):
    def __init__(self, border, width, box_size, qrcode_modules=None, **kwargs):
        """
        Initialise the PPM image with specified dimensions and create white background.

        PPM (Portable Pixmap) is a simple image format that can be created without external dependencies.
        
        - The border parameter is the width of quiet zone around QR code in modules
        - The width parameter is the width of QR code in modules  
        - The box_size parameter is the pixel size of each QR module
        - The qrcode_modules parameter stores the QR code module data. It is unused but the library needs it present in order to work.
        - **kwargs are additional arguments. They are unused but kept in case the library needs them present in order to work.
        """
        # Initialize attributes directly, bypassing BaseImage.__init__ to avoid dependencies
        self.border = border  # Store quiet zone width
        self.width = width    # Store QR code width in modules
        self.box_size = box_size  # Store pixel size per module
        self.pixel_size = width * box_size  # Calculate total image size in pixels
        
        # Create 2D array representing image pixels, initialized to white (255)
        self.pixels = [[255] * self.pixel_size for _ in range(self.pixel_size)]

    def drawrect(self, row, col):
        """
        Draw a black square for a QR module at the specified position.
        
        This method is called by the QR code library for each black module in the QR pattern.
        
        - The row parameter is the row position of the module in the QR grid
        - The col parameter is the column position of the module in the QR grid
        """
        # Draw black square by setting pixels to 0 (black) for the entire module area
        for r in range(self.box_size):  # Iterate through pixel rows within module
            for c in range(self.box_size):  # Iterate through pixel columns within module
                # Calculate actual pixel position and set to black
                self.pixels[row * self.box_size + r][col * self.box_size + c] = 0

    def save(self, filename):
        """
        Save the image as a P3 PPM file.
        
        P3 PPM format stores RGB values as plain text, making it simple to generate without image processing libraries.
        
        - The filename parameter is the path where the PPM file should be saved
        """
        # Open file for writing PPM data
        with open(filename, "w") as f:
            # Write PPM header: format, dimensions, and maximum color value
            f.write(f"P3\n{self.pixel_size} {self.pixel_size}\n255\n")
            
            # Write pixel data as RGB triplets
            for row in self.pixels:  # Process each row of pixels
                for val in row:  # Process each pixel in the row
                    # Convert grayscale value to RGB triplet (black or white)
                    color = "0 0 0" if val == 0 else "255 255 255"
                    f.write(f"{color}\n")
        
        # Confirm successful save
        print(f"PPM image saved as {filename}")

def parse_ppm_to_photoimage(ppm_filename):
    """
    Parse a P3 PPM file and convert it to a Tkinter PhotoImage for display.
    
    This function reads the PPM file created by PPMImage and converts it to a format that can be displayed in Tkinter widgets.
    
    - The ppm_filename the file path of the PPM file to load
        
    Returns a tk.PhotoImage object for display, or None if loading fails
    """
    try:
        # Read entire PPM file into memory
        with open(ppm_filename, "r") as f:
            lines = f.readlines()
        
        # Parse and validate PPM header
        if not lines[0].strip() == "P3":
            raise ValueError("Not a P3 PPM file")
        
        # Extract image dimensions from header
        width, height = map(int, lines[1].strip().split())
        
        # Extract maximum color value and validate
        maxval = int(lines[2].strip())
        if maxval != 255:
            raise ValueError("Maxval must be 255")

        # Read all pixel data (RGB triplets) from remaining lines
        pixels = []
        for line in lines[3:]:  # Skip header lines
            pixels.extend(map(int, line.strip().split()))
        
        # Validate pixel data completeness (3 values per pixel: R, G, B)
        expected = width * height * 3
        if len(pixels) != expected:
            raise ValueError(f"Invalid pixel data: expected {expected}, got {len(pixels)}")

        # Create Tkinter PhotoImage with specified dimensions
        photo = tk.PhotoImage(width=width, height=height)
        
        # Convert pixel data to PhotoImage format
        for y in range(height):      # Process each row
            for x in range(width):   # Process each column
                # Calculate index for RGB triplet in linear pixel array
                idx = (y * width + x) * 3
                r, g, b = pixels[idx:idx+3]  # Extract RGB values
                
                # Convert RGB to hex color (QR codes are black and white only)
                color = "#000000" if r == 0 and g == 0 and b == 0 else "#FFFFFF"
                photo.put(color, (x, y))  # Set pixel color in PhotoImage
        
        return photo  # Return completed PhotoImage
        
    except Exception as e:
        # Show error message if loading fails
        messagebox.showerror("Error", f"Failed to load PPM: {e}")
        return None

def show_qr_window(parent_window, reservation_info, ppm_filename, on_close_callback=None):
    """
    Display QR code in a modal dialog window that integrates with the dashboard.
    
    Creates a modal window to display the QR code with reservation details and user instructions.\
    The window is modal, meaning it blocks interaction with the parent window until closed.
    
    - The parent_window is the parent window (dashboard root)
    - The reservation_info is the data that was encoded in the QR code
    - The ppm_filename is the file path to the PPM file containing the QR code image
    - The on_close_callback is the callback function to execute when window is closed
        
    Returns the created QR window object
    """
    # Create modal dialog window as child of parent
    qr_window = tk.Toplevel(parent_window)
    qr_window.title("Reservation QR Code")  # Set window title
    
    # Configure window as modal dialog
    qr_window.transient(parent_window)  # Make window transient to parent
    qr_window.grab_set()  # Make window modal (blocks parent interaction)
    
    # Centre the window on the user's screen
    window_width = 720
    window_height = 720

    # Calculate horizontal position to centre window
    position_right = int(qr_window.winfo_screenwidth() / 2 - window_width / 2)

    # Calculate vertical position to centre window
    position_down = int(qr_window.winfo_screenheight() / 2 - window_height / 2)
    
    # Set window size and position
    qr_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    # Set the minimum and maximum window sizes to maintain proper layout
    qr_window.minsize(720, 720)  # Minimum window size (width, height)
    qr_window.maxsize(1920, 1080)  # Maximum window size (width, height)
    
    # Create main frame with padding for professional appearance
    main_frame = tk.Frame(qr_window, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)  # Fill entire window
    
    # Window title label with bold formatting
    title_label = tk.Label(
        main_frame, 
        text="Your Reservation QR Code", 
        font=("Arial", 14, "bold")
    )
    title_label.pack(pady=(0, 10))  # Add bottom padding
    
    # Load and display the QR code image
    photo = parse_ppm_to_photoimage(ppm_filename)
    if photo:
        # Display QR code with raised border for visual emphasis
        qr_label = tk.Label(main_frame, image=photo, relief=tk.RAISED, borderwidth=2)
        qr_label.image = photo  # Keep reference to prevent garbage collection
        qr_label.pack(pady=10)  # Add vertical padding around image
    else:
        # Show error message if image loading failed
        error_label = tk.Label(
            main_frame, 
            text="Error loading QR code image", 
            font=("Arial", 12),
            fg="red"  # Red text to indicate error
        )
        error_label.pack(pady=10)
    
    # Create frame for reservation information display
    info_frame = tk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
    info_frame.pack(fill=tk.X, pady=10)  # Fill width with vertical padding
    
    # Display reservation details in formatted text
    info_label = tk.Label(
        info_frame, 
        text=f"Reservation Details:\n{reservation_info}", 
        font=("Arial", 10),
        justify=tk.LEFT,  # Left-align text
        wraplength=350,  # Wrap long lines
        padx=10,  # Horizontal padding
        pady=10  # Vertical padding
    )
    info_label.pack()
    
    # Display user instructions with blue text for emphasis
    instructions = tk.Label(
        main_frame,
        text="Instructions:\n• Take a screenshot or photo of this QR code\n• Present it to event staff upon entry\n• You will be charged after validation",
        font=("Arial", 10),
        justify=tk.LEFT,  # Left-align instructions
        fg="blue"  # Blue text for instructions
    )
    instructions.pack(pady=10)
    
    # Create frame for action buttons
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(20, 0))  # Fill width with top padding
    
    def close_window():
        """Handle window closing and execute callback if provided."""
        qr_window.destroy()  # Close the QR window
        if on_close_callback:
            on_close_callback()  # Execute callback function
    
    # Save button for user convenience (shows save location)
    save_button = tk.Button(
        button_frame,
        text="Save Image",
        command=lambda: messagebox.showinfo("Saved", f"QR code saved to:\n{ppm_filename}"),
        width=12
    )
    save_button.pack(side=tk.LEFT)  # Position on left side
    
    # Close button to dismiss the window
    close_button = tk.Button(
        button_frame,
        text="Close",
        command=close_window,  # Call close function
        width=12
    )
    close_button.pack(side=tk.RIGHT)  # Position on right side
    
    # Handle window close button (X) in title bar
    qr_window.protocol("WM_DELETE_WINDOW", close_window)
    
    return qr_window  # Return window object for caller reference

def generate_reservation_qr(reservation_info, ppm_filename="reservation_qr.ppm", box_size=10, border=4, parent_window=None, on_close_callback=None):
    """
    Generate a QR code for reservation information and display it in a modal dialog.
    
    This is the main function for creating reservation QR codes.
    It generates the QR code, saves it as a PPM file, and displays it in the modal window.
    
    - The reservation_info parameter is the data to encode (e.g., "ID123-MATTHEW-20250531")
    - The ppm_filename parameter is the output file path for PPM format image
    - The box_size parameter is the pixel size of each QR module (affects image size)
    - The border parameter is the quiet zone width in modules (white space around QR code)
    - The parent_window parameter is the parent window for modal dialog
    - The on_close_callback parameter is the function to call when QR window is closed
        
    Returns:
        The QR window object if successful, None if generation fails
    """
    try:
        # Configure QR code parameters for optimal scanning
        qr = qrcode.QRCode(
            version=1,  # QR code version (size)
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction for efficiency 
            box_size=box_size,  # Pixel size per module
            border=border,  # Quiet zone width
        )
        
        # Add reservation data to QR code and optimize size
        qr.add_data(reservation_info)
        qr.make(fit=True)  # Auto-adjust version if needed

        # Generate PPM image file using custom image factory
        qr.make_image(image_factory=PPMImage).save(ppm_filename)
        
        # Display QR code in appropriate window type
        if parent_window:
            # Show as modal dialog integrated with parent application
            return show_qr_window(parent_window, reservation_info, ppm_filename, on_close_callback)
        else:
            # Fallback: create standalone window for testing purposes
            root = tk.Tk()
            root.withdraw()  # Hide root window (only show QR dialog)
            return show_qr_window(root, reservation_info, ppm_filename, on_close_callback)
            
    except Exception as e:
        # Handle QR generation errors gracefully
        if parent_window:
            # Show error dialog if parent window available
            messagebox.showerror("QR Generation Error", f"Failed to generate QR code: {str(e)}")
        else:
            # Print error to console for debugging
            print(f"Error generating QR code: {e}")
        return None  # Return None to indicate failure