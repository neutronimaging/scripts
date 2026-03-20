#!/bin/sh

ROOT_DIR="${1:-.}"

find "$ROOT_DIR" \
    -type f \( \
        -name "*.c" -o -name "*.cpp" -o -name "*.cc" -o -name "*.cxx" -o \
        -name "*.h" -o -name "*.hpp" -o -name "*.hxx" \
    \) \
| while read -r file; do
    # Extract include lines → normalize → extract basename
    sed -n 's/^[[:space:]]*#include[[:space:]]*["<]\([^">]*\)[">].*/\1/p' "$file" \
    | xargs -n1 basename
done \
| sort \
| uniq -c \
| sort -nr


# #!/bin/sh

# # Directory to scan (default: current dir)
# ROOT_DIR="${1:-.}"

# # Find all C/C++ source files
# # Add or remove extensions depending on your project
# find "$ROOT_DIR" \
#     -type f \( \
#         -name "*.c" -o -name "*.cpp" -o -name "*.cc" -o -name "*.cxx" -o \
#         -name "*.h" -o -name "*.hpp" -o -name "*.hxx" \
#     \) \
# | while read -r file; do
#     # Extract include lines
#     # Normalize the header name by removing #include, whitespace, quotes, angle brackets
#     sed -n 's/^[[:space:]]*#include[[:space:]]*["<]\([^">]*\)[">].*/\1/p' "$file"
# done \
# | sort \
# | uniq -c \
# | sort -nr
