"""
Main entry point for the PDF highlight extraction and export pipeline.
"""
import argparse
import os
import yaml
import json

from export_json import create_enriched_json
from export_csv import create_readwise_csv
from export_md import create_markdown_export

def main():
    """Main function to run the pipeline."""
    
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Extract PDF highlights and export to various formats.")
    parser.add_argument("pdf_path", help="The absolute path to the PDF file to process.")
    parser.add_argument("--output-dir", help="Directory to save output files. Overrides config.yaml.")
    parser.add_argument("--no-csv", action="store_true", help="Disable CSV export.")
    parser.add_argument("--no-md", action="store_true", help="Disable Markdown export.")
    args = parser.parse_args()

    # --- Configuration ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.isabs(args.pdf_path):
        print("Error: Please provide an absolute path for the PDF file.")
        return

    if not os.path.exists(args.pdf_path):
        print(f"Error: The file '{args.pdf_path}' was not found.")
        return

    # Load configuration from config.yaml located in the script's directory
    config_path = os.path.join(script_dir, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # --- Path Setup ---
    bibtex_path = os.path.join(script_dir, config.get("bibtex_path"))

    if args.output_dir:
        # Use the user-specified output directory
        output_dir = args.output_dir
        json_output_dir = output_dir
        csv_output_dir = output_dir
        md_output_dir = output_dir
    else:
        # Use directories from config.yaml, relative to the script directory
        json_output_dir = os.path.join(script_dir, config.get("json_output_dir"))
        csv_output_dir = os.path.join(script_dir, config.get("csv_output_dir"))
        md_output_dir = os.path.join(script_dir, config.get("md_output_dir"))

    # Create output directories if they don't exist
    os.makedirs(json_output_dir, exist_ok=True)
    if not args.no_csv:
        os.makedirs(csv_output_dir, exist_ok=True)
    if not args.no_md:
        os.makedirs(md_output_dir, exist_ok=True)

    # --- File Naming ---
    base_filename = os.path.splitext(os.path.basename(args.pdf_path))[0]
    json_path = os.path.join(json_output_dir, f"{base_filename}.json")

    # --- Run Pipeline ---
    # 1. Create enriched JSON (source of truth)
    create_enriched_json(args.pdf_path, bibtex_path, json_path)

    # 2. Create other exports from the JSON file
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            enriched_data = json.load(f)
        
        meta = enriched_data.get("meta", {})
        citation_key = meta.get("citation_key", base_filename)
        entry_type = meta.get("entry_type", "").lower()

        # Construct new base_filename based on naming convention
        if citation_key and entry_type:
            new_base_filename = f"{citation_key} {entry_type}-pdf"
        else:
            new_base_filename = base_filename

        # Create exports if not disabled
        if not args.no_csv:
            csv_path = os.path.join(csv_output_dir, f"{new_base_filename}.csv")
            create_readwise_csv(json_path, csv_path)

        if not args.no_md:
            md_path = os.path.join(md_output_dir, f"{new_base_filename}.md")
            create_markdown_export(json_path, md_path)

if __name__ == "__main__":
    main()
