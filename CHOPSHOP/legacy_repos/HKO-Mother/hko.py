import sys
import os
import yaml
import json
from datetime import datetime
from core.google_drive import DriveFetcher
from core.processor import DocumentProcessor

# --- Configuration ---
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

OUTPUT_DIR = CONFIG['output_directory']
MANIFEST_FILE = CONFIG['manifest_file']
DRIVE_FOLDER_ID = CONFIG['source_drive_folder_id']

# --- 1. Validation Logic ---
def validate_document(text):
    print("... Validating document...")
    if len(text) < CONFIG['validation']['min_length']:
        print("... VALIDATION FAILED: Document is too short.")
        return False
    print("... Validation OK.")
    return True

# --- 2. Orchestration ---
def run_workflow(file_input):
    try:
        print(f"---== STARTING WORKFLOW FOR INPUT: {file_input} ==---")

        if file_input.startswith("local:"):
            # 1A. Fetch from Local Machine
            file_path = file_input.replace("local:", "")
            if not os.path.exists(file_path):
                print(f"[!!] ERROR: Local file not found: {file_path}")
                return
            file_name_raw = os.path.basename(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            print(f"... Fetched local file: {file_name_raw}")
        else:
            # 1B. Fetch from Google Drive
            drive = DriveFetcher(DRIVE_FOLDER_ID)
            file_id = file_input
            file_metadata = drive.service.files().get(fileId=file_id, fields='name').execute()
            file_name_raw = file_metadata['name']
            raw_text = drive.download_file(file_id, file_name_raw)

        # 2. Process
        processor = DocumentProcessor()
        processing_prompt = "You are an expert editor. Review the following document, fix any errors, and format it clearly."
        processed_text = processor.process(raw_text, processing_prompt)

        # 3. Validate
        if not validate_document(processed_text):
            raise Exception("Validation failed for processed document.")

        # 4. Publish
        print("... Publishing to docs folder.")
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        # --- UPDATED FILENAME LOGIC ---
        file_name_base, ext = os.path.splitext(file_name_raw)
        output_filename = f"{datetime.now().strftime('%Y-%m-%d')}-{file_name_base}.html"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        # --- End of Update ---

        html_content = f"<html><head><title>{file_name_base}</title></head><body>"
        html_content += f"<h1>{file_name_base}</h1>"
        html_content += f"<pre>{processed_text}</pre>"
        html_content += "</body></html>"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"... Successfully saved to {output_path}")

        # 5. Update Manifest
        update_manifest(file_name_raw, output_filename)
        print(f"---== WORKFLOW COMPLETE FOR: {file_name_raw} ==---")

    except Exception as e:
        print(f"[!!] WORKFLOW FAILED for {file_input}: {e}")

def update_manifest(file_name, output_filename):
    manifest = []
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)

    entry = {
        'source_name': file_name,
        'output_file': output_filename,
        'processed_date': datetime.now().isoformat()
    }
    manifest.append(entry)

    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
    print("... Manifest updated.")

# --- Main Entry Point ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hko.py <file_id_1> <local:path/to/file.txt> ...")
        sys.exit(1)

    file_inputs = sys.argv[1:]
    print(f"Starting batch process for {len(file_inputs)} file(s).")
    for file_input in file_inputs:
        run_workflow(file_input)
    print("Batch process finished.")