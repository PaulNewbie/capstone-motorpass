#!/usr/bin/env python3
# debug_motorpass_setup.py - Check your MotorPass setup after reorganization

import os
import sys

def check_file_structure():
    """Check if files are in expected locations"""
    print("🔍 MOTORPASS SETUP CHECKER")
    print("=" * 50)
    
    # Find project root
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check for key files
    key_files = [
        "main.py",
        "best.onnx",
        "config.py",
        "etc/services/helmet_infer.py",
        "etc/services/rpi_camera.py",
        "etc/controllers/student.py",
        "etc/controllers/guest.py",
        "etc/ui/student_gui.py",
        "database/db_operations.py"
    ]
    
    print("\n📋 CHECKING KEY FILES:")
    for file in key_files:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
        
        if not exists and "/" in file:
            # Try alternative locations
            basename = os.path.basename(file)
            alternatives = []
            
            # Look in current directory
            if os.path.exists(basename):
                alternatives.append(f"Found in current dir: {basename}")
            
            # Look in subdirectories
            for root, dirs, files in os.walk("."):
                if basename in files:
                    alternatives.append(f"Found at: {os.path.join(root, basename)}")
            
            if alternatives:
                print(f"   💡 Alternative locations:")
                for alt in alternatives[:3]:  # Show max 3
                    print(f"      {alt}")
    
    # Check Python path
    print(f"\n🐍 PYTHON PATH:")
    for i, path in enumerate(sys.path[:5]):  # Show first 5
        print(f"   {i+1}. {path}")
    
    # Test imports
    print(f"\n🔄 TESTING IMPORTS:")
    
    # Test 1: ONNX
    try:
        import onnxruntime
        print("✅ onnxruntime available")
    except ImportError:
        print("❌ onnxruntime not installed")
    
    # Test 2: OpenCV
    try:
        import cv2
        print("✅ opencv (cv2) available")
    except ImportError:
        print("❌ opencv not installed")
    
    # Test 3: Your modules
    test_imports = [
        ("etc.services.helmet_infer", "helmet verification"),
        ("etc.services.rpi_camera", "camera service"),
        ("etc.controllers.student", "student controller"),
        ("database.db_operations", "database operations")
    ]
    
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description} ({module})")
        except ImportError as e:
            print(f"❌ {description} ({module}) - {e}")

def find_best_onnx():
    """Find the ONNX model file"""
    print(f"\n🔍 SEARCHING FOR best.onnx:")
    
    found_files = []
    
    # Search in current directory and subdirectories
    for root, dirs, files in os.walk("."):
        for file in files:
            if file == "best.onnx":
                full_path = os.path.join(root, file)
                size_mb = os.path.getsize(full_path) / 1024 / 1024
                found_files.append((full_path, size_mb))
    
    if found_files:
        print("✅ Found ONNX model files:")
        for path, size in found_files:
            print(f"   📄 {path} ({size:.1f} MB)")
        
        # Recommend the best one
        if len(found_files) == 1:
            print(f"💡 Use this path in helmet_infer.py:")
            print(f"   MODEL_PATH = \"{found_files[0][0]}\"")
        else:
            # Prefer the one in project root
            root_file = next((f for f in found_files if f[0] == "./best.onnx"), None)
            if root_file:
                print(f"💡 Recommended (project root):")
                print(f"   MODEL_PATH = \"best.onnx\"")
    else:
        print("❌ No best.onnx found!")
        print("📥 Please ensure your ONNX model is in the project directory")

def suggest_fixes():
    """Suggest fixes based on findings"""
    print(f"\n🔧 SUGGESTED FIXES:")
    
    fixes = [
        "1. Move best.onnx to project root if it's elsewhere",
        "2. Add this to top of helmet_infer.py:",
        "   import sys, os",
        "   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))",
        "3. Replace relative imports with absolute imports:",
        "   from etc.services.rpi_camera import ...",
        "4. Or add project root to PYTHONPATH:",
        "   export PYTHONPATH=\"$PWD:$PYTHONPATH\"",
    ]
    
    for fix in fixes:
        print(fix)

def main():
    check_file_structure()
    find_best_onnx()
    suggest_fixes()
    
    print(f"\n" + "=" * 50)
    print("🏁 Setup check complete!")

if __name__ == "__main__":
    main()
