import customtkinter as ctk
from pypresence import Presence
import time
import threading
import sys
import json
import os
import tkinter as tk # For context menu

# --- Constants & Configuration ---
APP_TITLE = "KitsuneRPC by Renji"
GEOMETRY = "900x600"

#Dark Theme Colors
COLOR_BG_SIDEBAR = "#1f1f1f"      # Sidebar Dark Grey
COLOR_BG_MAIN = "#121212"         # Main Content Black/Very Dark Grey
COLOR_ACCENT = "#3b82f6"          # Blue
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_SUB = "#aaaaaa"
COLOR_HOVER = "#2c2c2c"           # Sidebar Hover
COLOR_SELECTED = "#282828"        # Active Preset BG
COLOR_BORDER = "#333333"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue") # We will override mostly

class PresetManager:
    """Manages loading, saving, and manipulating presets."""
    def __init__(self, filepath="presets.json"):
        self.filepath = filepath
        self.presets = {}
        self.active_id = None
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    self.presets = data.get("presets", {})
                    self.active_id = data.get("active_id", None)
            except Exception as e:
                print(f"Failed to load presets: {e}")
        
        # Ensure at least one preset exists
        if not self.presets:
            self.create_preset("Default Preset")

    def save(self):
        data = {
            "presets": self.presets,
            "active_id": self.active_id
        }
        try:
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save presets: {e}")

    def create_preset(self, name):
        new_id = str(int(time.time())) # Simple ID
        self.presets[new_id] = {
            "name": name,
            "client_id": "",
            "state": "",
            "details": "",
            "large_image": "",
            "large_text": "",
            "small_image": "",
            "small_text": "",
            "buttons": [],
            "timer_enabled": False
        }
        self.active_id = new_id
        self.save()
        return new_id

    def duplicate_preset(self, preset_id):
        if preset_id in self.presets:
            new_id = str(int(time.time()))
            new_data = self.presets[preset_id].copy()
            new_data["name"] = f"{new_data['name']} Copy"
            self.presets[new_id] = new_data
            self.save()
            return new_id
        return None

    def delete_preset(self, preset_id):
        if preset_id in self.presets and len(self.presets) > 1:
            del self.presets[preset_id]
            # If we deleted the active one, pick another
            if self.active_id == preset_id:
                self.active_id = list(self.presets.keys())[0]
            self.save()
            return True
        return False

    def get_active_preset(self):
        if self.active_id and self.active_id in self.presets:
            return self.presets[self.active_id]
        # Fallback
        if self.presets:
            key = list(self.presets.keys())[0]
            self.active_id = key
            return self.presets[key]
        return None
        
    def update_active_preset(self, data):
        if self.active_id:
            self.presets[self.active_id].update(data)
            self.save()

class RPCApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title(APP_TITLE)
        self.geometry(GEOMETRY)
        self.configure(fg_color=COLOR_BG_MAIN)
        
        # Variables
        self.presets_mgr = PresetManager()
        self.rpc = None
        self.start_time = None
        self.is_connected = False
        self.buttons_list = [] # List of dicts for buttons

        # Layout Logic: 2 Columns
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, fg_color=COLOR_BG_SIDEBAR, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Force width

        self._setup_sidebar()

        # --- RIGHT MAIN CONTENT ---
        self.main_area = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self._setup_main_area()

        # Initial Load
        self.refresh_sidebar_list()
        self.load_preset_into_ui()
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_sidebar(self):
        # App Title / Client ID Label
        self.brand_label = ctk.CTkLabel(
            self.sidebar, 
            text="KitsuneRPC", 
            font=("Arial", 18, "bold"), 
            text_color=COLOR_TEXT_MAIN,
            anchor="w"
        )
        self.brand_label.pack(fill="x", padx=20, pady=(20, 10))

        # "Preset" Label
        ctk.CTkLabel(self.sidebar, text="Preset", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_SUB, anchor="w").pack(fill="x", padx=20, pady=(10, 5))

        # Scrollable Preset List
        self.preset_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", label_text="")
        self.preset_scroll.pack(expand=True, fill="both", padx=5, pady=5)

        # New Preset Button ("Button on bottom")
        self.new_preset_btn = ctk.CTkButton(
            self.sidebar,
            text="+ New Preset",
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_ACCENT,
            hover_color=COLOR_HOVER,
            command=self.add_new_preset
        )
        self.new_preset_btn.pack(fill="x", padx=15, pady=15)

    def _setup_main_area(self):
        # Top Bar (Title + Update)
        self.top_bar = ctk.CTkFrame(self.main_area, fg_color="transparent", height=60)
        self.top_bar.pack(fill="x", pady=(0, 20))
        
        # Client ID Input (Hidden/Safety) - Top Left of main area
        self.client_id_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.client_id_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.client_id_frame, text="Client ID", text_color=COLOR_TEXT_SUB, font=("Arial", 10)).pack(anchor="w")
        self.client_id_entry = ctk.CTkEntry(
            self.client_id_frame, 
            width=180, 
            fg_color=COLOR_HOVER, 
            border_width=0, 
            text_color=COLOR_TEXT_MAIN,
            show="*" # Masked for safety
        )
        self.client_id_entry.pack(anchor="w")

        # Connection Controls
        self.status_dot = ctk.CTkLabel(self.top_bar, text="●", font=("Arial", 24), text_color="#ef4444")
        self.status_dot.pack(side="left", padx=(15, 0), pady=12)

        self.connect_btn = ctk.CTkButton(
            self.top_bar,
            text="Connect",
            width=80,
            fg_color=COLOR_HOVER,
            hover_color="#333",
            text_color=COLOR_ACCENT,
            command=self.connect_rpc
        )
        self.connect_btn.pack(side="left", padx=10, pady=(16, 12)) # adjusted pady for alignment

        # Update Presence (Center Top)
        self.update_btn = ctk.CTkButton(
            self.top_bar,
            text="Update Presence",
            fg_color=COLOR_ACCENT,
            hover_color="#333",
            text_color="white",
            width=140,
            height=32,
            corner_radius=6,
            command=self.update_presence
        )
        self.update_btn.pack(side="right", pady=24)

        # Content Scroll
        self.content_scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        self.content_scroll.pack(expand=True, fill="both")

        # --- Editor Fields ---
        
        # 1. Status Details (Details/State)
        self._add_header("Status")
        self.details_entry = self._create_field("Details", "Describe what you are doing...")
        self.state_entry = self._create_field("State", "Your current status...")

        # 2. Assets
        self._add_header("Assets (Visuals)")
        self.large_img_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.large_img_frame.pack(fill="x", pady=5)
        self.large_image_key = self._create_field_in_frame(self.large_img_frame, "Large Image Key/URL", "Image Key or URL", 0)
        self.large_image_text = self._create_field_in_frame(self.large_img_frame, "Tooltip Text", "Text when hovering image", 1)

        self.small_img_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.small_img_frame.pack(fill="x", pady=5)
        self.small_image_key = self._create_field_in_frame(self.small_img_frame, "Small Image Key/URL", "Image Key or URL", 0)
        self.small_image_text = self._create_field_in_frame(self.small_img_frame, "Tooltip Text", "Text when hovering image", 1)

        # 3. Buttons
        self._add_header("Interactive Buttons")
        self.btn1_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.btn1_frame.pack(fill="x", pady=5)
        self.btn1_label = self._create_field_in_frame(self.btn1_frame, "Button 1 Label", "Label", 0)
        self.btn1_url = self._create_field_in_frame(self.btn1_frame, "Button 1 URL", "https://...", 1)

        self.btn2_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.btn2_frame.pack(fill="x", pady=5)
        self.btn2_label = self._create_field_in_frame(self.btn2_frame, "Button 2 Label", "Label", 0)
        self.btn2_url = self._create_field_in_frame(self.btn2_frame, "Button 2 URL", "https://...", 1)

    def _add_header(self, text):
        ctk.CTkLabel(self.content_scroll, text=text, font=("Arial", 15, "bold"), text_color=COLOR_ACCENT).pack(anchor="w", padx=5, pady=(20, 5))

    def _create_field(self, label_text, placeholder_text):
        container = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        container.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(container, text=label_text, font=("Arial", 12), text_color=COLOR_TEXT_SUB).pack(anchor="w")
        
        entry = ctk.CTkEntry(
            container,
            placeholder_text=placeholder_text,
            placeholder_text_color="#a0a0a0", 
            height=35,
            fg_color=COLOR_HOVER,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MAIN
        )
        entry.pack(fill="x", pady=(2, 0))
        return entry
    
    def _create_field_in_frame(self, frame, label_text, placeholder_text, col):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame, text=label_text, font=("Arial", 12), text_color=COLOR_TEXT_SUB).grid(row=0, column=col, sticky="w", padx=5)
        
        entry = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder_text,
            placeholder_text_color="#a0a0a0", 
            height=35,
            fg_color=COLOR_HOVER,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MAIN
        )
        entry.grid(row=1, column=col, sticky="ew", padx=5, pady=(2, 0))
        return entry

    # --- Preset Management & Sidebar Logic ---

    def refresh_sidebar_list(self):
        # Clear existing
        for widget in self.preset_scroll.winfo_children():
            widget.destroy()

        active = self.presets_mgr.get_active_preset()
        
        for pid, pdata in self.presets_mgr.presets.items():
            is_active = (pid == self.presets_mgr.active_id)
            color = COLOR_SELECTED if is_active else "transparent"
            text_color = COLOR_ACCENT if is_active else COLOR_TEXT_MAIN

            btn = ctk.CTkButton(
                self.preset_scroll,
                text=pdata["name"],
                fg_color=color,
                hover_color=COLOR_HOVER,
                text_color=text_color,
                anchor="w",
                height=35,
                command=lambda i=pid: self.switch_to_preset(i)
            )
            btn.pack(fill="x", pady=1)

            # Bind Right Click (Context Menu)
            btn.bind("<Button-3>", lambda event, i=pid: self.show_context_menu(event, i))

    def switch_to_preset(self, preset_id):
        # Save current UI state to the OLD active preset before switching
        self.save_current_ui_to_preset()
        
        # Switch ID
        self.presets_mgr.active_id = preset_id
        self.presets_mgr.save()
        
        # Refresh UI
        self.refresh_sidebar_list()
        self.load_preset_into_ui()

        # Update Brand Label to show active preset name
        self.brand_label.configure(text=self.presets_mgr.presets[preset_id]['name'])

    def add_new_preset(self):
        self.save_current_ui_to_preset() # Save current work first
        self.presets_mgr.create_preset("New Preset")
        self.refresh_sidebar_list()
        self.load_preset_into_ui()

    def show_context_menu(self, event, preset_id):
        # Create a standard tkinter Menu
        menu = tk.Menu(self, tearoff=0, bg=COLOR_BG_SIDEBAR, fg=COLOR_TEXT_MAIN, activebackground=COLOR_ACCENT)
        menu.add_command(label="Duplicate", command=lambda: self.duplicate_preset_action(preset_id))
        menu.add_command(label="Rename", command=lambda: self.rename_preset_action(preset_id))
        menu.add_separator()
        menu.add_command(label="Delete", command=lambda: self.delete_preset_action(preset_id))
        
        menu.tk_popup(event.x_root, event.y_root)

    def duplicate_preset_action(self, pid):
        self.presets_mgr.duplicate_preset(pid)
        self.refresh_sidebar_list()

    def delete_preset_action(self, pid):
        if self.presets_mgr.delete_preset(pid):
            self.refresh_sidebar_list()
            self.load_preset_into_ui()

    def rename_preset_action(self, pid):
        # Simple input dialog
        dialog = ctk.CTkInputDialog(text="Enter new name:", title="Rename Preset")
        new_name = dialog.get_input()
        if new_name:
            self.presets_mgr.presets[pid]['name'] = new_name
            self.presets_mgr.save()
            self.refresh_sidebar_list()

    # --- Data Binding ---

    def load_preset_into_ui(self):
        data = self.presets_mgr.get_active_preset()
        if not data: return

        # Helper to set entry text
        def set_text(entry, text):
            entry.delete(0, "end")
            if text:
                entry.insert(0, text)
            else:
                entry._activate_placeholder()

        set_text(self.client_id_entry, data.get("client_id", ""))
        set_text(self.details_entry, data.get("details", ""))
        set_text(self.state_entry, data.get("state", ""))
        
        set_text(self.large_image_key, data.get("large_image", ""))
        set_text(self.large_image_text, data.get("large_text", ""))
        set_text(self.small_image_key, data.get("small_image", ""))
        set_text(self.small_image_text, data.get("small_text", ""))

        btns = data.get("buttons", [])
        set_text(self.btn1_label, btns[0]["label"] if len(btns) > 0 else "")
        set_text(self.btn1_url, btns[0]["url"] if len(btns) > 0 else "")
        set_text(self.btn2_label, btns[1]["label"] if len(btns) > 1 else "")
        set_text(self.btn2_url, btns[1]["url"] if len(btns) > 1 else "")

    def save_current_ui_to_preset(self):
        # Gather data from UI
        btns = []
        b1l, b1u = self.btn1_label.get().strip(), self.btn1_url.get().strip()
        if b1l and b1u: btns.append({"label": b1l, "url": b1u})
        
        b2l, b2u = self.btn2_label.get().strip(), self.btn2_url.get().strip()
        if b2l and b2u: btns.append({"label": b2l, "url": b2u})

        data = {
            "client_id": self.client_id_entry.get().strip(),
            "details": self.details_entry.get(),
            "state": self.state_entry.get(),
            "large_image": self.large_image_key.get().strip(),
            "large_text": self.large_image_text.get().strip(),
            "small_image": self.small_image_key.get().strip(),
            "small_text": self.small_image_text.get().strip(),
            "buttons": btns
        }
        self.presets_mgr.update_active_preset(data)

    # --- RPC Logic ---

    def connect_rpc(self):
        if self.is_connected:
            self.disconnect_rpc()
            return
            
        client_id = self.client_id_entry.get().strip()
        if not client_id:
            print("No Client ID")
            return

        try:
            self.rpc = Presence(client_id)
            self.rpc.connect()
            self.is_connected = True
            
            self.status_dot.configure(text_color="#22c55e")
            self.connect_btn.configure(text="Disconnect", fg_color=COLOR_ACCENT, text_color="white")
            self.client_id_entry.configure(state="disabled")
            print("Connected")
        except Exception as e:
            print(f"Connection Failed: {e}")
            self.status_dot.configure(text_color="#ef4444")

    def disconnect_rpc(self):
        if self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except: pass
        self.rpc = None
        self.is_connected = False
        self.status_dot.configure(text_color="#ef4444")
        self.connect_btn.configure(text="Connect", fg_color=COLOR_HOVER)
        self.client_id_entry.configure(state="normal")
        print("Disconnected")

    def update_presence(self):
        self.save_current_ui_to_preset() # Auto-save on update
        
        if not self.is_connected or not self.rpc:
            print("Not Connected")
            return

        data = self.presets_mgr.get_active_preset()
        
        # Timer logic removed as requested
        start = None

        try:
            # Validate Buttons
            valid_btns = []
            for btn in data.get("buttons", []):
                if btn['url'].startswith("http"):
                    valid_btns.append(btn)
                else:
                    print(f"Skipping Invalid URL: {btn['url']}")
            
            if not valid_btns: valid_btns = None

            self.rpc.update(
                state=data.get("state") or None,
                details=data.get("details") or None,
                large_image=data.get("large_image") or None,
                large_text=data.get("large_text") or None,
                small_image=data.get("small_image") or None,
                small_text=data.get("small_text") or None,
                buttons=valid_btns,
                start=start
            )
            print("Presence Updated")
        except Exception as e:
            print(f"Update Failed: {e}")

    def on_close(self):
        self.save_current_ui_to_preset()
        if self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except: pass
        self.destroy()

if __name__ == "__main__":
    app = RPCApp()
    app.mainloop()
