


import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re
import json
import ctypes

# Fix DPI scaling for high-resolution displays
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

class CANFilterTool:
    def __init__(self, root):
        self.root = root
        self.root.title("CAN ID Filter Tool - Enhanced")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.minsize(1200, 1050)  # Minimum size to prevent it from being too small
        
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.case_sensitive_var = tk.BooleanVar(value=False)
        self.exclude_mode_var = tk.BooleanVar(value=False)
        self.exact_match_var = tk.BooleanVar(value=False)
        
        self.presets_file = "can_id_presets.json"
        
        self.create_widgets()
        self.load_preset_list()
    
    def create_widgets(self):
        # Configure style for larger checkboxes
        style = ttk.Style()
        style.configure('Large.TCheckbutton', font=('Arial', 11))
        
        # Input/Output Frame
        io_frame = tk.LabelFrame(self.root, text="Input/Output Files", padx=10, pady=10)
        io_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        tk.Label(io_frame, text="Input File:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(io_frame, textvariable=self.input_file_var, width=60).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(io_frame, text="Browse", command=self.select_input_file, width=10).grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(io_frame, text="Output File:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(io_frame, textvariable=self.output_file_var, width=60).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(io_frame, text="Save As", command=self.select_output_file, width=10).grid(row=1, column=2, padx=5, pady=5)
        
        # Filter Options Frame
        filter_frame = tk.LabelFrame(self.root, text="Filter Options", padx=10, pady=10)
        filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        tk.Label(filter_frame, text="CAN IDs (comma-separated):").grid(row=0, column=0, sticky="w", pady=5)
        self.can_ids_entry = tk.Entry(filter_frame, width=60)
        self.can_ids_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        # Checkboxes with larger font and bigger checkbox squares
        checkbox_font = ("Arial", 11)
        ttk.Checkbutton(filter_frame, text="Case Sensitive", variable=self.case_sensitive_var, style='Large.TCheckbutton').grid(row=1, column=0, sticky="w", pady=8, padx=5)
        ttk.Checkbutton(filter_frame, text="Exclude Mode (inverse)", variable=self.exclude_mode_var, style='Large.TCheckbutton').grid(row=1, column=1, sticky="w", pady=8, padx=5)
        ttk.Checkbutton(filter_frame, text="Exact Match", variable=self.exact_match_var, style='Large.TCheckbutton').grid(row=1, column=2, sticky="w", pady=8, padx=5)
        
        # Presets Frame
        preset_frame = tk.LabelFrame(self.root, text="CAN ID Presets", padx=10, pady=10)
        preset_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        tk.Label(preset_frame, text="Preset Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.preset_name_entry = tk.Entry(preset_frame, width=30)
        self.preset_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(preset_frame, text="Save Preset", command=self.save_preset, width=12).grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(preset_frame, text="Load Preset:").grid(row=1, column=0, sticky="w", pady=5)
        self.preset_combo = ttk.Combobox(preset_frame, width=28, state="readonly")
        self.preset_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(preset_frame, text="Load", command=self.load_preset, width=12).grid(row=1, column=2, padx=5, pady=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=730, mode='determinate')
        self.progress.grid(row=3, column=0, padx=10, pady=10)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        
        # Action Buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=5, column=0, pady=10)
        
        tk.Button(button_frame, text="Filter", command=self.filter_can_ids, width=15, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Preview (250 lines)", command=self.preview_results, width=18).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_fields, width=15).pack(side=tk.LEFT, padx=5)
    
    def select_input_file(self):
        filename = filedialog.askopenfilename(filetypes=[("ASC files", "*.asc"), ("All files", "*.*")])
        if filename:
            self.input_file_var.set(filename)
    
    def select_output_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".asc",
                                                filetypes=[("ASC files", "*.asc"), ("All files", "*.*")])
        if filename:
            self.output_file_var.set(filename)
    
    def validate_can_ids(self, can_ids_str):
        """Validate and clean CAN IDs"""
        can_ids = [id.strip() for id in can_ids_str.split(',') if id.strip()]
        
        if not can_ids:
            messagebox.showerror("Error", "Please provide at least one CAN ID.")
            return None
        
        validated = []
        for can_id in can_ids:
            # Accept hex (0x123, 0X123) or decimal numbers
            if can_id.lower().startswith('0x'):
                try:
                    int(can_id, 16)
                    validated.append(can_id)
                except ValueError:
                    messagebox.showwarning("Warning", f"Invalid hex CAN ID: {can_id}")
            else:
                try:
                    int(can_id)
                    validated.append(can_id)
                except ValueError:
                    # If not a number, still accept it (might be alphanumeric ID)
                    validated.append(can_id)
        
        return validated
    
    def match_line(self, line, can_ids):
        """Check if line matches any CAN ID based on settings"""
        line_to_check = line if self.case_sensitive_var.get() else line.lower()
        
        for can_id in can_ids:
            id_to_check = can_id if self.case_sensitive_var.get() else can_id.lower()
            
            if self.exact_match_var.get():
                # Use word boundary matching for exact match
                pattern = r'\b' + re.escape(id_to_check) + r'\b'
                if re.search(pattern, line_to_check):
                    return True
            else:
                # Simple substring matching
                if id_to_check in line_to_check:
                    return True
        
        return False
    
    def filter_can_ids(self):
        input_file = self.input_file_var.get()
        output_file = self.output_file_var.get()
        can_ids_str = self.can_ids_entry.get()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please provide both input and output files.")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        can_ids = self.validate_can_ids(can_ids_str)
        if not can_ids:
            return
        
        # Check output directory is writable
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.access(output_dir, os.W_OK):
            messagebox.showerror("Error", "Cannot write to output directory!")
            return
        
        try:
            self.status_label.config(text="Filtering in progress...")
            self.progress['value'] = 0
            self.root.update_idletasks()
            
            file_size = os.path.getsize(input_file)
            bytes_read = 0
            total_lines = 0
            matched_lines = 0
            
            with open(input_file, "r", encoding='utf-8', errors='ignore') as log:
                with open(output_file, "w", encoding='utf-8') as output:
                    for line in log:
                        total_lines += 1
                        bytes_read += len(line.encode('utf-8'))
                        
                        # Update progress every 100 lines
                        if total_lines % 100 == 0:
                            self.progress['value'] = (bytes_read / file_size) * 100
                            self.root.update_idletasks()
                        
                        match_found = self.match_line(line, can_ids)
                        
                        # Apply exclude mode logic
                        if (match_found and not self.exclude_mode_var.get()) or \
                           (not match_found and self.exclude_mode_var.get()):
                            matched_lines += 1
                            output.write(line)
            
            self.progress['value'] = 100
            self.status_label.config(text="Filtering complete!")
            
            percentage = (matched_lines / total_lines * 100) if total_lines > 0 else 0
            
            messagebox.showinfo("Success", 
                f"Filtering complete!\n\n"
                f"Total lines: {total_lines:,}\n"
                f"Matched lines: {matched_lines:,}\n"
                f"Percentage: {percentage:.2f}%\n\n"
                f"Output saved to:\n{output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status_label.config(text="Error occurred!")
        finally:
            self.progress['value'] = 0
    
    def preview_results(self):
        """Show first 250 matching lines"""
        input_file = self.input_file_var.get()
        can_ids_str = self.can_ids_entry.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        can_ids = self.validate_can_ids(can_ids_str)
        if not can_ids:
            return
        
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview - First 250 Matches")
        preview_window.geometry("1000x600")
        
        # Create frame for text widget and scrollbars
        text_frame = tk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create text widget
        text_widget = tk.Text(text_frame, wrap=tk.NONE, font=("Courier", 9))
        text_widget.grid(row=0, column=0, sticky="nsew")
        
        # Vertical scrollbar
        scrollbar_y = tk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        text_widget.config(yscrollcommand=scrollbar_y.set)
        
        # Horizontal scrollbar
        scrollbar_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        text_widget.config(xscrollcommand=scrollbar_x.set)
        
        # Configure grid weights
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Status label
        status_label = tk.Label(preview_window, text="Loading...", relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        try:
            count = 0
            with open(input_file, "r", encoding='utf-8', errors='ignore') as log:
                for line in log:
                    match_found = self.match_line(line, can_ids)
                    
                    if (match_found and not self.exclude_mode_var.get()) or \
                       (not match_found and self.exclude_mode_var.get()):
                        text_widget.insert(tk.END, line)
                        count += 1
                        if count >= 250:
                            break
            
            if count == 0:
                text_widget.insert(tk.END, "No matches found in the file.")
                status_label.config(text="No matches found")
            else:
                status_label.config(text=f"Showing {count} matching lines")
            
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
    def save_preset(self):
        """Save current CAN IDs as a preset"""
        preset_name = self.preset_name_entry.get().strip()
        can_ids = self.can_ids_entry.get().strip()
        
        if not preset_name:
            messagebox.showwarning("Warning", "Please enter a preset name.")
            return
        
        if not can_ids:
            messagebox.showwarning("Warning", "Please enter CAN IDs to save.")
            return
        
        presets = self.load_presets_from_file()
        presets[preset_name] = can_ids
        
        try:
            with open(self.presets_file, "w") as f:
                json.dump(presets, f, indent=2)
            
            messagebox.showinfo("Success", f"Preset '{preset_name}' saved successfully!")
            self.load_preset_list()
            self.preset_name_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preset:\n{str(e)}")
    
    def load_preset(self):
        """Load selected preset"""
        preset_name = self.preset_combo.get()
        
        if not preset_name:
            messagebox.showwarning("Warning", "Please select a preset to load.")
            return
        
        presets = self.load_presets_from_file()
        
        if preset_name in presets:
            self.can_ids_entry.delete(0, tk.END)
            self.can_ids_entry.insert(0, presets[preset_name])
            self.status_label.config(text=f"Loaded preset: {preset_name}")
        else:
            messagebox.showerror("Error", "Preset not found!")
    
    def load_presets_from_file(self):
        """Load presets from JSON file"""
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def load_preset_list(self):
        """Update preset dropdown with saved presets"""
        presets = self.load_presets_from_file()
        self.preset_combo['values'] = list(presets.keys())
    
    def clear_fields(self):
        """Clear all input fields"""
        self.input_file_var.set("")
        self.output_file_var.set("")
        self.can_ids_entry.delete(0, tk.END)
        self.preset_name_entry.delete(0, tk.END)
        self.progress['value'] = 0
        self.status_label.config(text="Ready")

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CANFilterTool(root)
    root.mainloop()




















# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# import os
# import re
# import json
# import ctypes

# # Fix DPI scaling for high-resolution displays
# try:
#     ctypes.windll.shcore.SetProcessDpiAwareness(1)
# except:
#     pass

# class CANFilterTool:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("CAN ID Filter Tool - Enhanced")
#         self.root.geometry("1250x1050")
#         self.root.resizable(True, True)
        
#         self.input_file_var = tk.StringVar()
#         self.output_file_var = tk.StringVar()
#         self.case_sensitive_var = tk.BooleanVar(value=False)
#         self.exclude_mode_var = tk.BooleanVar(value=False)
#         self.exact_match_var = tk.BooleanVar(value=False)
        
#         self.presets_file = "can_id_presets.json"
        
#         self.create_widgets()
#         self.load_preset_list()
    
#     def create_widgets(self):
#         # Input/Output Frame
#         io_frame = tk.LabelFrame(self.root, text="Input/Output Files", padx=10, pady=10)
#         io_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
#         tk.Label(io_frame, text="Input File:").grid(row=0, column=0, sticky="w", pady=5)
#         tk.Entry(io_frame, textvariable=self.input_file_var, width=60).grid(row=0, column=1, padx=5, pady=5)
#         tk.Button(io_frame, text="Browse", command=self.select_input_file, width=10).grid(row=0, column=2, padx=5, pady=5)
        
#         tk.Label(io_frame, text="Output File:").grid(row=1, column=0, sticky="w", pady=5)
#         tk.Entry(io_frame, textvariable=self.output_file_var, width=60).grid(row=1, column=1, padx=5, pady=5)
#         tk.Button(io_frame, text="Save As", command=self.select_output_file, width=10).grid(row=1, column=2, padx=5, pady=5)
        
#         # Filter Options Frame
#         filter_frame = tk.LabelFrame(self.root, text="Filter Options", padx=10, pady=10)
#         filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
#         tk.Label(filter_frame, text="CAN IDs (comma-separated):").grid(row=0, column=0, sticky="w", pady=5)
#         self.can_ids_entry = tk.Entry(filter_frame, width=60)
#         self.can_ids_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
#         # Checkboxes with larger font
#         # Checkboxes with larger font and bigger checkbox squares
#         checkbox_font = ("Arial", 11)
#         ttk.Checkbutton(filter_frame, text="Case Sensitive", variable=self.case_sensitive_var, style='Large.TCheckbutton').grid(row=1, column=0, sticky="w", pady=8, padx=5)
#         ttk.Checkbutton(filter_frame, text="Exclude Mode (inverse)", variable=self.exclude_mode_var, style='Large.TCheckbutton').grid(row=1, column=1, sticky="w", pady=8, padx=5)
#         ttk.Checkbutton(filter_frame, text="Exact Match", variable=self.exact_match_var, style='Large.TCheckbutton').grid(row=1, column=2, sticky="w", pady=8, padx=5)
        
#         # Presets Frame
#         preset_frame = tk.LabelFrame(self.root, text="CAN ID Presets", padx=10, pady=10)
#         preset_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
#         tk.Label(preset_frame, text="Preset Name:").grid(row=0, column=0, sticky="w", pady=5)
#         self.preset_name_entry = tk.Entry(preset_frame, width=30)
#         self.preset_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
#         tk.Button(preset_frame, text="Save Preset", command=self.save_preset, width=12).grid(row=0, column=2, padx=5, pady=5)
        
#         tk.Label(preset_frame, text="Load Preset:").grid(row=1, column=0, sticky="w", pady=5)
#         self.preset_combo = ttk.Combobox(preset_frame, width=28, state="readonly")
#         self.preset_combo.grid(row=1, column=1, padx=5, pady=5)
        
#         tk.Button(preset_frame, text="Load", command=self.load_preset, width=12).grid(row=1, column=2, padx=5, pady=5)
        
#         # Progress Bar
#         self.progress = ttk.Progressbar(self.root, length=730, mode='determinate')
#         self.progress.grid(row=3, column=0, padx=10, pady=10)
        
#         # Status Label
#         self.status_label = tk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
#         self.status_label.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        
#         # Action Buttons
#         button_frame = tk.Frame(self.root)
#         button_frame.grid(row=5, column=0, pady=10)
        
#         tk.Button(button_frame, text="Filter", command=self.filter_can_ids, width=15, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
#         tk.Button(button_frame, text="Preview (10 lines)", command=self.preview_results, width=15).pack(side=tk.LEFT, padx=5)
#         tk.Button(button_frame, text="Clear", command=self.clear_fields, width=15).pack(side=tk.LEFT, padx=5)
    
#     def select_input_file(self):
#         filename = filedialog.askopenfilename(filetypes=[("ASC files", "*.asc"), ("All files", "*.*")])
#         if filename:
#             self.input_file_var.set(filename)
    
#     def select_output_file(self):
#         filename = filedialog.asksaveasfilename(defaultextension=".asc",
#                                                 filetypes=[("ASC files", "*.asc"), ("All files", "*.*")])
#         if filename:
#             self.output_file_var.set(filename)
    
#     def validate_can_ids(self, can_ids_str):
#         """Validate and clean CAN IDs"""
#         can_ids = [id.strip() for id in can_ids_str.split(',') if id.strip()]
        
#         if not can_ids:
#             messagebox.showerror("Error", "Please provide at least one CAN ID.")
#             return None
        
#         validated = []
#         for can_id in can_ids:
#             # Accept hex (0x123, 0X123) or decimal numbers
#             if can_id.lower().startswith('0x'):
#                 try:
#                     int(can_id, 16)
#                     validated.append(can_id)
#                 except ValueError:
#                     messagebox.showwarning("Warning", f"Invalid hex CAN ID: {can_id}")
#             else:
#                 try:
#                     int(can_id)
#                     validated.append(can_id)
#                 except ValueError:
#                     # If not a number, still accept it (might be alphanumeric ID)
#                     validated.append(can_id)
        
#         return validated
    
#     def match_line(self, line, can_ids):
#         """Check if line matches any CAN ID based on settings"""
#         line_to_check = line if self.case_sensitive_var.get() else line.lower()
        
#         for can_id in can_ids:
#             id_to_check = can_id if self.case_sensitive_var.get() else can_id.lower()
            
#             if self.exact_match_var.get():
#                 # Use word boundary matching for exact match
#                 pattern = r'\b' + re.escape(id_to_check) + r'\b'
#                 if re.search(pattern, line_to_check):
#                     return True
#             else:
#                 # Simple substring matching
#                 if id_to_check in line_to_check:
#                     return True
        
#         return False
    
#     def filter_can_ids(self):
#         input_file = self.input_file_var.get()
#         output_file = self.output_file_var.get()
#         can_ids_str = self.can_ids_entry.get()
        
#         if not input_file or not output_file:
#             messagebox.showerror("Error", "Please provide both input and output files.")
#             return
        
#         if not os.path.exists(input_file):
#             messagebox.showerror("Error", "Input file does not exist!")
#             return
        
#         can_ids = self.validate_can_ids(can_ids_str)
#         if not can_ids:
#             return
        
#         # Check output directory is writable
#         output_dir = os.path.dirname(output_file)
#         if output_dir and not os.access(output_dir, os.W_OK):
#             messagebox.showerror("Error", "Cannot write to output directory!")
#             return
        
#         try:
#             self.status_label.config(text="Filtering in progress...")
#             self.progress['value'] = 0
#             self.root.update_idletasks()
            
#             file_size = os.path.getsize(input_file)
#             bytes_read = 0
#             total_lines = 0
#             matched_lines = 0
            
#             with open(input_file, "r", encoding='utf-8', errors='ignore') as log:
#                 with open(output_file, "w", encoding='utf-8') as output:
#                     for line in log:
#                         total_lines += 1
#                         bytes_read += len(line.encode('utf-8'))
                        
#                         # Update progress every 100 lines
#                         if total_lines % 100 == 0:
#                             self.progress['value'] = (bytes_read / file_size) * 100
#                             self.root.update_idletasks()
                        
#                         match_found = self.match_line(line, can_ids)
                        
#                         # Apply exclude mode logic
#                         if (match_found and not self.exclude_mode_var.get()) or \
#                            (not match_found and self.exclude_mode_var.get()):
#                             matched_lines += 1
#                             output.write(line)
            
#             self.progress['value'] = 100
#             self.status_label.config(text="Filtering complete!")
            
#             percentage = (matched_lines / total_lines * 100) if total_lines > 0 else 0
            
#             messagebox.showinfo("Success", 
#                 f"Filtering complete!\n\n"
#                 f"Total lines: {total_lines:,}\n"
#                 f"Matched lines: {matched_lines:,}\n"
#                 f"Percentage: {percentage:.2f}%\n\n"
#                 f"Output saved to:\n{output_file}")
            
#         except Exception as e:
#             messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
#             self.status_label.config(text="Error occurred!")
#         finally:
#             self.progress['value'] = 0
    
#     def preview_results(self):
#         """Show first 10 matching lines"""
#         input_file = self.input_file_var.get()
#         can_ids_str = self.can_ids_entry.get()
        
#         if not input_file:
#             messagebox.showerror("Error", "Please select an input file.")
#             return
        
#         if not os.path.exists(input_file):
#             messagebox.showerror("Error", "Input file does not exist!")
#             return
        
#         can_ids = self.validate_can_ids(can_ids_str)
#         if not can_ids:
#             return
        
#         preview_window = tk.Toplevel(self.root)
#         preview_window.title("Preview - First 10 Matches")
#         preview_window.geometry("800x400")
        
#         text_widget = tk.Text(preview_window, wrap=tk.NONE, width=100, height=20)
#         text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
#         scrollbar_y = tk.Scrollbar(preview_window, command=text_widget.yview)
#         scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
#         text_widget.config(yscrollcommand=scrollbar_y.set)
        
#         scrollbar_x = tk.Scrollbar(preview_window, orient=tk.HORIZONTAL, command=text_widget.xview)
#         scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
#         text_widget.config(xscrollcommand=scrollbar_x.set)
        
#         try:
#             count = 0
#             with open(input_file, "r", encoding='utf-8', errors='ignore') as log:
#                 for line in log:
#                     match_found = self.match_line(line, can_ids)
                    
#                     if (match_found and not self.exclude_mode_var.get()) or \
#                        (not match_found and self.exclude_mode_var.get()):
#                         text_widget.insert(tk.END, line)
#                         count += 1
#                         if count >= 10:
#                             break
            
#             if count == 0:
#                 text_widget.insert(tk.END, "No matches found in the file.")
            
#             text_widget.config(state=tk.DISABLED)
            
#         except Exception as e:
#             messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
#     def save_preset(self):
#         """Save current CAN IDs as a preset"""
#         preset_name = self.preset_name_entry.get().strip()
#         can_ids = self.can_ids_entry.get().strip()
        
#         if not preset_name:
#             messagebox.showwarning("Warning", "Please enter a preset name.")
#             return
        
#         if not can_ids:
#             messagebox.showwarning("Warning", "Please enter CAN IDs to save.")
#             return
        
#         presets = self.load_presets_from_file()
#         presets[preset_name] = can_ids
        
#         try:
#             with open(self.presets_file, "w") as f:
#                 json.dump(presets, f, indent=2)
            
#             messagebox.showinfo("Success", f"Preset '{preset_name}' saved successfully!")
#             self.load_preset_list()
#             self.preset_name_entry.delete(0, tk.END)
            
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to save preset:\n{str(e)}")
    
#     def load_preset(self):
#         """Load selected preset"""
#         preset_name = self.preset_combo.get()
        
#         if not preset_name:
#             messagebox.showwarning("Warning", "Please select a preset to load.")
#             return
        
#         presets = self.load_presets_from_file()
        
#         if preset_name in presets:
#             self.can_ids_entry.delete(0, tk.END)
#             self.can_ids_entry.insert(0, presets[preset_name])
#             self.status_label.config(text=f"Loaded preset: {preset_name}")
#         else:
#             messagebox.showerror("Error", "Preset not found!")
    
#     def load_presets_from_file(self):
#         """Load presets from JSON file"""
#         if os.path.exists(self.presets_file):
#             try:
#                 with open(self.presets_file, "r") as f:
#                     return json.load(f)
#             except:
#                 return {}
#         return {}
    
#     def load_preset_list(self):
#         """Update preset dropdown with saved presets"""
#         presets = self.load_presets_from_file()
#         self.preset_combo['values'] = list(presets.keys())
    
#     def clear_fields(self):
#         """Clear all input fields"""
#         self.input_file_var.set("")
#         self.output_file_var.set("")
#         self.can_ids_entry.delete(0, tk.END)
#         self.preset_name_entry.delete(0, tk.END)
#         self.progress['value'] = 0
#         self.status_label.config(text="Ready")

# # Create and run the application
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = CANFilterTool(root)
#     root.mainloop()

