import os
import shutil

def cleanup_old_files():
    """Clean up any old files from previous sessions"""
    upload_folder = "uploaded_files"
    
    if not os.path.exists(upload_folder):
        print("📁 Upload folder doesn't exist")
        return
    
    print("🧹 Cleaning up old files...")
    
    items = os.listdir(upload_folder)
    cleaned_files = 0
    cleaned_folders = 0
    
    for item in items:
        item_path = os.path.join(upload_folder, item)
        
        if os.path.isfile(item_path):
            # Remove loose files
            os.remove(item_path)
            print(f"🗑️ Removed file: {item}")
            cleaned_files += 1
        elif os.path.isdir(item_path):
            # Remove directories (including old session folders)
            shutil.rmtree(item_path)
            print(f"🗑️ Removed folder: {item}")
            cleaned_folders += 1
    
    print(f"✅ Cleanup complete! Removed {cleaned_files} files and {cleaned_folders} folders")

if __name__ == "__main__":
    cleanup_old_files()
