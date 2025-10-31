## About The Project
This repository is designed to host all the code used in the development of the Multi-Contrast X-ray Nanoscope, hosted at The Francis Crick Institute

## Built With
The scripts are a mixture of python and Matlab files. Please install both before proceeding. I advise also installing a Python IDE, here we use spyder
The reconstruction pipeline requires installation of CIL
https://github.com/TomographicImaging/CIL.git

## Usage
- Control scripts are used to acquire data. The master script CT.py runs tomographic acquisition with the help of custom librarys for control of motors, detectors and source.
- Processing scripts form a pipeline for reconstruction of phase-contrast data.
  - find and correct for stability issues
  - measure the geometry of the scan
  - run flat field correction, while accounting for drifts and artefacts
  - Integration via Paganin Phase retreival
- Utilities are functions to help with the processing scripts

## Contact
Adam Doherty - doherta@crick.ac.uk
