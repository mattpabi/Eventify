import tkinter as tk
import tkinter.messagebox as messagebox
import os

class StageView:
    def __init__(self, root, db_manager, event_id, username, back_callback=None):
        self.db_manager = db_manager
        self.root = root
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

        self.selected_seats = set()
        self.seat_buttons = []

        self.load_images()
        self.setup_layout()
        self.initialize_seats()
        self.add_seat_legend()
        self.add_info_panel()
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
        self.master = tk.Frame(self.root)
        self.master.pack(expand=True, fill='both')
        
        # Add back button if back callback exists
        if self.back_callback:
            back_button = tk.Button(
                self.master, 
                text="Back to Dashboard", 
                command=self.back_callback,
                font=("Arial", 10),
                width=16
            )
            back_button.grid(row=0, column=0, pady=10, padx=10, sticky='nw')

        # Display event info
        if hasattr(self, 'event') and self.event:
            event_info = f"{self.event['name']} - {self.event['date']} {self.event['time']}"
            event_label = tk.Label(self.master, text=event_info, font=("Arial", 12, "bold"))
            event_label.grid(row=0, column=1, pady=10, sticky='n')

        self.stage = tk.Label(self.master, text="STAGE", bg="gold", font=("Arial", 16, "bold"), width=50, height=3)
        self.stage.grid(row=1, column=1, pady=(0, 2), sticky='n')

        for gap_row in range(2, 7):
            tk.Label(self.master, text="").grid(row=gap_row, column=1)

        self.master.grid_columnconfigure(0, minsize=12)
        self.master.grid_columnconfigure(1, weight=1)
        self.frame = tk.Frame(self.master)
        self.frame.grid(row=7, column=1, sticky='n')

    def initialize_seats(self):
        self.seat_buttons = []
        for r, (row_label, total_seats) in enumerate(self.rows):
            left_count = total_seats // 2
            right_count = total_seats - left_count

            tk.Label(self.frame, text=row_label, font=self.label_font, width=2, anchor='e').grid(
                row=r, column=0, padx=0, pady=0, sticky='e')

            # Left seats
            for c in range(left_count):
                col = 18 - left_count + c + 1
                seat_num = c + 1
                seat_id = (row_label, seat_num)
                selected = [False]

                if seat_id in self.reserved_seats:
                    btn_img = self.seat_img_reserved
                    state = "disabled"
                elif seat_id in self.user_reserved_seats:
                    btn_img = self.seat_img_user_reserved
                    state = "disabled"
                else:
                    btn_img = self.seat_img
                    state = "normal"

                btn = tk.Button(
                    self.frame, image=btn_img, width=24, height=24,
                    padx=0, pady=0, borderwidth=0, highlightthickness=0,
                    relief="flat", takefocus=0,
                    bg=self.frame["bg"], activebackground=self.frame["bg"],
                    state=state
                )

                if state == "normal":
                    btn.config(command=lambda b=btn, s=selected, sid=seat_id: self.toggle_seat(b, s, sid))

                btn.grid(row=r, column=col, padx=0, pady=0)
                self.seat_buttons.append((btn, seat_id, selected))

            tk.Label(self.frame, text="", width=1).grid(row=r, column=19)

            # Right seats
            for c in range(right_count):
                col = 20 + c
                seat_num = left_count + c + 1
                seat_id = (row_label, seat_num)
                selected = [False]

                if seat_id in self.reserved_seats:
                    btn_img = self.seat_img_reserved
                    state = "disabled"
                elif seat_id in self.user_reserved_seats:
                    btn_img = self.seat_img_user_reserved
                    state = "disabled"
                else:
                    btn_img = self.seat_img
                    state = "normal"

                btn = tk.Button(
                    self.frame, image=btn_img, width=24, height=24,
                    padx=0, pady=0, borderwidth=0, highlightthickness=0,
                    relief="flat", takefocus=0,
                    bg=self.frame["bg"], activebackground=self.frame["bg"],
                    state=state
                )

                if state == "normal":
                    btn.config(command=lambda b=btn, s=selected, sid=seat_id: self.toggle_seat(b, s, sid))

                btn.grid(row=r, column=col, padx=0, pady=0)
                self.seat_buttons.append((btn, seat_id, selected))

            for c in range(right_count, 18):
                col = 20 + c
                tk.Label(self.frame, text="", width=2).grid(row=r, column=col)

            tk.Label(self.frame, text=row_label, font=self.label_font, width=2, anchor='w').grid(
                row=r, column=38, padx=0, pady=0, sticky='w')

    def add_seat_legend(self):
        legend_row = len(self.rows) + 1
        legend_frame = tk.Frame(self.frame)
        legend_frame.grid(row=legend_row, column=0, columnspan=39, pady=10)
        legend_frame.grid_columnconfigure(0, weight=1)
        legends = [
            (self.seat_img, "Available"),
            (self.seat_img_reserved, "Unavailable"),
            (self.seat_img_selected, "Selected"),
            (self.seat_img_user_reserved, "Your Reservation")
        ]
        for i, (img, text) in enumerate(legends):
            item_frame = tk.Frame(legend_frame)
            item_frame.grid(row=0, column=i, padx=15)
            label_img = tk.Label(item_frame, image=img)
            label_img.pack(side='top')
            label_text = tk.Label(item_frame, text=text, font=("Arial", 10))
            label_text.pack(side='top')
        self.legend_images = [img for img, _ in legends]

    def add_info_panel(self):
        # Place 5 rows after the legend
        info_panel_row = len(self.rows) + 1 + 5
        self.info_panel = tk.Frame(self.frame)
        self.info_panel.grid(row=info_panel_row, column=0, columnspan=39, pady=10, sticky='n')

        # Reserved Seats Section
        self.reserved_frame = tk.LabelFrame(self.info_panel, text="Your Reserved Seats", font=("Arial", 10, "bold"))
        self.reserved_frame.pack(side='left', padx=10, fill='y')

        self.reserved_listbox = tk.Listbox(self.reserved_frame, height=8, width=20, exportselection=False)
        self.reserved_listbox.pack(side='left', fill='y')
        reserved_scroll = tk.Scrollbar(self.reserved_frame, orient='vertical', command=self.reserved_listbox.yview)
        reserved_scroll.pack(side='right', fill='y')
        self.reserved_listbox.config(yscrollcommand=reserved_scroll.set)
        # Make reserved seats listbox non-interactive
        self.reserved_listbox.bind("<Button-1>", lambda e: "break")
        self.reserved_listbox.bind("<B1-Motion>", lambda e: "break")
        self.reserved_listbox.bind("<FocusIn>", lambda e: self.root.focus())

        # Selected Seats Section
        self.selected_frame = tk.LabelFrame(self.info_panel, text="Your Selected Seats", font=("Arial", 10, "bold"))
        self.selected_frame.pack(side='left', padx=10, fill='y')

        self.selected_listbox = tk.Listbox(self.selected_frame, height=8, width=20, exportselection=False)
        self.selected_listbox.pack(side='left', fill='y')
        selected_scroll = tk.Scrollbar(self.selected_frame, orient='vertical', command=self.selected_listbox.yview)
        selected_scroll.pack(side='right', fill='y')
        self.selected_listbox.config(yscrollcommand=selected_scroll.set)

        # Book Button (below selected seats)
        self.button_panel = tk.Frame(self.info_panel)
        self.button_panel.pack(side='left', padx=20, anchor='n', fill='y')
        self.book_button = tk.Button(self.button_panel, text="Book", font=("Arial", 12, "bold"),
                                     state='disabled', command=self.book_selected_seats)
        self.book_button.pack(pady=(50, 0), anchor='n')  # 50px top padding for vertical spacing

    def update_reserved_display(self):
        self.reserved_listbox.delete(0, tk.END)
        if self.user_reserved_seats:
            for row, num in sorted(self.user_reserved_seats):
                self.reserved_listbox.insert(tk.END, f"{row}{num}")
        else:
            self.reserved_listbox.insert(tk.END, "No reserved seats.")

    def update_selected_display(self):
        self.selected_listbox.delete(0, tk.END)
        if self.selected_seats:
            for row, num in sorted(self.selected_seats):
                self.selected_listbox.insert(tk.END, f"{row}{num}")
            self.book_button.config(state='normal')
        else:
            self.selected_listbox.insert(tk.END, "No seats selected.")
            self.book_button.config(state='disabled')

    def toggle_seat(self, btn, selected, seat_id):
        if selected[0]:
            btn.config(image=self.seat_img)
            selected[0] = False
            self.selected_seats.discard(seat_id)
        else:
            btn.config(image=self.seat_img_selected)
            selected[0] = True
            self.selected_seats.add(seat_id)
        self.update_selected_display()

    def refresh_seat_buttons(self):
        # Re-fetch reserved seats (excluding current user)
        reserved_seats_list = self.db_manager.get_reserved_seats(self.event_id, self.current_username)
        self.reserved_seats = set(reserved_seats_list)
        user_reserved_seats_list = self.db_manager.get_user_reserved_seats(self.event_id, self.current_username)
        self.user_reserved_seats = set(user_reserved_seats_list)
        # Destroy all seat buttons and recreate
        for btn, _, _ in self.seat_buttons:
            btn.destroy()
        self.seat_buttons.clear()
        self.initialize_seats()

    def book_selected_seats(self):
        seats_to_reserve = list(self.selected_seats)
        if not seats_to_reserve:
            messagebox.showwarning("No Seats Selected", "Please select at least one seat to book.")
            return

        result = self.db_manager.reserve_seats(self.current_username, self.event_id, seats_to_reserve)

        if result['success']:
            booked_seats = ', '.join([f"{row}{num}" for row, num in result['reserved']])
            messagebox.showinfo("Booking Successful", f"You have booked seats: {booked_seats}")
            # Refresh reserved seats from database
            user_reserved_seats_list = self.db_manager.get_user_reserved_seats(self.event_id, self.current_username)
            self.user_reserved_seats = set(user_reserved_seats_list)
            self.selected_seats.clear()
            self.update_reserved_display()
            self.update_selected_display()
            self.refresh_seat_buttons()
        else:
            messagebox.showerror("Booking Failed", "There was an error booking your seats, please try again.")