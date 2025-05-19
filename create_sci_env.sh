#!/bin/bash

# Usage: ./create_scientific_env.sh my-env-name

ENV_NAME="$1"

if [ -z "$ENV_NAME" ]; then
  echo "Usage: $0 <env-name>"
  exit 1
fi

mkdir "$ENV_NAME"
cd "$ENV_NAME" || exit

# Create pixi.toml
cat > pixi.toml <<EOF
[project]
name = "$ENV_NAME"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64"]

[dependencies]
numpy = "*"
scipy = "*"
matplotlib = "*"
jupyter = "*"
notebook = "6.*"
pandas = "*"
scikit-learn = "*"
scikit-image = "*"
uncertainties = "*"
opencv = "*"
pandoc = "*"
jupyter-book = "*"
ipywidgets = "*"
astropy = "*"
dask = "*"
mysqlclient = "*"
seaborn = "*"
tifffile = "*"
tqdm = "*"
pytest = "*"
matplotlib-scalebar = "*"
ffmpeg = "*"
rise = "*"
jupyter_contrib_nbextensions = "*"
EOF

# Install environment
pixi install

# Setup Jupyter nbextensions
pixi run jupyter contrib nbextension install --user
pixi run jupyter nbextension enable rise/main

echo "✅ Pixi environment '$ENV_NAME' created and configured."

