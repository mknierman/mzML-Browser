#!/usr/bin/env python3
"""
Interactive mzML Browser

This application provides an interactive visualization of mzML files with:
- TIC (Total Ion Chromatogram) in the upper plot
- Mass spectra at selected time points in the lower plot
- Interactive zooming and navigation capabilities
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import pymzml
import os
from typing import Dict, List, Tuple, Optional


class MzMLBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("mzML Interactive Browser")
        self.root.geometry("1200x800")
        
        # Data storage
        self.mzml_file = None
        self.tic_data = None
        self.spectra_data = {}
        self.current_spectrum_index = 0
        
        # Loading indicator
        self.loading_window = None
        self.loading_label = None
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open mzML file", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create matplotlib figure with two subplots
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.ax1 = self.fig.add_subplot(211)  # TIC plot
        self.ax2 = self.fig.add_subplot(212)  # Mass spectra plot
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add matplotlib toolbar
        toolbar_frame = tk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        
        # Add custom buttons in a separate frame below the toolbar
        button_frame = tk.Frame(main_frame, bg='lightgray', relief=tk.RAISED, bd=2)
        button_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Add label for the button section
        button_label = tk.Label(button_frame, text="Navigation Controls:", 
                               font=('Arial', 11, 'bold'), bg='lightgray')
        button_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Add home button to reset both plots
        home_button = tk.Button(button_frame, text="🏠 HOME", 
                               command=self.reset_all_plots, 
                               bg='lightblue', relief=tk.RAISED, 
                               font=('Arial', 11, 'bold'),
                               width=10, height=2)
        home_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Add reset zoom button for mass spectrum
        reset_button = tk.Button(button_frame, text="🔍 RESET MS ZOOM", 
                                command=self.reset_mass_spectrum_zoom,
                                bg='lightgreen', relief=tk.RAISED,
                                font=('Arial', 11, 'bold'),
                                width=15, height=2)
        reset_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Initialize plots with empty data to make toolbar visible
        self.initialize_empty_plots()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Please open an mzML file")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind mouse events
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        
        # Bind keyboard events
        self.root.bind('<Left>', self.on_left_arrow)
        self.root.bind('<Right>', self.on_right_arrow)
        
        # Zoom state variables
        self.zoom_active = False
        self.zoom_start = None
        self.zoom_end = None
        
    def initialize_empty_plots(self):
        """Initialize plots with empty data to make toolbar visible"""
        # Create empty plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Set up TIC plot
        self.ax1.set_xlabel('Retention Time (min)')
        self.ax1.set_ylabel('Total Ion Count')
        self.ax1.set_title('Total Ion Chromatogram (TIC)')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_xlim(0, 10)
        self.ax1.set_ylim(0, 1000)
        
        # Set up mass spectrum plot
        self.ax2.set_xlabel('m/z')
        self.ax2.set_ylabel('Intensity')
        self.ax2.set_title('Mass Spectrum')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_xlim(0, 1000)
        self.ax2.set_ylim(0, 1000)
        
        # Add placeholder text
        self.ax1.text(5, 500, 'Please load an mzML file to view data', 
                     ha='center', va='center', fontsize=12, alpha=0.5)
        self.ax2.text(500, 500, 'Mass spectrum will appear here', 
                     ha='center', va='center', fontsize=12, alpha=0.5)
        
        # Adjust layout and draw
        self.fig.tight_layout()
        self.canvas.draw()
        
    def show_loading_indicator(self, filename):
        """Show loading indicator window"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Loading...")
        self.loading_window.geometry("300x150")
        self.loading_window.resizable(False, False)
        
        # Center the loading window
        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        
        # Loading content
        loading_frame = tk.Frame(self.loading_window)
        loading_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Loading text
        self.loading_label = tk.Label(loading_frame, text=f"Loading {filename}...", 
                                     font=("Arial", 12))
        self.loading_label.pack(pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(loading_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=10)
        self.progress_bar.start()
        
        # Cancel button
        cancel_button = tk.Button(loading_frame, text="Cancel", 
                                 command=self.cancel_loading)
        cancel_button.pack(pady=10)
        
        # Center the window
        self.loading_window.update_idletasks()
        x = (self.loading_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.loading_window.winfo_screenheight() // 2) - (150 // 2)
        self.loading_window.geometry(f'300x150+{x}+{y}')
        
        self.loading_window.update()
    
    def hide_loading_indicator(self):
        """Hide loading indicator window"""
        if self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None
            self.loading_label = None
    
    def cancel_loading(self):
        """Cancel the loading process"""
        self.hide_loading_indicator()
        self.status_var.set("Loading cancelled")
    
    def open_file(self):
        """Open and parse mzML file"""
        file_path = filedialog.askopenfilename(
            title="Select mzML file",
            filetypes=[("mzML files", "*.mzML"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.show_loading_indicator(os.path.basename(file_path))
                self.load_mzml_file(file_path)
            except Exception as e:
                self.hide_loading_indicator()
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def load_mzml_file(self, file_path: str):
        """Load and parse mzML file"""
        self.status_var.set(f"Loading {os.path.basename(file_path)}...")
        self.root.update()
        
        # Parse mzML file
        msrun = pymzml.run.Reader(file_path)
        
        # Extract TIC data
        tic_times = []
        tic_intensities = []
        spectrum_indices = []
        
        total_spectra = 0
        for spectrum in msrun:
            total_spectra += 1
        
        # Reset the reader to start from beginning
        msrun = pymzml.run.Reader(file_path)
        
        for i, spectrum in enumerate(msrun):
            try:
                # Update loading progress every 100 spectra
                if i % 100 == 0 and self.loading_label:
                    progress = (i / total_spectra) * 100
                    self.loading_label.config(text=f"Loading {os.path.basename(file_path)}... {progress:.1f}%")
                    self.loading_window.update()
                
                if spectrum.ms_level == 1:  # MS1 spectra only
                    # Get retention time
                    rt = spectrum.scan_time_in_minutes()
                    tic_times.append(rt)
                    tic_intensities.append(spectrum.TIC)
                    spectrum_indices.append(i)
                
                # Store spectrum data for later use
                # Use the mz and i attributes which are available in pymzml 2.5.11
                mz_values = spectrum.mz
                intensities = spectrum.i
                
                # Ensure we have valid data
                if mz_values is not None and intensities is not None and len(mz_values) > 0:
                    self.spectra_data[i] = {
                        'rt': rt,
                        'mz': mz_values,
                        'intensities': intensities,
                        'index': i
                    }
            except Exception as e:
                print(f"Warning: Error processing spectrum {i}: {e}")
                continue
        
        if not spectrum_indices:
            raise ValueError("No MS1 spectra found in the mzML file")
        
        self.tic_data = {
            'times': np.array(tic_times),
            'intensities': np.array(tic_intensities),
            'indices': spectrum_indices
        }
        
        self.mzml_file = file_path
        self.current_spectrum_index = spectrum_indices[len(spectrum_indices)//2]  # Start with middle spectrum
        
        # Update plots
        self.update_plots()
        self.status_var.set(f"Loaded {os.path.basename(file_path)} - {len(spectrum_indices)} MS1 spectra")
        
        # Hide loading indicator
        self.hide_loading_indicator()
    
    def update_plots(self):
        """Update both TIC and mass spectra plots"""
        if self.tic_data is None:
            return
            
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Plot TIC
        self.ax1.plot(self.tic_data['times'], self.tic_data['intensities'], 'b-', linewidth=1)
        self.ax1.set_xlabel('Retention Time (min)')
        self.ax1.set_ylabel('Total Ion Count')
        self.ax1.set_title('Total Ion Chromatogram (TIC)')
        self.ax1.grid(True, alpha=0.3)
        
        # Highlight current spectrum in TIC with vertical line
        if self.current_spectrum_index in self.spectra_data:
            current_rt = self.spectra_data[self.current_spectrum_index]['rt']
            y_min, y_max = self.ax1.get_ylim()
            self.ax1.axvline(x=current_rt, color='red', linestyle='-', linewidth=2, alpha=0.8)
        
        # Plot mass spectrum
        if self.current_spectrum_index in self.spectra_data:
            spectrum = self.spectra_data[self.current_spectrum_index]
            mz_values = spectrum['mz']
            intensities = spectrum['intensities']
            
            # Filter out zero intensities for cleaner plot
            non_zero_mask = intensities > 0
            mz_filtered = mz_values[non_zero_mask]
            intensities_filtered = intensities[non_zero_mask]
            
            self.ax2.plot(mz_filtered, intensities_filtered, 'k-', linewidth=0.5)
            self.ax2.set_xlabel('m/z')
            self.ax2.set_ylabel('Intensity')
            self.ax2.set_title(f'Mass Spectrum at {spectrum["rt"]:.3f} min')
            self.ax2.grid(True, alpha=0.3)
            
            # Add peak annotations for top peaks
            if len(intensities_filtered) > 0:
                top_peaks_idx = np.argsort(intensities_filtered)[-10:]  # Top 10 peaks
                for idx in top_peaks_idx:
                    mz_val = mz_filtered[idx]
                    intensity_val = intensities_filtered[idx]
                    self.ax2.annotate(f'{mz_val:.2f}', 
                                    xy=(mz_val, intensity_val),
                                    xytext=(5, 5), textcoords='offset points',
                                    fontsize=8, ha='left', va='bottom')
        
        # Adjust layout
        self.fig.tight_layout()
        self.canvas.draw()
    
    def on_click(self, event):
        """Handle mouse clicks on the plots"""
        if event.inaxes == self.ax1 and self.tic_data is not None:
            # TIC plot click - select spectrum
            clicked_time = event.xdata
            if clicked_time is not None:
                closest_idx = np.argmin(np.abs(self.tic_data['times'] - clicked_time))
                self.current_spectrum_index = self.tic_data['indices'][closest_idx]
                self.update_plots()
                
                # Update status
                rt = self.tic_data['times'][closest_idx]
                self.status_var.set(f"Selected spectrum at {rt:.3f} min")
        
        elif event.inaxes == self.ax2:
            # Mass spectrum plot click - start zoom selection
            if event.button == 1:  # Left click
                self.zoom_active = True
                self.zoom_start = (event.xdata, event.ydata)
                self.status_var.set("Click and drag to zoom mass spectrum")
    
    def on_scroll(self, event):
        """Handle mouse scroll events for zooming"""
        if event.inaxes == self.ax2 and self.current_spectrum_index in self.spectra_data:
            # Zoom in/out on mass spectrum plot
            cur_xlim = self.ax2.get_xlim()
            cur_ylim = self.ax2.get_ylim()
            
            xdata = event.xdata
            ydata = event.ydata
            
            if xdata is None or ydata is None:
                return
            
            # Zoom factor
            base_scale = 1.1
            if event.button == 'up':
                scale_factor = 1 / base_scale
            else:
                scale_factor = base_scale
            
            # Calculate new limits
            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
            
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
            
            self.ax2.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
            self.ax2.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
            
            self.canvas.draw()
            self.status_var.set("Zoomed mass spectrum")
    
    def on_mouse_move(self, event):
        """Handle mouse movement for zoom selection"""
        if self.zoom_active and event.inaxes == self.ax2:
            self.zoom_end = (event.xdata, event.ydata)
            # Could add visual feedback here if needed
    
    def on_mouse_release(self, event):
        """Handle mouse release for zoom selection"""
        if self.zoom_active and event.inaxes == self.ax2 and event.button == 1:
            if self.zoom_start and self.zoom_end:
                x1, y1 = self.zoom_start
                x2, y2 = self.zoom_end
                
                if x1 is not None and x2 is not None and y1 is not None and y2 is not None:
                    # Set zoom limits
                    self.ax2.set_xlim(min(x1, x2), max(x1, x2))
                    self.ax2.set_ylim(min(y1, y2), max(y1, y2))
                    self.canvas.draw()
                    self.status_var.set("Zoomed mass spectrum")
            
            self.zoom_active = False
            self.zoom_start = None
            self.zoom_end = None
    
    def reset_mass_spectrum_zoom(self):
        """Reset the mass spectrum plot to show all data"""
        if self.current_spectrum_index in self.spectra_data:
            spectrum = self.spectra_data[self.current_spectrum_index]
            mz_values = spectrum['mz']
            intensities = spectrum['intensities']
            
            # Filter out zero intensities
            non_zero_mask = intensities > 0
            mz_filtered = mz_values[non_zero_mask]
            intensities_filtered = intensities[non_zero_mask]
            
            if len(mz_filtered) > 0:
                # Set limits to show all data with some padding
                mz_range = mz_filtered.max() - mz_filtered.min()
                intensity_range = intensities_filtered.max() - intensities_filtered.min()
                
                self.ax2.set_xlim(mz_filtered.min() - mz_range * 0.05, 
                                 mz_filtered.max() + mz_range * 0.05)
                self.ax2.set_ylim(0, intensities_filtered.max() * 1.1)
                
                self.canvas.draw()
                self.status_var.set("Reset mass spectrum zoom")
    
    def reset_all_plots(self):
        """Reset both TIC and mass spectrum plots to their original view"""
        if self.tic_data is not None:
            # Reset TIC plot to show all data
            tic_times = self.tic_data['times']
            tic_intensities = self.tic_data['intensities']
            
            if len(tic_times) > 0:
                # Set TIC limits to show all data with some padding
                time_range = tic_times.max() - tic_times.min()
                intensity_range = tic_intensities.max() - tic_intensities.min()
                
                self.ax1.set_xlim(tic_times.min() - time_range * 0.02, 
                                 tic_times.max() + time_range * 0.02)
                self.ax1.set_ylim(0, tic_intensities.max() * 1.05)
        
        # Reset mass spectrum plot
        if self.current_spectrum_index in self.spectra_data:
            spectrum = self.spectra_data[self.current_spectrum_index]
            mz_values = spectrum['mz']
            intensities = spectrum['intensities']
            
            # Filter out zero intensities
            non_zero_mask = intensities > 0
            mz_filtered = mz_values[non_zero_mask]
            intensities_filtered = intensities[non_zero_mask]
            
            if len(mz_filtered) > 0:
                # Set limits to show all data with some padding
                mz_range = mz_filtered.max() - mz_filtered.min()
                
                self.ax2.set_xlim(mz_filtered.min() - mz_range * 0.05, 
                                 mz_filtered.max() + mz_range * 0.05)
                self.ax2.set_ylim(0, intensities_filtered.max() * 1.1)
        
        # Redraw the plots
        self.canvas.draw()
        self.status_var.set("Reset all plots to original view")
    
    def on_left_arrow(self, event):
        """Handle left arrow key press - move to previous spectrum"""
        if self.tic_data is not None and len(self.tic_data['indices']) > 1:
            current_idx = self.tic_data['indices'].index(self.current_spectrum_index)
            if current_idx > 0:
                self.current_spectrum_index = self.tic_data['indices'][current_idx - 1]
                self.update_plots()
                
                # Update status
                rt = self.spectra_data[self.current_spectrum_index]['rt']
                self.status_var.set(f"Selected spectrum at {rt:.3f} min (←)")
    
    def on_right_arrow(self, event):
        """Handle right arrow key press - move to next spectrum"""
        if self.tic_data is not None and len(self.tic_data['indices']) > 1:
            current_idx = self.tic_data['indices'].index(self.current_spectrum_index)
            if current_idx < len(self.tic_data['indices']) - 1:
                self.current_spectrum_index = self.tic_data['indices'][current_idx + 1]
                self.update_plots()
                
                # Update status
                rt = self.spectra_data[self.current_spectrum_index]['rt']
                self.status_var.set(f"Selected spectrum at {rt:.3f} min (→)")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = MzMLBrowser(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
