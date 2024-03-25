import struct
import pyaudio
import pvporcupine
import Jetson.GPIO as GPIO
import time 
import json
import paho.mqtt.client as mqtt
from hx711 import HX711

#hx711 setup
import sys
import gpiod

chip = gpiod.Chip("0", gpiod.Chip.OPEN_BY_NUMBER)

def cleanAndExit():
    print("Cleaning...")

    chip.close()
        
    print("Bye!")
    sys.exit()

#hx_before = HX711(dout = 15, pd_sck = 13, chip = chip)
#referenceUnit_before = 9.7392
hx_after = HX711(dout = 23, pd_sck = 21, chip = chip)
referenceUnit_after = 118

#hx_before.set_reading_format("MSB", "MSB")
hx_after.set_reading_format("MSB", "MSB")

#hx_before.set_reference_unit(referenceUnit_before)
hx_after.set_reference_unit(referenceUnit_after)

#hx_before.reset()
hx_after.reset()

#hx_before.tare()
hx_after.tare()

def get_weight(hx):
    val = hx.get_weight(11)

    hx.power_down()
    hx.power_up()
    time.sleep(0.1)

    return val

    
#MQTT setup
is_mqtt_enabled = None
patient_id = input("Patient ID: ")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

def on_connect(client, userdata, flags, rc, properties):
    client.subscribe("reminder/led")
    print('Connected with result code '+str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(json.loads(msg.payload)))
    try:
        body = json.loads(msg.payload)
        if msg.topic == "reminder/led" and int(body["patientId"]) == int(patient_id):
            handle_led(body["type"])
    except ValueError as e:
        return False
    return True
    
def handle_led(t):
    if t == "before":
        start_blink(before_pin, 10)
    elif t == "after":
        start_blink(after_pin, 10)

def start_blink(led, times):
    for i in range(times):
        print("here")
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(led, GPIO.LOW)
        time.sleep(0.5)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

try:
    #client.connect('192.168.1.177', 1883, 60)
    client.connect('192.168.50.177', 1883, 60)
    is_mqtt_enabled = True
    client.loop_start()
except:
    is_mqtt_enabled = False
    print("there")

#pico setup
access_key = 'TkrVuBilUvGh7RBxRcfRpWBb+vwa2Fr62pmMKa4QffGqV+edroOM+g=='
before_model = '/home/edge-01/Desktop/iht_project/picovoice/Before-Food_en_jetson_v3_0_0.ppn'
after_model ='/home/edge-01/Desktop/iht_project/picovoice/After-Food_en_jetson_v3_0_0.ppn'
porcupine = pvporcupine.create(
  access_key=access_key,
  keyword_paths=[before_model, after_model]
)
pa = None
audio_stream = None

#gpio setup
before_pin = 7
after_pin = 11
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(before_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(after_pin, GPIO.OUT, initial=GPIO.LOW)


pa = pyaudio.PyAudio()
audio_stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length)

def get_next_audio_frame():
    pcm = audio_stream.read(porcupine.frame_length)
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
    return pcm

def handle_pill_load(load):
    pass

#start
before_state = 0 #0 nothing; 1 pill putting; 2 not consumed
after_state = 0
before_weight = None
after_weight = None

def cross_threshold(current, ref):
    threshold = 2
    return abs(current - ref) > threshold

def wait_for_pill(hx, led):
    before = get_weight(hx)
    GPIO.output(led, GPIO.HIGH)
    threshold = 2
    while True:
        next = get_weight(hx)
        if abs(next-before) > 2:
            return next
        
    

while True:
    try:
        keyword_index = porcupine.process(get_next_audio_frame())
        if keyword_index == 0 and before_state == 0:
            print("before detected")
            before_state += 1
            continue
        elif keyword_index == 1 and after_state == 0:
            print("after detected")
            after_state += 1
            continue

        
        if before_state == 1:
            #handle before pill tracking
            print("waiting for before pills")
            before_weight = wait_for_pill(hx_after, before_pin)
            payload = {"patient_id":patient_id, "action":"before_new", "weight":before_weight}
            client.publish('pills/status',payload=json.dumps(payload),qos=0)
            GPIO.output(before_pin, GPIO.LOW)
            before_state += 1
            continue
        if after_state == 1:
            #handle after pill tracking
            print("waiting for before pills")
            after_weight = wait_for_pill(hx_after, after_pin)
            payload = {"patient_id":patient_id, "action":"after_new", "weight":after_weight}
            client.publish('pills/status',payload=json.dumps(payload),qos=0)
            GPIO.output(after_pin, GPIO.LOW)
            after_state += 1
            continue

        if before_state == 2:
            print("checking if before decreased")
            current_weight = get_weight(hx_after)
            if cross_threshold(current_weight, before_weight):
                print("Before Weight decreased!")
                payload = {"patient_id":patient_id, "action":"before_take"}
                client.publish('pills/status', payload=json.dumps(payload), qos=0)
                before_state = 0
                before_weight = None
                
        if after_state == 2:
            print("checking if after decreased")
            current_weight = get_weight(hx_after)
            if cross_threshold(current_weight, after_weight):
                print("After Weight decreased!")
                payload = {"patient_id":patient_id, "action":"after_take"}
                client.publish('pills/status', payload=json.dumps(payload), qos=0)
                after_state = 0
                after_weight = None

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
        client.loop_stop()
        GPIO.cleanup()



