# Edge Layer
## Author
Done by: Sherman Ng Wei Sheng

## Requirements
<u>Tested on the following hardware / software</u>:<br/>
Device: Jetson Nano Developer Kit<br/>
Ubuntu Version: 18.04<br/>
Python Version: 3.9.16<br/>

## Directory Description
1. `*.ppn`: contains the machine learning model for pico-voice to detect the wake-words
2. `pill-detect.py`: entry point to run the pill detection model
3. `porcupine.py`: entry point to run the edge program
4. `requirements.txt`: necessary python packages

## How to Run
1. Prepare the environment variables. The following environment variables should be present in the `.env` file.
```
PICO_API_KEY=\<ACCESS KEY TO PICOVOICE>
MQTT_IP_ADDR=\<IP ADDRESS OF MQTT BROKER>
MQTT_PORT=\<PORT OF MQTT BROKER>
ROBOFLOW_API_KEY=\<API KEY TO ROBOFLOW>
```
2. Start the virtual environment / or create one and ensure that all requirements are installed
```bash
source pico-venv/bin/activate
pip install -r requirements.txt
```
3. Start the script that contains the pill detection model
```bash
python pill-detect.py
```
4. Start the script that contains the main edge application and speech recognition
```bash
python porcupine.py
```
5. When prompted, key in the patient ID that is assigned this pillbox
