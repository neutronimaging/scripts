import argparse
import numpy as np
import matplotlib.pyplot as plt
from bm4d import bm4d
from tqdm import tqdm
import tifffile as tiff
# import nrrd
import json
import psutil
import time
from pathlib import Path
import re

import sys
sys.path.append('../')
import amglib.readers as rd

def test_volume_limit(initial_size=(50, 50, 50), increment=(50, 50, 50), max_attempts=50):
    print("Running test denoising on increasing volume sizes to determine the maximum size that can be processed without running out of memory.")
    
    """Test the volume size limit of BM4D."""
    size = np.array(initial_size)
    for attempt in range(max_attempts):
        print(f"Testing volume size: {tuple(size)}")
        try:
            # Create a random volume of the current size
            volume = np.random.rand(*size) * 255
            # Apply BM4D denoising
            start_time = time.time()
            bm4d(volume, sigma_psd=25)  # Adjust sigma_psd as needed
            end_time = time.time()
            # Check memory usage
            memory_info = psutil.virtual_memory()
            print(f"Memory used: {memory_info.used / (1024 ** 2):.2f} MB")
            print(f"Time taken: {end_time - start_time:.2f} seconds")
            print("Success!")
        except Exception as e:
            print(f"Failed at size {tuple(size)}. Error: {e}")
            break
        # Increment the volume size
        size += increment


def test_run():
    test_volume_limit(initial_size=(50, 50, 50), increment=(50, 50, 50), max_attempts=50)
    return

def load_3d_volume(filepath, first, last,roi=None):
    """Load a 3D volume from a .tif, preserving its data type."""

    volume = rd.read_images(filepath, first=first, last=last)

    if roi is not None:
        x_start, x_end, y_start, y_end = roi
        volume = volume[:, y_start:y_end, x_start:x_end]

    return volume  # No normalization applied


def save_3d_volume(volume, filepath):
    """Save a 3D volume to a .tif or .nrrd file, preserving its data type."""

    rd.save_TIFF(filepath, volume)


def process_block(block, sigma_psd=0.1):
    """Denoise a single block using BM4D."""
    return bm4d(block, sigma_psd=sigma_psd)


def divide_volume(volume, block_size, overlap):
    """Divide the volume into overlapping blocks."""
    z, y, x = volume.shape
    blocks = []
    block_coords = []

    z_step = block_size[0] - overlap
    y_step = block_size[1] - overlap
    x_step = block_size[2] - overlap

    for z_start in range(0, z, z_step):
        for y_start in range(0, y, y_step):
            for x_start in range(0, x, x_step):
                z_end = min(z_start + block_size[0], z)
                y_end = min(y_start + block_size[1], y)
                x_end = min(x_start + block_size[2], x)

                # Extract block
                block = volume[z_start:z_end, y_start:y_end, x_start:x_end]

                # If the block is smaller than expected, pad it
                pad_width = [
                    (0, block_size[0] - block.shape[0]),
                    (0, block_size[1] - block.shape[1]),
                    (0, block_size[2] - block.shape[2]),
                ]
                block = np.pad(block, pad_width, mode="constant", constant_values=0)

                blocks.append(block)
                block_coords.append((z_start, z_end, y_start, y_end, x_start, x_end))

    return blocks, block_coords


def merge_blocks(blocks, block_coords, volume_shape):
    """Merge blocks into the final volume by directly stitching them."""
    merged_volume = np.zeros(volume_shape, dtype=blocks[0].dtype)

    for block, (z_start, z_end, y_start, y_end, x_start, x_end) in zip(blocks, block_coords):
        # Clip block to fit within the original volume dimensions
        z_clip = slice(0, z_end - z_start)
        y_clip = slice(0, y_end - y_start)
        x_clip = slice(0, x_end - x_start)

        merged_volume[z_start:z_end, y_start:y_end, x_start:x_end] = block[z_clip, y_clip, x_clip]

    return merged_volume


def denoise_large_volume(volume, block_size=(25, 25, 25), overlap=1, sigma_psd=0.3):
    """Denoise a large 3D volume using BM4D with overlapping block processing."""
    print(f"Volume shape: {volume.shape}")
    print(f"Block size: {block_size}, Overlap: {overlap}")
    
    # Divide the volume into overlapping blocks
    blocks, block_coords = divide_volume(volume, block_size, overlap)
    print(f"Number of blocks: {len(blocks)}")
    
    # Apply BM4D to each block
    denoised_blocks = []
    for block in tqdm(blocks, desc="Denoising blocks"):
        denoised_block = process_block(block, sigma_psd=sigma_psd)
        denoised_blocks.append(denoised_block)

    # Merge the denoised blocks
    denoised_volume = merge_blocks(denoised_blocks, block_coords, volume.shape)

    return denoised_volume


