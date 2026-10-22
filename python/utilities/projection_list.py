import numpy as np
import argparse
import csv
from itertools import zip_longest

import sys

sys.path.append('../')

import amglib.readers as rd

def main() :
    parser = argparse.ArgumentParser(description='Creates a file list for MuhRec (angle, filename)')
    parser.add_argument('-i','--input', type=str, help='Input file mask')
    parser.add_argument('--first', type=int,help='The first file in the sequence')
    parser.add_argument('--last', type=int, help='The last file in the sequence')
    parser.add_argument('-o','--output', default="projections.csv", type=str, help='Projection file list (.csv)')
    args = parser.parse_args()

    data=rd.read_fits_meta_data2(args.input,args.first,args.last,parlist = ['HIERARCH sample_position_2/sp2_ry'], include_fname=True)

    for key, values in data.items():
        if key != 'filename':
            data[key] = [float(value.split()[0]) if isinstance(value, str) else float(value) for value in values]

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        # writer.writerow(data.keys())
        writer.writerows(zip_longest(*data.values(), fillvalue=""))



if __name__ == "__main__":
    main()