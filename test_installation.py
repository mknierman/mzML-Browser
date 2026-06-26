#!/usr/bin/env python3
"""
Test script to verify that all required dependencies are properly installed
"""

def test_imports():
    """Test that all required packages can be imported"""
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import tkinter: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✓ matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import matplotlib: {e}")
        return False
    
    try:
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        print("✓ matplotlib backend imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import matplotlib backend: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        return False
    
    try:
        import pymzml
        print("✓ pymzml imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pymzml: {e}")
        return False
    
    return True

def test_gui_creation():
    """Test that basic GUI elements can be created"""
    try:
        import tkinter as tk
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        # Create a simple test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create a test figure
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 4, 2])
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, root)
        
        print("✓ GUI elements created successfully")
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Failed to create GUI elements: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing mzML Browser Installation...")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    print()
    
    # Test GUI creation
    gui_ok = test_gui_creation()
    print()
    
    if imports_ok and gui_ok:
        print("✓ All tests passed! The mzML Browser should work correctly.")
        print("\nTo run the application:")
        print("python mzml_browser.py")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
        print("\nTo install missing dependencies:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()

