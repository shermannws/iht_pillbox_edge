# Edge Layer
## Author
Done by: Sherman Ng Wei Sheng

## Requirements
<u>Tested on the following hardware / software</u>:<br/>
Device: Jetson Nano Developer Kit<br/>
Ubuntu Version: 18.04<br/>
Python Version: 3.9.16<br/>

## Directory Description
1. `pico-venv`: contains the python virtual environment with the python dependencies required to run the code
2. `*.ppn`: contains the machine learning model for pico-voice to detect the wake-words
3. `porcupine.py`: entry point to run the edge program
4. `requirements.txt`: necessary python packages

## How to Run
1. Prepare the environment variables. The following environment variables should be present in the `.env` file.
```
PICO_API_KEY=\<ACCESS KEY TO PICOVOICE>
MQTT_IP_ADDR=\<IP ADDRESS OF MQTT BROKER>
MQTT_PORT=\<PORT OF MQTT BROKER>
```
2. Start the virtual environment / or create one and ensure that all requirements are installed
```bash
source pico-venv/bin/activate
pip install -r requirements.txt
```
3. Start the script
```bash
python porcupine.py
```
4. When prompted, key in the patient ID that is assigned this pillbox
