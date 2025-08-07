"""
Script to list all files and subdirectories in the PaddleOCR model cache directory.
Use this to verify what is present in .paddlex/official_models and help debug repeated downloads.
"""
import os

paddlex_models_dir = os.path.expanduser('~/.paddlex/official_models')

if not os.path.exists(paddlex_models_dir):
    print(f"Directory does not exist: {paddlex_models_dir}")
else:
    print(f"Listing contents of: {paddlex_models_dir}\n")
    for root, dirs, files in os.walk(paddlex_models_dir):
        level = root.replace(paddlex_models_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

print("\nDone. Check above for model files and subdirectories. If files are missing or incomplete, PaddleOCR may re-download them.")
