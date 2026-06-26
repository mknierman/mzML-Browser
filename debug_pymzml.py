#!/usr/bin/env python3
"""
Debug script to check pymzml version and available methods
"""

import pymzml
import sys

def check_pymzml_version():
    """Check pymzml version and available methods"""
    print(f"pymzml version: {pymzml.__version__}")
    print(f"Python version: {sys.version}")
    print()

def test_spectrum_methods():
    """Test available methods on a spectrum object"""
    print("Testing spectrum object methods...")
    
    # Create a simple test mzML file or use a sample
    try:
        # Try to create a minimal spectrum object to test methods
        from pymzml.spec import Spectrum
        
        # Create a dummy spectrum for testing
        spectrum = Spectrum()
        
        print("Available methods on spectrum object:")
        methods = [method for method in dir(spectrum) if not method.startswith('_')]
        for method in sorted(methods):
            print(f"  - {method}")
        
        print("\nTesting specific methods:")
        
        # Test get_peaks
        try:
            peaks = spectrum.get_peaks()
            print("✓ get_peaks() method exists")
        except AttributeError:
            print("✗ get_peaks() method not found")
        
        # Test peaks
        try:
            peaks = spectrum.peaks()
            print("✓ peaks() method exists")
        except AttributeError:
            print("✗ peaks() method not found")
        
        # Test mz and i attributes
        try:
            mz = spectrum.mz
            print("✓ spectrum.mz attribute exists")
        except AttributeError:
            print("✗ spectrum.mz attribute not found")
        
        try:
            i = spectrum.i
            print("✓ spectrum.i attribute exists")
        except AttributeError:
            print("✗ spectrum.i attribute not found")
        
        # Test scan_time_in_minutes
        try:
            rt = spectrum.scan_time_in_minutes()
            print("✓ scan_time_in_minutes() method exists")
        except AttributeError:
            print("✗ scan_time_in_minutes() method not found")
        
        # Test TIC
        try:
            tic = spectrum.TIC
            print("✓ TIC attribute exists")
        except AttributeError:
            print("✗ TIC attribute not found")
        
        # Test ms_level
        try:
            level = spectrum.ms_level
            print("✓ ms_level attribute exists")
        except AttributeError:
            print("✗ ms_level attribute not found")
            
    except Exception as e:
        print(f"Error testing spectrum methods: {e}")

def main():
    """Main function"""
    print("pymzml Debug Information")
    print("=" * 40)
    
    check_pymzml_version()
    test_spectrum_methods()
    
    print("\n" + "=" * 40)
    print("If you're having issues, try:")
    print("1. Update pymzml: pip install --upgrade pymzml")
    print("2. Check if your mzML file is properly formatted")
    print("3. Ensure the file contains MS1 spectra")

if __name__ == "__main__":
    main()

