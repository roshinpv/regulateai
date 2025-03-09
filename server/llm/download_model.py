import os
import sys
import requests
from tqdm import tqdm
import argparse

def download_file(url, destination):
    """
    Download a file from a URL to a destination with progress bar.
    
    Args:
        url: URL to download from
        destination: Local file path to save to
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    # Check if file already exists
    if os.path.exists(destination):
        print(f"File already exists at {destination}")
        return
    
    # Download with progress bar
    print(f"Downloading from {url} to {destination}")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as file, tqdm(
        desc=os.path.basename(destination),
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def main():
    parser = argparse.ArgumentParser(description='Download LLM model')
    parser.add_argument('--model', type=str, default='llama-3-8b-instruct.Q4_K_M.gguf', 
                        help='Model filename to download')
    parser.add_argument('--url', type=str, 
                        default='https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct.Q4_K_M.gguf',
                        help='URL to download from')
    parser.add_argument('--output-dir', type=str, default='models',
                        help='Directory to save the model')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Download model
    destination = os.path.join(args.output_dir, args.model)
    download_file(args.url, destination)
    
    print(f"Model downloaded successfully to {destination}")

if __name__ == "__main__":
    main()