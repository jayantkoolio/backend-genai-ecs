import json
import torch
import soundfile as sf
import os
import music_tag
import boto3
from audiocraft.models import AudioGen
from dotenv import load_dotenv
import sys

model = AudioGen.get_pretrained('./huggingface/hub/models--facebook--audiogen-medium/snapshots/389bbdcd572a583ebf9e120b1a0f9f809eb005a2/')

AWS_SERVER_PUBLIC_KEY = os.environ["ACCESS_KEY"]
AWS_SERVER_SECRET_KEY = os.environ["SECRET_KEY"]

load_dotenv()
RECEIPT_HANDLE = os.environ.get("RECEIPT_HANDLE")
QUEUE_URL = os.environ.get("QUEUE_URL")

# s3 = boto3.resource('s3')
# s3 = boto3.resource("s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

session = boto3.Session(
    aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
)

s3 = session.resource("s3")

BUCKET = "ns.riffusion.test"
FOLDER = "dev_audiogen/"
FOLDER_QA = "qa_audiogen/"


def create_audio(prompt, filename, username, env, length, jobnam):
    model.set_generation_params(
        use_sampling=True,
        top_k=250,
        duration=length
    )
    res = model.generate(descriptions=[prompt],progress=True)
    res_cpu = res.cpu()
    audio_array = res_cpu.numpy()
    sampling_rate = 16000
    audio_array = audio_array.squeeze()
    sf.write(filename, audio_array, sampling_rate)
    audio = music_tag.load_file(filename)
    audio['Title'] = username
    audio['Composer'] = env
    audio['Albumartist'] = jobnam
    audio.save()
    if env == "qa":
      folder = FOLDER_QA
    else :
      folder = FOLDER
    saved_filename_with_format = folder + filename
    s3.Bucket(BUCKET).upload_file(filename, saved_filename_with_format)
    if os.path.exists(filename):
        os.remove(filename)
    sqs_client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=RECEIPT_HANDLE)

data = os.environ.get("DATA")
print(data)
# data = '{"positive_text": "cat meowing", "username": "jayant1_lambda", "env" : "development", "jobname": "ecefb906-27c5-4024-a83f-fb689dfd7365", "duration": "5.0" }'
data = json.loads(data)
prompt = data['positive_text']
username = data['username']
ENV = data['env']
job = data['jobname']
FILENAME =  prompt + "_audiogen" +  ".wav"
duration = float(data['duration'])
create_audio(prompt, FILENAME, username, ENV, duration, job)
