import argparse
from pypdf import PdfReader, PdfWriter

def cleaner():
    parser = argparse.ArgumentParser(description='Remove metadata from PDF files')
    parser.add_argument('-i','--input', type=str, help='Input PDF file')
    parser.add_argument('-o','--output', type=str, help='Output PDF file')
    args = parser.parse_args()

    reader = PdfReader(args.input)
    writer = PdfWriter()

    for page in reader.pages:
        if '/Annots' in page:
            for annot in page['/Annots']:
                obj = annot.get_object()
                if '/T' in obj:
                    obj.pop('/T')

    writer.append_pages_from_reader(reader)

    with open(args.output, 'wb') as fp:
        writer.write(fp)

if __name__ == "__main__":
    cleaner()