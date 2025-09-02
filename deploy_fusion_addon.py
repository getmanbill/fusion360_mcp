#!/usr/bin/env python3
"""
Fusion 360 Add-in Deployment Utility
Copies the fusion_addon files to the correct Fusion 360 scripts location
"""

import os
import shutil
import sys
import time
from pathlib import Path
from typing import List, Tuple

def get_fusion_scripts_path() -> Path:
    """Get the Fusion 360 scripts directory path"""
    # Standard Fusion 360 scripts location on Windows
    appdata = os.environ.get('APPDATA')
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found")
    
    fusion_scripts = Path(appdata) / "Autodesk" / "Autodesk Fusion 360" / "API" / "Scripts"
    return fusion_scripts

def ensure_directory_exists(path: Path) -> None:
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)
    print(f"SUCCESS: Directory ensured: {path}")

def copy_file_with_logging(src: Path, dst: Path) -> bool:
    """Copy file and log the operation"""
    try:
        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        shutil.copy2(src, dst)
        
        # Verify copy was successful
        if dst.exists():
            src_size = src.stat().st_size
            dst_size = dst.stat().st_size
            if src_size == dst_size:
                print(f"SUCCESS: Copied: {src.name} ({src_size} bytes)")
                return True
            else:
                print(f"ERROR: Size mismatch: {src.name} (src:{src_size} != dst:{dst_size})")
                return False
        else:
            print(f"ERROR: Failed to copy: {src.name}")
            return False
            
    except Exception as e:
        print(f"ERROR: Error copying {src.name}: {e}")
        return False

def copy_directory_recursive(src_dir: Path, dst_dir: Path) -> Tuple[int, int]:
    """Recursively copy directory contents and return (success_count, total_count)"""
    success_count = 0
    total_count = 0
    
    for item in src_dir.rglob('*'):
        if item.is_file():
            # Skip __pycache__ files and .git files
            if '__pycache__' in str(item) or '.git' in str(item):
                continue
                
            relative_path = item.relative_to(src_dir)
            dst_path = dst_dir / relative_path
            
            total_count += 1
            if copy_file_with_logging(item, dst_path):
                success_count += 1
    
    return success_count, total_count

def backup_existing_addon(fusion_scripts: Path, addon_name: str) -> bool:
    """Backup existing addon if it exists"""
    addon_path = fusion_scripts / addon_name
    if addon_path.exists():
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = fusion_scripts / f"{addon_name}_backup_{timestamp}"
        
        try:
            # Copy tree but ignore .git and __pycache__ directories
            def ignore_patterns(dir, files):
                return [f for f in files if f.startswith('.git') or f == '__pycache__']
            
            shutil.copytree(addon_path, backup_path, ignore=ignore_patterns)
            print(f"BACKUP: Backed up existing addon to: {backup_path.name}")
            return True
        except Exception as e:
            print(f"WARNING: Failed to backup existing addon: {e}")
            return False
    else:
        print("INFO: No existing addon found - fresh install")
        return True

def deploy_addon() -> bool:
    """Main deployment function"""
    print("Fusion 360 Add-in Deployment Utility")
    print("=" * 50)
    
    # Get paths
    current_dir = Path.cwd()
    # Check if we're in the fusion_addon directory already
    if current_dir.name == "fusion_addon":
        source_dir = current_dir
    else:
        source_dir = current_dir / "fusion_addon"
    
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        return False
    
    try:
        fusion_scripts = get_fusion_scripts_path()
        print(f"DIR: Fusion scripts directory: {fusion_scripts}")
        
        # Ensure Fusion scripts directory exists
        ensure_directory_exists(fusion_scripts)
        
        # Backup existing addon
        addon_name = "fusion_mcp_addon"
        backup_existing_addon(fusion_scripts, addon_name)
        
        # Deploy new addon
        target_dir = fusion_scripts / addon_name
        print(f"\nINFO: Deploying addon to: {target_dir}")
        
        # Remove existing target if it exists
        if target_dir.exists():
            shutil.rmtree(target_dir)
            print("INFO: Removed existing addon directory")
        
        # Copy all files
        print("\nINFO: Copying addon files...")
        success_count, total_count = copy_directory_recursive(source_dir, target_dir)
        
        # Summary
        print(f"\nSUMMARY: Deployment Summary:")
        print(f"   Files copied: {success_count}/{total_count}")
        print(f"   Success rate: {(success_count/total_count*100):.1f}%")
        
        if success_count == total_count:
            print("\nSUCCESS: DEPLOYMENT SUCCESSFUL!")
            print("\nINFO: Next Steps:")
            print("   1. Open Fusion 360")
            print("   2. Go to Utilities -> ADD-INS")
            print("   3. Click 'Scripts and Add-Ins'")
            print("   4. Select 'fusion_mcp_addon' from the list")
            print("   5. Click 'Run' to start the add-in")
            print("   6. Look for 'Fusion MCP Add-in (v2) started!' message")
            print("\nTEST: Test with:")
            print("   python test_complex_sketch.py")
            return True
        else:
            print(f"\nWARNING: PARTIAL DEPLOYMENT - {total_count - success_count} files failed")
            return False
            
    except Exception as e:
        print(f"\nERROR: DEPLOYMENT FAILED: {e}")
        return False

def main():
    """Main entry point"""
    try:
        success = deploy_addon()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nINFO: Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
