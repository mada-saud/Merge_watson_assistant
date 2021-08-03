import argparse
import base64
import configparser
import json
import threading
import time
import pyaudio
import websocket
import requests
import sys
from websocket._abnf import ABNF
from ibm_watson import AssistantV2
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException
from enum import Enum
from typing import Dict, List
from ibm_cloud_sdk_core import BaseService, DetailedResponse
from ibm_cloud_sdk_core.authenticators.authenticator import Authenticator
from ibm_cloud_sdk_core.get_authenticator import get_authenticator_from_environment
from ibm_cloud_sdk_core.utils import convert_model

Url = 'https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/f97ac3c4-fc3b-4b3e-9487-b0d89e11e4b5'
Apikey = 'ezTC8JPerwC2DCCKBnz9O7CMf128OBBgJTqvLrar7oZY'  

Authen = IAMAuthenticator('oqTnr5v65IpOgJ0VAM7_v4CcghnCZWGwOJaG1sh7MgE7')
Assi = AssistantV2(
    version='2021-06-14',
    authenticator = Authen
)

Assi.set_service_url('https://api.eu-gb.assistant.watson.cloud.ibm.com')

Ch = 1024
F = pyaudio.paInt16
Cha = 1
RATE = 44100
RECORD_SECONDS = 5
FINALS = []
Final = None
Response = None

REGION_MAP = {
    'us-east': 'gateway-wdc.watsonplatform.net',
    'us-south': 'stream.watsonplatform.net',
    'eu-gb': 'stream.watsonplatform.net',
    'eu-de': 'stream-fra.watsonplatform.net',
    'au-syd': 'gateway-syd.watsonplatform.net',
    'jp-tok': 'gateway-syd.watsonplatform.net',
}


def error(self, error):
    print(error)

def get_auth():
    configuration = configparser.RawConfigParser()
    configuration.read('speech.cfg')
    Apikey = configuration.get('auth', 'apikey')
    return ("apikey", Apikey)

def on_open(Web):
    args = Web.args
    data = {"action": "start","content-type": "audio/l16;rate=%d" % RATE,"continuous": True,
         "interim_results": True,"word_confidence": True,"timestamps": True,"max_alternatives": 3
            }
    Web.send(json.dumps(data).encode('utf8'))
    threading.Thread(target=read_audio,args=(Web, args.timeout)).start()

def parse_args():
    parser = argparse.ArgumentParser(
        description='Transcribe Watson text in real time')
    parser.add_argument('-t', '--timeout', type=int, default=5)
    args = parser.parse_args()
    return args

def get_url():
    configuration = configparser.RawConfigParser()
    configuration.read('speech.cfg')
    Area = configuration.get('auth', 'region')
    host = REGION_MAP[Area]
    return ("wss://{}/speech-to-text/api/v1/recognize"
           "?model=en-AU_BroadbandModel").format(host)

def message(self, message):
    global Final
    Data = json.loads(message)
    if "results" in Data:
        if Data["results"][0]["final"]:
            FINALS.append(Data)
            Final = None
        else:
            Final = Data
        print(Data['results'][0]['alternatives'][0]['transcript'])

def read_audio(Web, timeout):
    global Average
    python_audio = pyaudio.PyAudio()
    Average = int(python_audio.get_default_input_device_info()['defaultSampleRate'])
    Flow = python_audio.open(format=F,channels=Cha,rate=RATE,input=True,frames_per_buffer=Ch)

    print("Recording")
    Record = timeout or RECORD_SECONDS

    for m in range(0, int(RATE / Ch * Record)):
        Data = Flow.read(Ch)
        Web.send(Data, ABNF.OPCODE_BINARY)
    Flow.stop_stream()
    Flow.close()
    print("* done recording")
    Data = {"action": "stop"}
    Web.send(json.dumps(Data).encode('utf8'))
    time.sleep(1)
    Web.close()
    python_audio.terminate()

def close(Web):
    global Final
    global Response
    global transcript
    if Final:
        FINALS.append(Final)
    transcript = "".join([x['results'][0]['alternatives'][0]['transcript']
                          for x in FINALS])
    return transcript
    
def main():
    Top = {}
    Send = ":".join(get_auth())
    Top["Authorization"] = "Basic " + base64.b64encode(
        Send.encode()).decode()
    The_Url = get_url()
    Web = websocket.WebSocketApp(The_Url,header=Top,on_message=message,on_error=error,on_close=close)
    Web.on_open = on_open
    Web.args = parse_args()
    Web.run_forever()

    outfile = open('Input_text.txt','w')
    outfile.write(close(Web))
    outfile.close()
    

if __name__ == "__main__":
    main()


    Create_Session = Assi.create_session(
    assistant_id='450e28f0-ac2d-4cc8-a5c5-e2a1dbaf3f8f'
    ).get_result()

    Session_Load_File = json.loads(json.dumps(Create_Session, indent=2))
    Id_of_session =Session_Load_File['session_id']

    Assistant_message = Assi.message(
    "450e28f0-ac2d-4cc8-a5c5-e2a1dbaf3f8f",
    Id_of_session,
    input={'text': transcript },
    ).get_result()

    Message_Load_File = json.loads(json.dumps(Assistant_message, indent=2))
    Response = Message_Load_File["output"]["generic"][0]["text"]
    print(Response)


def main():

    authenticator = IAMAuthenticator(Apikey)

    text_2_speech = TextToSpeechV1(authenticator=authenticator)

    text_2_speech.set_service_url(Url)

    with open('Response_Voice.mp3', 'wb') as audio_file:
        r = text_2_speech.synthesize(Response, accept='audio/mp3',voice='en-US_AllisonV3Voice').get_result()
        audio_file.write(r.content)

if __name__ == "__main__":
    main()






   








