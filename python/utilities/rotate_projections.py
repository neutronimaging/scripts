import numpy as np
import sys
import argparse

sys.path.append('../')
import amglib.readers as rd

def mask_modifier(mask,st) :
    s=mask.split('.')
    s.insert(-1,st)
    s.insert(-1,'.')
    return ''.join(s)

def convert_files(mask, first, last, angle,output=None):
    if not output:
        output = mask_modifier(mask,'_rot')        
    
    for idx in range(int(first), int(last) + 1):
        file_name = mask.format(idx)
        try:
            # data = rd.read(file_name)
            output_file_name = output.format(idx)
            print(f"Rotating {file_name} by {angle} degrees -> {output_file_name}")
            # rd.write(output_file_name, data)
            
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")


if __name__ == "__main__":
    # Replace with your repository and token
    
    parser = argparse.ArgumentParser(description="Fetches an issue list from GitHub.")
    parser.add_argument('-m','--mask', help="File mask in the format <path>/<mask>{0:0N}.ext. Mask is the base name of the file e.g. img_, N is the number of zero padding, and ext is the file extension (tif, fit are supported)", default=None)
    parser.add_argument('-f','--first', help="The fist file index to convert")
    parser.add_argument('-l','--last', help="The last file index to convert.") 
    parser.add_argument('-o','--output', help="The output file mask in the format <path>/<mask>{0:0N}.ext. Warning, don't use the same as the input they will be overwritten", default=None)
    parser.add_argument('-a','--angle', help="Rotation angle.", default=0.0, type=float)
    
    args = parser.parse_args()
    
    convert_files(mask=args.mask, first=args.first, last=args.last, angle=args.angle,output=args.output)
#     parser.add_argument('-c','--closed', help="Fetch closed issues.", action="store_true", default=False)
    