"""
Script to delete all PaddleOCR model files in .paddlex/official_models.
Use this to force a clean re-download of all models (may help resolve cache issues).
"""
import os
import shutil

paddlex_models_dir = os.path.expanduser('~/.paddlex/official_models')

if not os.path.exists(paddlex_models_dir):
    print(f"Directory does not exist: {paddlex_models_dir}")
else:
    confirm = input(f"Are you sure you want to delete ALL contents of {paddlex_models_dir}? (yes/no): ")
    if confirm.lower() == 'yes':
        shutil.rmtree(paddlex_models_dir)
        print(f"Deleted: {paddlex_models_dir}")
    else:
        print("Aborted. No files were deleted.")

print("Done.")
