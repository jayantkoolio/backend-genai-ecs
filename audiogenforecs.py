import json
import torch
import soundfile as sf
import os
import music_tag
import boto3
from audiocraft.models import AudioGen
from dotenv import load_dotenv
import sys

model = AudioGen.get_pretrained('facebook/audiogen-medium')

load_dotenv()
RECEIPT_HANDLE = os.environ.get("RECEIPT_HANDLE")
QUEUE_URL = os.environ.get("QUEUE_URL")

s3 = boto3.resource('s3')
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
data = json.loads(data)
print(data)
prompt = data['positive_text']
username = data['username']
ENV = data['env']
job = data['jobname']
FILENAME =  prompt + "_audiogen" +  ".wav"
duration = data['duration']
create_audio(prompt, FILENAME, username, ENV, duration, job)
return "Done"
