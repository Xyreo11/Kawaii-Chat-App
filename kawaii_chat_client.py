import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import datetime
import base64

# Color scheme
THEME_COLORS = {
    'bg_main': '#FFD6EC',  # Light pink
    'bg_sidebar': '#FFBEDD',  # Darker pink
    'accent': '#FF85C2',  # Hot pink
    'text_dark': '#5C4055',  # Dark mauve
    'text_light': '#FFFFFF',  # White
    'button': '#FF66B2',  # Bright pink
    'button_hover': '#FF33A1',  # Brighter pink
    'input_bg': '#FFFFFF',  # White
    'secondary': '#E6A7C5',  # Lavender pink
}

# Fonts
FONT_MAIN = ('Comic Sans MS', 10)
FONT_HEADER = ('Comic Sans MS', 14, 'bold')
FONT_MESSAGE = ('Comic Sans MS', 10)
FONT_TITLE = ('Comic Sans MS', 18, 'bold')

class KawaiiChatClient:
    def __init__(self, root):
        # Main window setup
        self.root = root
        self.root.title("🌸 KawaiiChat 🌸")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        self.root.configure(bg=THEME_COLORS['bg_main'])
        
        # Set icon if available
        try:
            self.root.iconbitmap('kawaii_icon.ico')
        except:
            pass
        
        # Server configuration
        self.server_host = '127.0.0.1'  # Default value
        self.server_port = 9999         # Default value
        
        # Try to load saved server settings
        self.load_server_settings()
        
        # Socket and connection
        self.socket = None
        self.connected = False
        self.current_user = None
        self.user_list = []
        self.current_chat_user = None
        
        # Initialize chat messages dict
        self.chat_messages = {}  # {user_id: [messages]}
        
        # Create server config button on login screen
        self.create_login_frame()
    
    def create_server_config_dialog(self):
        """Create a dialog to configure server connection settings"""
        config_window = tk.Toplevel(self.root)
        config_window.title("✨ Server Connection ✨")
        config_window.geometry("400x300")
        config_window.configure(bg=THEME_COLORS['bg_main'])
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Title with decorative elements
        tk.Label(config_window, text="✧･ﾟ: *✧･ﾟ:*", font=('Comic Sans MS', 14), 
                bg=THEME_COLORS['bg_main'], fg=THEME_COLORS['accent']).pack(pady=(10, 0))
        
        tk.Label(config_window, text="Connect to Server", font=FONT_HEADER, 
                bg=THEME_COLORS['bg_main'], fg=THEME_COLORS['text_dark']).pack(pady=(5, 15))
        
        # Form frame
        form_frame = tk.Frame(config_window, bg=THEME_COLORS['secondary'], padx=20, pady=20,
                            bd=2, relief=tk.GROOVE)
        form_frame.pack(padx=20, pady=10, fill=tk.X)
        
        # Server address
        tk.Label(form_frame, text="Server Address:", font=FONT_MAIN, 
                bg=THEME_COLORS['secondary'], fg=THEME_COLORS['text_dark']).pack(anchor="w")
        
        host_entry = tk.Entry(form_frame, font=FONT_MAIN, width=30, bg=THEME_COLORS['input_bg'])
        host_entry.insert(0, self.server_host)  # Default value
        host_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Server port
        tk.Label(form_frame, text="Server Port:", font=FONT_MAIN,
                bg=THEME_COLORS['secondary'], fg=THEME_COLORS['text_dark']).pack(anchor="w")
        
        port_entry = tk.Entry(form_frame, font=FONT_MAIN, width=10, bg=THEME_COLORS['input_bg'])
        port_entry.insert(0, str(self.server_port))  # Default value
        port_entry.pack(anchor="w", pady=5)
        
        # Save settings checkbox
        save_var = tk.BooleanVar(value=True)
        save_check = tk.Checkbutton(form_frame, text="Remember these settings", 
                                font=FONT_MAIN, variable=save_var,
                                bg=THEME_COLORS['secondary'], fg=THEME_COLORS['text_dark'])
        save_check.pack(anchor="w", pady=(10, 15))
        
        def apply_settings():
            try:
                host = host_entry.get().strip()
                port = int(port_entry.get().strip())
                
                if not host:
                    messagebox.showerror("Error", "Server address cannot be empty")
                    return
                    
                if port <= 0 or port > 65535:
                    messagebox.showerror("Error", "Invalid port number")
                    return
                    
                # Update client settings
                self.server_host = host
                self.server_port = port
                
                # Save settings if checked
                if save_var.get():
                    self.save_server_settings()
                    
                config_window.destroy()
                
                # Attempt connection
                self.connect_to_server()
                
            except ValueError:
                messagebox.showerror("Error", "Port must be a valid number")
        
        # Button frame
        button_frame = tk.Frame(config_window, bg=THEME_COLORS['bg_main'])
        button_frame.pack(pady=15)
        
        # Connect button
        connect_btn = tk.Button(button_frame, text="Connect ✨", font=FONT_MAIN,
                            bg=THEME_COLORS['button'], fg=THEME_COLORS['text_light'],
                            width=12, command=apply_settings)
        connect_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", font=FONT_MAIN,
                            bg=THEME_COLORS['secondary'], fg=THEME_COLORS['text_dark'],
                            width=12, command=config_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Decorative elements
        tk.Label(config_window, text="♡ ♡ ♡", font=('Arial', 16), bg=THEME_COLORS['bg_main'],
            fg=THEME_COLORS['accent']).pack(pady=10)

    def save_server_settings(self):
        """Save server settings to a local file"""
        try:
            settings = {
                'server_host': self.server_host,
                'server_port': self.server_port
            }
            
            with open('kawaii_chat_settings.json', 'w') as f:
                json.dump(settings, f)
                
        except Exception as e:
            print(f"Error saving server settings: {e}")

    def load_server_settings(self):
        """Load server settings from a local file"""
        try:
            if os.path.exists('kawaii_chat_settings.json'):
                with open('kawaii_chat_settings.json', 'r') as f:
                    settings = json.load(f)
                    
                self.server_host = settings.get('server_host', self.server_host)
                self.server_port = settings.get('server_port', self.server_port)
        except Exception as e:
            print(f"Error loading server settings: {e}")
    
    def create_login_frame(self):
        # Clear previous frames
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main login frame with decorative elements
        self.login_frame = tk.Frame(self.root, bg=THEME_COLORS['bg_main'])
        self.login_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title with hearts
        title_frame = tk.Frame(self.login_frame, bg=THEME_COLORS['bg_main'])
        title_frame.pack(pady=(50, 20))
        
        tk.Label(title_frame, text="❤️", font=('Arial', 20), bg=THEME_COLORS['bg_main']).pack(side=tk.LEFT, padx=5)
        tk.Label(title_frame, text="KawaiiChat", font=FONT_TITLE, bg=THEME_COLORS['bg_main'], 
                 fg=THEME_COLORS['text_dark']).pack(side=tk.LEFT)
        tk.Label(title_frame, text="❤️", font=('Arial', 20), bg=THEME_COLORS['bg_main']).pack(side=tk.LEFT, padx=5)
        
        # Subtitle
        tk.Label(self.login_frame, text="The cutest chat app ever!", font=('Comic Sans MS', 12, 'italic'),
                 bg=THEME_COLORS['bg_main'], fg=THEME_COLORS['text_dark']).pack(pady=(0, 30))
        
        # Login content frame
        login_content = tk.Frame(self.login_frame, bg=THEME_COLORS['secondary'], padx=40, pady=30,
                                bd=2, relief=tk.GROOVE)
        login_content.pack(padx=20, pady=20)
        
        # Username field
        tk.Label(login_content, text="Username:", font=FONT_MAIN, bg=THEME_COLORS['secondary'],
                fg=THEME_COLORS['text_dark']).grid(row=0, column=0, sticky='w', pady=(0, 10))
        self.username_entry = tk.Entry(login_content, font=FONT_MAIN, width=25, bg=THEME_COLORS['input_bg'],
                                      fg=THEME_COLORS['text_dark'])
        self.username_entry.grid(row=0, column=1, pady=(0, 10))
        
        # Password field  
        tk.Label(login_content, text="Password:", font=FONT_MAIN, bg=THEME_COLORS['secondary'],
                fg=THEME_COLORS['text_dark']).grid(row=1, column=0, sticky='w')
        self.password_entry = tk.Entry(login_content, font=FONT_MAIN, width=25, show="•", bg=THEME_COLORS['input_bg'],
                                      fg=THEME_COLORS['text_dark'])
        self.password_entry.grid(row=1, column=1)
        
        # Buttons frame
        button_frame = tk.Frame(login_content, bg=THEME_COLORS['secondary'])
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 10))
        
        # Login button
        self.login_button = tk.Button(button_frame, text="Login ✨", font=FONT_MAIN, bg=THEME_COLORS['button'],
                                     fg=THEME_COLORS['text_light'], width=12, command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        # Register button
        self.register_button = tk.Button(button_frame, text="Register 🌟", font=FONT_MAIN, bg=THEME_COLORS['button'],
                                        fg=THEME_COLORS['text_light'], width=12, command=self.show_register)
        self.register_button.pack(side=tk.LEFT, padx=5)
        
        server_btn = tk.Button(self.login_frame, text="Server Settings 🔧", font=FONT_MAIN, 
                         bg=THEME_COLORS['secondary'], fg=THEME_COLORS['text_dark'],
                         command=self.create_server_config_dialog)
        server_btn.pack(pady=10)
        
        # Add current server indicator
        tk.Label(self.login_frame, text=f"Current server: {self.server_host}:{self.server_port}", 
            font=('Comic Sans MS', 8), bg=THEME_COLORS['bg_main'],
            fg=THEME_COLORS['text_dark']).pack()
            
        # Decorative elements
        tk.Label(self.login_frame, text="✨ ✨ ✨", font=('Arial', 16), bg=THEME_COLORS['bg_main']).pack(pady=20)
        
        # Footer
        footer_frame = tk.Frame(self.login_frame, bg=THEME_COLORS['bg_main'])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        tk.Label(footer_frame, text="Made with ❤️ for kawaii chat lovers", font=('Comic Sans MS', 8),
                 bg=THEME_COLORS['bg_main'], fg=THEME_COLORS['text_dark']).pack()
    
    def show_register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title( "✨ Register for KawaiiChat ✨")
        register_window.geometry("400x350")
        register_window.configure(bg=THEME_COLORS['bg_main'])
        register_window.transient(self.root)
        register_window.grab_set()
        
        # Title
        tk.Label(register_window, text="Create Your Account", font=FONT_HEADER, bg=THEME_COLORS['bg_main'],
                fg=THEME_COLORS['text_dark']).pack(pady=(20, 30))
        
        # Form frame
        form_frame = tk.Frame(register_window, bg=THEME_COLORS['secondary'], padx=20, pady=20)
        form_frame.pack(padx=20, pady=10, fill=tk.X)
        
        # Username
        tk.Label(form_frame, text="Username:", font=FONT_MAIN, bg=THEME_COLORS['secondary'],
                fg=THEME_COLORS['text_dark']).grid(row=0, column=0, sticky='w', pady=(0, 10))
        username_entry = tk.Entry(form_frame, font=FONT_MAIN, width=25, bg=THEME_COLORS['input_bg'])
        username_entry.grid(row=0, column=1, pady=(0, 10))
        
        # Password
        tk.Label(form_frame, text="Password:", font=FONT_MAIN, bg=THEME_COLORS['secondary'],
                fg=THEME_COLORS['text_dark']).grid(row=1, column=0, sticky='w', pady=(0, 10))
        password_entry = tk.Entry(form_frame, font=FONT_MAIN, width=25, show="•", bg=THEME_COLORS['input_bg'])
        password_entry.grid(row=1, column=1, pady=(0, 10))
        
        # Display name
        tk.Label(form_frame, text="Display Name:", font=FONT_MAIN, bg=THEME_COLORS['secondary'],
                fg=THEME_COLORS['text_dark']).grid(row=2, column=0, sticky='w')
        display_name_entry = tk.Entry(form_frame, font=FONT_MAIN, width=25, bg=THEME_COLORS['input_bg'])
        display_name_entry.grid(row=2, column=1)
        
        # Register button
        def do_register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            display_name = display_name_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required!")
                return
                
            if not display_name:
                display_name = username
                
            self.register(username, password, display_name)
            register_window.destroy()
            
        tk.Button(register_window, text="Register ✨", font=FONT_MAIN, bg=THEME_COLORS['button'],
                 fg=THEME_COLORS['text_light'], width=15, command=do_register).pack(pady=20)
        
        # Decorative elements
        tk.Label(register_window, text="✨ ✨ ✨", font=('Arial', 16), bg=THEME_COLORS['bg_main']).pack(pady=10)
    
    def create_main_interface(self):
        # Clear previous frames
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create main content structure with paned window
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=THEME_COLORS['bg_main'],
                                       sashwidth=4, sashrelief=tk.RAISED)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar for contacts
        self.contacts_frame = tk.Frame(self.main_paned, bg=THEME_COLORS['bg_sidebar'], width=250)
        self.main_paned.add(self.contacts_frame, stretch="never")
        
        # Right content area for chat
        self.chat_frame = tk.Frame(self.main_paned, bg=THEME_COLORS['bg_main'])
        self.main_paned.add(self.chat_frame, stretch="always")
        
        # Set minimum widths
        self.contacts_frame.update()
        self.main_paned.paneconfig(self.contacts_frame, minsize=200)
        
        # Setup contacts sidebar
        self.setup_contacts_sidebar()
        
        # Setup empty chat area
        self.setup_empty_chat_area()
    
    def setup_contacts_sidebar(self):
        # Header with user info
        header_frame = tk.Frame(self.contacts_frame, bg=THEME_COLORS['accent'], padx=10, pady=10)
        header_frame.pack(fill=tk.X)
        
       
        # Search frame
        search_frame = tk.Frame(self.contacts_frame, bg=THEME_COLORS['bg_sidebar'], padx=10, pady=10)
        search_frame.pack(fill=tk.X)
        
        # Search entry with cute icon
        search_icon_label = tk.Label(search_frame, text="🔍", bg=THEME_COLORS['bg_sidebar'])
        search_icon_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = tk.Entry(search_frame, bg=THEME_COLORS['input_bg'], fg=THEME_COLORS['text_dark'],
                                   font=FONT_MAIN)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_contacts)
        
        # Contacts list label
        contacts_label_frame = tk.Frame(self.contacts_frame, bg=THEME_COLORS['bg_sidebar'], padx=10)
        contacts_label_frame.pack(fill=tk.X, pady=(10, 5))
        
        tk.Label(contacts_label_frame, text="Friends ♡", font=FONT_MAIN, bg=THEME_COLORS['bg_sidebar'],
                fg=THEME_COLORS['text_dark']).pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = tk.Button(contacts_label_frame, text="↻", bg=THEME_COLORS['secondary'], 
                              fg=THEME_COLORS['text_dark'], command=self.request_users_list)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Contacts list frame with scrollbar
        contacts_list_frame = tk.Frame(self.contacts_frame, bg=THEME_COLORS['bg_sidebar'], padx=10, pady=5)
        contacts_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.contacts_canvas = tk.Canvas(contacts_list_frame, bg=THEME_COLORS['bg_sidebar'], highlightthickness=0)
        scrollbar = tk.Scrollbar(contacts_list_frame, orient=tk.VERTICAL, command=self.contacts_canvas.yview)
        
        self.contacts_list_inner = tk.Frame(self.contacts_canvas, bg=THEME_COLORS['bg_sidebar'])
        
        self.contacts_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.contacts_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # User info 
        user_info_frame = tk.Frame(header_frame, bg=THEME_COLORS['accent'])
        user_info_frame.pack(fill=tk.X)

        user_label = tk.Label(user_info_frame, text=f"✨ {self.current_user['display_name']} ✨", 
                            font=FONT_HEADER, bg=THEME_COLORS['accent'], fg=THEME_COLORS['text_light'])
        user_label.pack(side=tk.LEFT, pady=5, padx=5)

        # # Add profile button
        # profile_button = tk.Button(user_info_frame, text="✏️ Profile", font=FONT_MAIN, 
        #                         bg=THEME_COLORS['secondary'], fg=THEME_COLORS['text_dark'],
        #                         command=self.open_profile_settings)
        # profile_button.pack(side=tk.RIGHT, pady=5, padx=5)
        
        canvas_frame = self.contacts_canvas.create_window((0, 0), window=self.contacts_list_inner, anchor="nw")
        
        # Configure canvas scroll area
        def configure_scroll_region(event):
            self.contacts_canvas.configure(scrollregion=self.contacts_canvas.bbox("all"))
            
        self.contacts_list_inner.bind("<Configure>", configure_scroll_region)
        
        # Make canvas expand with frame
        def on_canvas_resize(event):
            self.contacts_canvas.itemconfig(canvas_frame, width=event.width)
            
        self.contacts_canvas.bind("<Configure>", on_canvas_resize)
        
        # Add mousewheel scrolling
        self.bind_mousewheel(self.contacts_canvas, self.contacts_list_inner)

        # Also bind mousewheel for all child widgets to ensure scrolling works when hovering over contacts
        for child in self.contacts_list_inner.winfo_children():
            child.bind("<MouseWheel>", lambda event: self.contacts_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            child.bind("<Button-4>", lambda event: self.contacts_canvas.yview_scroll(-1, "units"))
            child.bind("<Button-5>", lambda event: self.contacts_canvas.yview_scroll(1, "units"))
                
        # Populate contacts
        self.update_contacts_list()
    
    def update_contacts_list(self): #on refresh
        # Clear previous contacts
        for widget in self.contacts_list_inner.winfo_children():
            widget.destroy()
            
        # Sort users: online first, then by name
        sorted_users = sorted(self.user_list, key=lambda x: (x['status'] != 'online', x['display_name'].lower()))
        
        for user in sorted_users:
            # Skip current user
            if user['id'] == self.current_user['id']:
                continue
                
            # Create contact frame
            contact_frame = tk.Frame(self.contacts_list_inner, bg=THEME_COLORS['bg_sidebar'], padx=5, pady=5)
            contact_frame.pack(fill=tk.X, pady=2)
            
            # Status indicator (green dot for online, gray for offline)
            status_color = "#4CAF50" if user['status'] == 'online' else "#FF0000"
            status_indicator = tk.Canvas(contact_frame, width=10, height=10, bg=THEME_COLORS['bg_sidebar'], 
                                      highlightthickness=0)
            status_indicator.create_oval(2, 2, 8, 8, fill=status_color, outline="")
            status_indicator.pack(side=tk.LEFT, padx=(0, 5))
            
            # Display name
            display_name = user.get('display_name') or user['username']
            name_label = tk.Label(contact_frame, text=display_name, font=FONT_MAIN, bg=THEME_COLORS['bg_sidebar'],
                                fg=THEME_COLORS['text_dark'], anchor='w')
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Make entire frame clickable
            contact_frame.bind("<Button-1>", lambda e, u=user: self.select_chat_user(u))
            name_label.bind("<Button-1>", lambda e, u=user: self.select_chat_user(u))
            
            # Add hover effect
            def on_enter(e, frame=contact_frame):
                frame.config(bg=THEME_COLORS['secondary'])
                for child in frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=THEME_COLORS['secondary'])
                    elif isinstance(child, tk.Canvas):
                        child.config(bg=THEME_COLORS['secondary'])
                        
            def on_leave(e, frame=contact_frame):
                frame.config(bg=THEME_COLORS['bg_sidebar'])
                for child in frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=THEME_COLORS['bg_sidebar'])
                    elif isinstance(child, tk.Canvas):
                        child.config(bg=THEME_COLORS['bg_sidebar'])
            
            contact_frame.bind("<Enter>", on_enter)
            contact_frame.bind("<Leave>", on_leave)
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)
    
    def filter_contacts(self, event=None):
        if not hasattr(self, 'contacts_list_inner'):
            return  # Exit if the attribute doesn't exist yet

        search_text = self.search_entry.get().lower().strip()
        
        for widget in self.contacts_list_inner.winfo_children():
            widget.pack_forget()
            
        for widget in self.contacts_list_inner.winfo_children():
            name_label = None
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    name_label = child
                    break
                    
            if name_label and search_text in name_label.cget('text').lower():
                widget.pack(fill=tk.X, pady=2)

    
    def setup_empty_chat_area(self):
        # Header frame
        self.chat_header = tk.Frame(self.chat_frame, bg=THEME_COLORS['accent'], height=60)
        self.chat_header.pack(fill=tk.X)
        
        # Empty header content
        tk.Label(self.chat_header, text="Select a friend to chat! ♡", font=FONT_HEADER, 
                bg=THEME_COLORS['accent'], fg=THEME_COLORS['text_light']).pack(pady=15)
        
        # Empty chat content with cute graphic
        empty_content = tk.Frame(self.chat_frame, bg=THEME_COLORS['bg_main'])
        empty_content.pack(fill=tk.BOTH, expand=True)
        
        # Cute message
        tk.Label(empty_content, text="✧･ﾟ: *✧･ﾟ:*", font=('Comic Sans MS', 20),
                bg=THEME_COLORS['bg_main'], fg=THEME_COLORS['accent']).pack(pady=(100, 10))
        
        tk.Label(empty_content, text="No messages yet!", font=FONT_HEADER,
                bg=THEME_COLORS['bg_main'], fg=THEME_COLORS['text_dark']).pack()
        
        tk.Label(empty_content, text="Select a friend from the list to start chatting", font=FONT_MAIN,
                bg=THEME_COLORS['bg_main'], fg=THEME_COLORS['text_dark']).pack(pady=10)
        
        tk.Label(empty_content, text="*:･ﾟ✧*:･ﾟ✧", font=('Comic Sans MS', 20),
                bg=THEME_COLORS['bg_main'], fg=THEME_COLORS['accent']).pack(pady=10)
    
    def setup_chat_area(self, user):
        # Clear previous chat content
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
            
        # Header with user info
        self.chat_header = tk.Frame(self.chat_frame, bg=THEME_COLORS['accent'], height=60)
        self.chat_header.pack(fill=tk.X)
        
        # User status indicator
        header_content = tk.Frame(self.chat_header, bg=THEME_COLORS['accent'])
        header_content.pack(fill=tk.X, pady=10, padx=15)
        
        # Status indicator
        status_color = "#4CAF50" if user['status'] == 'online' else "#FF0000"
        status_indicator = tk.Canvas(header_content, width=12, height=12, bg=THEME_COLORS['accent'], 
                                  highlightthickness=0)
        status_indicator.create_oval(2, 2, 10, 10, fill=status_color, outline="")
        status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        
        # User name
        tk.Label(header_content, text=user['display_name'], font=FONT_HEADER,
                bg=THEME_COLORS['accent'], fg=THEME_COLORS['text_light']).pack(side=tk.LEFT)
        
        # Chat messages area
        chat_content = tk.Frame(self.chat_frame, bg=THEME_COLORS['bg_main'])
        chat_content.pack(fill=tk.BOTH, expand=True)
        
        # Messages canvas with scrollbar
        self.messages_canvas = tk.Canvas(chat_content, bg=THEME_COLORS['bg_main'], highlightthickness=0)
        messages_scrollbar = tk.Scrollbar(chat_content, orient=tk.VERTICAL, command=self.messages_canvas.yview)
        
        self.messages_frame = tk.Frame(self.messages_canvas, bg=THEME_COLORS['bg_main'], padx=20, pady=20)
        
        self.messages_canvas.configure(yscrollcommand=messages_scrollbar.set)
        messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        messages_window = self.messages_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        
        # Configure canvas scroll area
        def configure_messages_scroll(event):
            self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
            
        self.messages_frame.bind("<Configure>", configure_messages_scroll)
        
        # Make canvas expand with frame
        def on_messages_canvas_resize(event):
            self.messages_canvas.itemconfig(messages_window, width=event.width)
            
        self.messages_canvas.bind("<Configure>", on_messages_canvas_resize)
        self.bind_mousewheel(self.messages_canvas, self.messages_frame)
        
        # Input area at bottom
        input_area = tk.Frame(self.chat_frame, bg=THEME_COLORS['bg_main'], padx=15, pady=15)
        input_area.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Text input with emojis button
        text_input_frame = tk.Frame(input_area, bg=THEME_COLORS['bg_main'])
        text_input_frame.pack(fill=tk.X)
        
        # Emoji button
        emoji_button = tk.Button(text_input_frame, text="😊", font=('Arial', 16), bg=THEME_COLORS['secondary'],
                               command=self.show_emoji_picker)
        emoji_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Text input
        self.message_input = tk.Text(text_input_frame, height=3, width=1, font=FONT_MAIN, 
                                   bg=THEME_COLORS['input_bg'], fg=THEME_COLORS['text_dark'],
                                   wrap=tk.WORD)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Send button
        send_button = tk.Button(text_input_frame, text="Send ✨", font=FONT_MAIN, bg=THEME_COLORS['button'],
                              fg=THEME_COLORS['text_light'], command=self.send_message)
        send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to send
        self.message_input.bind("<Return>", lambda e: self.send_message() or "break")
        
        # Load and display existing messages
        self.display_messages(user['id'])
        
        # Scroll to bottom of messages
        self.scroll_to_bottom()
    
    def show_emoji_picker(self):
        emoji_window = tk.Toplevel(self.root)
        emoji_window.title("Emoji Picker")
        emoji_window.geometry("300x200")
        emoji_window.configure(bg=THEME_COLORS['bg_main'])
        emoji_window.transient(self.root)
        
        # Common emojis
        emojis = ["😊", "😂", "🥰", "😍", "👍", "❤️", "✨", "🌟", "🎉", "🌸", "💕", "😭", "🥺", "😘", 
                 "🙏", "🔥", "💯", "🤣", "😅", "😁", "🥳", "🤔", "🙄", "😴"]
        
        emoji_frame = tk.Frame(emoji_window, bg=THEME_COLORS['bg_main'], padx=10, pady=10)
        emoji_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create grid of emoji buttons
        row, col = 0, 0
        for emoji in emojis:
            def add_emoji(e=emoji):
                self.message_input.insert(tk.INSERT, e)
                emoji_window.destroy()
                
            btn = tk.Button(emoji_frame, text=emoji, font=('Arial', 16), bg=THEME_COLORS['bg_main'],
                          command=add_emoji)
            btn.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col > 5:  # 6 emojis per row
                col = 0
                row += 1
    
    def bind_mousewheel(self, canvas, frame=None):
        """Add mousewheel scrolling support to a canvas more efficiently"""
        # Instead of binding to every child widget, bind only to the canvas and frame
        
        def _on_mousewheel(event):
            # Use a fixed scroll amount for better performance
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # Return "break" to prevent event propagation
            return "break"
        
        def _on_mousewheel_linux_up(event):
            canvas.yview_scroll(-1, "units")
            return "break"
            
        def _on_mousewheel_linux_down(event):
            canvas.yview_scroll(1, "units")
            return "break"
        
        # Bind to canvas
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", _on_mousewheel_linux_up)
        canvas.bind("<Button-5>", _on_mousewheel_linux_down)
        
        # If frame is provided, bind to it as well
        if frame:
            frame.bind("<MouseWheel>", _on_mousewheel)
            frame.bind("<Button-4>", _on_mousewheel_linux_up)
            frame.bind("<Button-5>", _on_mousewheel_linux_down)
        
    def display_messages(self, user_id):
        # Clear previous messages
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
            
        # Check if we have messages for this user
        if user_id not in self.chat_messages:
            self.chat_messages[user_id] = []
            
        # Get messages, limit to most recent MAX_MESSAGES if there are too many
        MAX_MESSAGES = 50  
        messages = self.chat_messages[user_id]
        if len(messages) > MAX_MESSAGES:
            # Add a "load more" button at the top
            load_more_frame = tk.Frame(self.messages_frame, bg=THEME_COLORS['bg_main'])
            load_more_frame.pack(fill=tk.X, pady=5)
            
            load_more_btn = tk.Button(load_more_frame, text="Load older messages...", 
                                    font=FONT_MAIN, bg=THEME_COLORS['secondary'],
                                    command=lambda: self.load_more_messages(user_id))
            load_more_btn.pack(pady=5)
            
            # Display only the most recent messages
            messages_to_display = messages[-MAX_MESSAGES:]
        else:
            messages_to_display = messages
                
        # Display messages
        for msg in messages_to_display:
            self.display_message(msg)
        
    def load_more_messages(self, user_id):
        current_count = len(self.messages_frame.winfo_children())
        # Load another batch (e.g. 50 more messages)
        batch_size = 50
        start_idx = max(0, len(self.chat_messages[user_id]) - current_count - batch_size)
        end_idx = len(self.chat_messages[user_id]) - current_count
        
        # Clear existing messages
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
            
        # Display older messages + current messages
        messages_to_display = self.chat_messages[user_id][start_idx:]
        
        for msg in messages_to_display:
            self.display_message(msg)
    
    def display_message(self, msg):
        # Determine if this is sent or received message
        is_sent = msg['sender_id'] == self.current_user['id']
        
        # Message frame
        message_frame = tk.Frame(self.messages_frame, bg=THEME_COLORS['bg_main'])
        message_frame.pack(fill=tk.X, pady=5)
        
        # Position left or right based on sender
        if is_sent:
            spacer = tk.Frame(message_frame, width=100, bg=THEME_COLORS['bg_main'])
            spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bubble background
        bubble_bg = THEME_COLORS['accent'] if is_sent else THEME_COLORS['secondary']
        bubble_fg = THEME_COLORS['text_light'] if is_sent else THEME_COLORS['text_dark']
        
        # Message content
        bubble = tk.Frame(message_frame, bg=bubble_bg, padx=10, pady=8, bd=1, relief=tk.RAISED)
        bubble.pack(side=tk.RIGHT if is_sent else tk.LEFT, anchor='e' if is_sent else 'w')
        
        # Message text
        msg_text = tk.Label(bubble, text=msg['content'], font=FONT_MESSAGE, bg=bubble_bg, fg=bubble_fg,
                          justify=tk.LEFT, wraplength=400)
        msg_text.pack(anchor='e' if is_sent else 'w')
        
        # Timestamp
        time_str = self.format_timestamp(msg['timestamp'])
        time_label = tk.Label(bubble, text=time_str, font=('Comic Sans MS', 7), bg=bubble_bg,
                           fg=bubble_fg)
        time_label.pack(anchor='e', pady=(3, 0))
        
        if not is_sent:
            spacer = tk.Frame(message_frame, width=100, bg=THEME_COLORS['bg_main'])
            spacer.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    
    def format_timestamp(self, timestamp):
        if isinstance(timestamp, str):
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
            except ValueError:
                return timestamp
        else:
            dt = timestamp
            
        now = datetime.datetime.now()
        
        if dt.date() == now.date():
            # Today, show time
            return dt.strftime("%H:%M")
        elif (now.date() - dt.date()).days == 1:
            # Yesterday
            return f"Yesterday {dt.strftime('%H:%M')}"
        else:
            # Another day
            return dt.strftime("%Y-%m-%d %H:%M")
    
    def scroll_to_bottom(self):
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
    
    def select_chat_user(self, user):
        self.current_chat_user = user
        self.setup_chat_area(user)
        # Request chat history with this user
        self.send_to_server({
            'type': 'get_chat_history',
            'user_id': user['id']
        })
    
    def send_message(self):
        if not self.current_chat_user:
            return
            
        message = self.message_input.get("1.0", "end-1c").strip()
        if not message:
            return
            
        # Clear input
        self.message_input.delete("1.0", tk.END)
        
        # Create message object
        now = datetime.datetime.now()
        msg = {
            'sender_id': self.current_user['id'],
            'receiver_id': self.current_chat_user['id'],
            'content': message,
            'timestamp': now.isoformat()
        }
        
        # Add to local messages
        if self.current_chat_user['id'] not in self.chat_messages:
            self.chat_messages[self.current_chat_user['id']] = []
            
        self.chat_messages[self.current_chat_user['id']].append(msg)
        
        # Display message
        self.display_message(msg)
        
        # Scroll to bottom
        self.scroll_to_bottom()
        
        # Send to server
        self.send_to_server({
            'type': 'message',
            'receiver_id': self.current_chat_user['id'],
            'content': message
        })
    
      
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(60)#ncrease timeout to 60conds
            self.socket.connect((self.server_host, self.server_port))
            # After connection is established, set to None for blocking mode
            self.socket.settimeout(None)
            self.connected = True
            
            if not hasattr(self, '_listener_started'):
                threading.Thread(target=self.listen_for_messages, daemon=True).start()
                print(f"Started message listener thread for {self.server_host}:{self.server_port}")
                self._listener_started = True
            
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            return False
        
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required!")
            return
        
        
        self._password = password
        
        # Connect to server if needed
        if not self.connected and not self.connect_to_server():
            return
            
        # Send login request
        self.send_to_server({
            'type': 'login',
            'username': username,
            'password': password
        })
    
    def register(self, username, password, display_name=None):
        # Connect to server if needed
        if not self.connected and not self.connect_to_server():
            return
            
        # Send registration request
        self.send_to_server({
            'type': 'register',
            'username': username,
            'password': password,
            'display_name': display_name
        })
    
    def request_users_list(self):
        if not self.connected:
            return
            
        self.send_to_server({
            'type': 'get_users'
        })
    
    def send_to_server(self, data):
        if not self.connected or not self.socket:
            print("Cannot send data - not connected")
            self.root.after(1000, self.attempt_reconnect)
            return False
            
        try:
            # Special handling for larger data like images
            is_large_data = 'image_data' in data and len(data['image_data']) > 100000
            
            if is_large_data:
                # Set a longer timeout for image uploads
                self.socket.settimeout(60)  # 60 second timeout
                
            # Add newline character to properly delimit messages
            self.socket.sendall((json.dumps(data) + '\n').encode('utf-8'))
            
            if is_large_data:
                # Reset timeout to default
                self.socket.settimeout(None)
                
            return True
        except BrokenPipeError:
            print("Connection lost: broken pipe")
            self.connected = False
            self.root.after(1000, self.attempt_reconnect)
            return False
        except ConnectionResetError:
            print("Connection reset by peer")
            self.connected = False
            self.root.after(1000, self.attempt_reconnect)
            return False
        except Exception as e:
            print(f"Could not send data to server: {e}")
            self.connected = False
            self.root.after(1000, self.attempt_reconnect)
            return False
    
    def process_incoming_message(self, message):
        message_type = message.get('type')
        
        if message_type == 'login_response':
            if message.get('success'):
                self.current_user = message.get('user')
                self.user_list = message.get('users', [])               
                
                
                # Initialize chat messages dictionary for all users
                for user in self.user_list:
                    if user['id'] != self.current_user['id'] and user['id'] not in self.chat_messages:
                        self.chat_messages[user['id']] = []
                
                # Start message listening thread ONCE
                if not hasattr(self, '_listener_started'):
                    threading.Thread(target=self.listen_for_messages, daemon=True).start()
                    print("Started message listener thread in login response")
                    self._listener_started = True
                
                # Process unread messages
                unread_messages = message.get('unread_messages', [])
                
                for msg in unread_messages:
                    sender_id = msg['sender_id']
                    if sender_id not in self.chat_messages:
                        self.chat_messages[sender_id] = []
                        
                    # Convert to our message format
                    formatted_msg = {
                        'sender_id': sender_id,
                        'receiver_id': self.current_user['id'],
                        'content': msg['message'],
                        'timestamp': msg['sent_at']
                    }
                    
                    self.chat_messages[sender_id].append(formatted_msg)
                
                # Switch to main interface
                self.create_main_interface()
                
                # Show notification for unread messages
                if unread_messages:
                    messagebox.showinfo("Unread Messages", 
                                      f"You have {len(unread_messages)} unread messages!")
            else:
                messagebox.showerror("Login Failed", message.get('message', "Invalid credentials"))
                
        elif message_type == 'register_response':
            if message.get('success'):
                messagebox.showinfo("Registration Successful", 
                                  "Your account has been created! You can now login.")
                # Start message listening thread ONCE (optional, if you directly enter UI after register)
                if not hasattr(self, '_listener_started'):
                    threading.Thread(target=self.listen_for_messages, daemon=True).start()
                    print("Started in register")
                    self._listener_started = True
            else:
                messagebox.showerror("Registration Failed", 
                                   message.get('message', "Registration failed"))
                
        elif message_type == 'users_list':
            self.user_list = message.get('users', [])
            self.update_contacts_list()
        
        elif message_type == 'chat_history':
            user_id = message.get('user_id')
            messages = message.get('messages', [])
            
            print(f"Received {len(messages)} messages in chat history")
            
            # Clear existing messages for this user
            self.chat_messages[user_id] = []
            
            # Process and store all messages
            for msg in messages:
                formatted_msg = {
                    'sender_id': msg['sender_id'],
                    'receiver_id': msg['receiver_id'],
                    'content': msg['message'],
                    'timestamp': msg['sent_at']
                }
                self.chat_messages[user_id].append(formatted_msg)
            
            # If we're currently viewing this chat, refresh the display
            if self.current_chat_user and self.current_chat_user['id'] == user_id:
                # Clean the messages frame first
                for widget in self.messages_frame.winfo_children():
                    widget.destroy()
                # Now display messages
                self.display_messages(user_id)
                self.scroll_to_bottom()
            
        elif message_type == 'new_message':
            sender = message.get('sender')
            content = message.get('content')
            timestamp = message.get('timestamp')
            
            if sender['id'] not in self.chat_messages:
                self.chat_messages[sender['id']] = []
                
            # Add message to chat
            msg = {
                'sender_id': sender['id'],
                'receiver_id': self.current_user['id'],
                'content': content,
                'timestamp': timestamp
            }
            
            self.chat_messages[sender['id']].append(msg)
            
            # If we're currently chatting with this user, display the message
            if self.current_chat_user and self.current_chat_user['id'] == sender['id']:
                self.display_message(msg)
                # Scroll to bottom
                self.scroll_to_bottom()
            else:
                # Show notification
                messagebox.showinfo("New Message", f"New message from {sender['display_name']}")
        
        elif message_type == 'heartbeat':
            # Respond to server heartbeat
            self.send_to_server({
                'type': 'heartbeat_response'
            })
            
       
            
    def listen_for_messages(self):
        buffer = ""
        
        while self.connected:
            try:
                # Set a timeout for receiving data
                self.socket.settimeout(10) # 30 second timeout
                data = self.socket.recv(4096).decode('utf-8')
                # Reset timeout after successful receive
                self.socket.settimeout(None)
                
                if not data:
                    self.connected = False
                    print("Connection lost: no data received")
                    self.root.after(5000, self.attempt_reconnect)
                    break
                    
                buffer += data
                
                # Process complete messages
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        message = json.loads(line)
                        # Process in main thread to avoid tkinter issues
                        self.root.after(0, lambda m=message: self.process_incoming_message(m))
                    except json.JSONDecodeError:
                        print("Error decoding JSON message")
                        
            except socket.timeout:
                # Socket timeout - send heartbeat to check connection
                print("Socket timeout, sending heartbeat...")
                try:
                    self.send_to_server({'type': 'client_heartbeat'})
                    print("Heartbeat sent successfully")
                except Exception as e:
                    self.connected = False
                    print(f"Connection lost during heartbeat: {e}")
                    self.root.after(5000, self.attempt_reconnect)
                    break
                    
            except ConnectionResetError:
                self.connected = False
                print("Connection reset by server")
                self.root.after(5000, self.attempt_reconnect)
                break
                
            except ConnectionAbortedError:
                self.connected = False
                print("Connection aborted")
                self.root.after(5000, self.attempt_reconnect)
                break
                
            except Exception as e:
                self.connected = False
                print(f"Error receiving messages: {e}")
                self.root.after(5000, self.attempt_reconnect)
                break
            
    def attempt_reconnect(self):
        """Attempt to reconnect to the server after connection loss"""
        if self.connected:
            return  # Already reconnected somehow lol
            
        print(f"Attempting to reconnect to {self.server_host}:{self.server_port}...")
        
        try:
            # Create new socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            
            # Start new listener thread
            threading.Thread(target=self.listen_for_messages, daemon=True).start()
            print("Reconnected successfully. Starting new message listener.")
            
            # Re-authenticate if we have user credentials
            if self.current_user:
                print(f"Re-authenticating as {self.current_user['username']}...")
                self.send_to_server({
                    'type': 'login',
                    'username': self.current_user['username'],
                    'password': self._password if hasattr(self, '_password') else '' #fixed
                })
                
                
                messagebox.showinfo("Reconnected", 
                                "Connection to server re-established.\nYou may need to refresh your contacts.")
                    
        except Exception as e:
            print(f"Reconnection failed: {e}")
            # Schedule another attempt
            self.root.after(10000, self.attempt_reconnect)  # Try again after 10 seconds

if __name__ == "__main__":
    #high dpi awareness, just to check
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    root = tk.Tk()
    app = KawaiiChatClient(root)
    root.mainloop()