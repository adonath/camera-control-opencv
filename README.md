# Gammapy CTA Symposium Demo

## Package requirements
To test  you will need the packages listed in opencv.yml. To create and activate a conda environment with all the imports needed, do:

```bash
conda env create -f opencv.yml
conda activate opencv
```
To start the apps:

```bash

python capture/app.py

cd gallery
python app.py --port 8000 snapshots/
```
Both apps can run on the same laptop, but should use a different port.