def visualize_slices(original_volume, denoised_volume, slice_index=None):
    """Visualize the original, denoised, and difference slices."""
    if slice_index is None:
        slice_index = original_volume.shape[0] // 2  # Default to the middle slice

    original_slice = original_volume[slice_index, :, :]
    denoised_slice = denoised_volume[slice_index, :, :]
    difference_slice = np.abs(original_slice - denoised_slice)

    fig, axs = plt.subplots(1, 3, figsize=(18, 6))

    axs[0].imshow(original_slice, cmap='gray')
    axs[0].set_title("Original Slice")
    axs[0].axis('off')

    axs[1].imshow(denoised_slice, cmap='gray')
    axs[1].set_title("Denoised Slice")
    axs[1].axis('off')

    axs[2].imshow(difference_slice, cmap='plasma')
    axs[2].set_title("Difference Map")
    axs[2].axis('off')

    plt.tight_layout()
    plt.show()

def build_default_config_path(output_filepath):
    """Build a config JSON path next to output images based on the output mask."""
    output_path = Path(output_filepath)
    output_dir = output_path.parent
    stem = output_path.stem

    # Remove formatting placeholders such as {0:04d} from the output stem.
    stem = re.sub(r"\{[^{}]*\}", "", stem).rstrip("_- ")
    if not stem:
        stem = "bm4d"

    return output_dir / f"{stem}_config.json"

def save_config(parameters, output_filepath, config_path=None):
    """Save denoising parameters as JSON near the output images."""
    target_path = Path(config_path) if config_path else build_default_config_path(output_filepath)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(parameters, f, indent=2)

    print(f"Saved configuration to {target_path}")

def process(parameters):
    # Load the 3D volume
    input_filepath  = parameters.get('input_filepath')
    output_filepath = parameters.get('output_filepath')
    first_slice     = parameters.get('first',0)
    last_slice      = parameters.get('last',100)
    roi             = parameters.get('roi', None)

    if input_filepath is None or output_filepath is None:
        raise ValueError("Input and output file paths must be specified.")
    
    original_volume = load_3d_volume(input_filepath,
                                     first = first_slice,
                                     last  = last_slice,
                                     roi   = roi)

    # Denoise the volume
    block_size = parameters.get('block_size', (250, 250, 250))
    overlap    = parameters.get('overlap', 2)
    sigma_psd  = parameters.get('sigma_psd', 9000)

    denoised_volume = denoise_large_volume(original_volume, block_size, overlap, sigma_psd).astype(original_volume.dtype)
    print(f"Denoising completed for volume shape: {original_volume.shape}, dtype: {original_volume.dtype}")
    print(f"Denoised volume shape: {denoised_volume.shape}, dtype: {denoised_volume.dtype}")    
    # denoised_volume = original_volume

    # Visualize the results (use the middle slice by default)
    if parameters.get('visualize', False):
        visualize_slices(original_volume, denoised_volume)

    # Save the denoised volume
    save_3d_volume(denoised_volume, output_filepath)
    print(f"Denoised volume saved to {output_filepath}")
    save_config(parameters, output_filepath)

def run(args):
    if args.test:
        # Run test denoising on increasing volume sizes to determine the maximum size that can be
        # processed without running out of memory
        test_run()
        return
    
    elif args.saveraw:
        if args.input is None or args.output is None:
            raise ValueError("Input and output file paths must be specified for saving raw volume.")
        
        # Load the 3D volume
        original_volume = load_3d_volume(args.input, first=args.first, last=args.last, roi=args.roi)
        save_3d_volume(original_volume, args.output)
        print(f"Raw volume saved to {args.output}")
        return
    
    elif args.config is not None:
        with open(args.config, 'r') as f:
            parameters = json.load(f)
    else:
        parameters = {
            'input_filepath':  args.input,
            'output_filepath': args.output,
            'block_size':     (args.blocksize, args.blocksize, args.blocksize),
            'overlap':         args.overlap,
            'sigma_psd':       args.sigma,
            'visualize':       args.visualize,
            'first':           args.first,
            'last':            args.last,
            'roi':             args.roi
        }   

    process(parameters)

if __name__ == "__main__":
    # Filepath for input volume

    parser = argparse.ArgumentParser(description='BM3D Denoising for 3D Volumes')
    parser.add_argument('-i','--input',     type=str, help='Input file mask')
    parser.add_argument('-o','--output',    type=str, help='Output file mask')
    parser.add_argument('-b','--blocksize', type=int, default=250, help='Block size for denoising (default: 250)')
    parser.add_argument('-p','--overlap',   type=int, default=2, help='Overlap size for denoising (default: 2)')
    parser.add_argument('-w','--saveraw',   action='store_true', help='Save the raw volume')
    parser.add_argument('-s','--sigma',     type=float, default=9000, help='Sigma value for BM4D denoising (default: 9000)')
    parser.add_argument('-v','--visualize', action='store_true',help='Visualize the denoising results')
    parser.add_argument('-f','--first',     type=int, default=None, help='First slice to denoise')
    parser.add_argument('-l','--last',      type=int, default=None, help='Last slice to denoise')
    parser.add_argument('-r','--roi',       type=int, nargs=4, help='Region of interest (ROI) in the format: x_start x_end y_start y_end',default=None)
    parser.add_argument('-t','--test',      action='store_true', help='Run test denoising on increasing volume sizes to determine the maximum size that can be processed without running out of memory') 
    parser.add_argument('-c','--config',    type=str, default=None, help='Path to a configuration file (.json) for denoising parameters (optional). CLI parameters will override.') 
    args = parser.parse_args()

    run(args)