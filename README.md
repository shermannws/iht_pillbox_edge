# Edge Layer
## Author
Done by: Sherman Ng Wei Sheng

## Requirements
<u>Tested on the following hardware</u>
Device: Jetson Nano Developer Kit
Ubuntu Version: 18.04
Python Version: 3.9.16

## Directory Description
1. `pico-venv`: contains the python virtual environment with the python dependencies required to run the code
2. `*.ppn`: contains the machine learning model for pico-voice to detect the wake-words
3. `porcupine.py`: entry point to run the edge program

## How to Run
1. Start the virtual environment
```bash
source pico-venv/bin/activate
```
2. Start the script
```bash
python porcupine.py
```
3. When prompted, key in the patient ID that is assigned this pillbox
