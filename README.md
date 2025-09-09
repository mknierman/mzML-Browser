# mzML Interactive Browser

An interactive Python application for visualizing mzML (mass spectrometry data) files with real-time exploration capabilities.

## Features

- **Total Ion Chromatogram (TIC)**: Upper plot showing the total ion count over time
- **Mass Spectra**: Lower plot displaying the mass spectrum at selected time points
- **Interactive Navigation**: Click on the TIC plot to view mass spectra at specific retention times
- **Zoom and Pan**: Full matplotlib navigation toolbar for zooming and panning in both plots
- **Peak Annotations**: Automatic labeling of top 10 peaks in mass spectra
- **Real-time Updates**: Instant spectrum switching with visual feedback

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Required Packages**:
   - `pymzml`: For parsing mzML files
   - `matplotlib`: For plotting and interactive visualization
   - `numpy`: For numerical operations
   - `tkinter`: For the GUI (usually comes with Python)

## Usage

1. **Run the Application**:
   ```bash
   python mzml_browser.py
   ```

2. **Open an mzML File**:
   - Use the "File" → "Open mzML file" menu option
   - Or use the file dialog that appears when you start the application

3. **Navigate the Data**:
   - **TIC Plot (Upper)**: Shows the total ion chromatogram over time
   - **Mass Spectrum Plot (Lower)**: Shows the mass spectrum at the selected time point
   - **Click on TIC**: Click anywhere on the TIC plot to view the mass spectrum at that retention time
   - **Zoom**: Use the matplotlib toolbar to zoom in/out of either plot
   - **Pan**: Use the pan tool to navigate around zoomed areas

4. **Features**:
   - Red dot on TIC plot indicates the currently selected spectrum
   - Top 10 peaks in mass spectra are automatically labeled with m/z values
   - Status bar shows current retention time and file information
   - Both plots support independent zooming and navigation

## File Format Support

This application supports standard mzML files containing:
- MS1 spectra (full scan mass spectra)
- Retention time information
- m/z and intensity data

## Troubleshooting

- **Large Files**: Very large mzML files may take some time to load. The application will show a loading message.
- **Memory Usage**: The application loads all spectrum data into memory for fast access. Very large files may require significant RAM.
- **File Format**: Ensure your mzML file is properly formatted and contains MS1 spectra.

## Technical Details

- **Data Processing**: Only MS1 spectra are processed and displayed
- **Performance**: Optimized for interactive use with pre-loaded spectrum data
- **Visualization**: Uses matplotlib for high-quality, interactive plots
- **GUI**: Built with tkinter for cross-platform compatibility

## Example Workflow

1. Start the application
2. Open your mzML file
3. Examine the TIC plot to identify regions of interest
4. Click on peaks or regions in the TIC to view corresponding mass spectra
5. Use zoom tools to examine specific m/z ranges or time regions
6. Navigate between different time points to compare spectra

## License

This project is open source and available under the MIT License.

## Notes
Written with the help of cursor.ai
