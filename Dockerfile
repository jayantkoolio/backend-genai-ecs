FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y wget

ENV DEBIAN_FRONTEND=noninteractive

# Installing NVIDIA and CUDA drivers for ubuntu 22.04
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
RUN mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
RUN wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb
RUN dpkg -i cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb
RUN cp /var/cuda-repo-ubuntu2204-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
RUN apt-get update
RUN apt-get install -y cuda

WORKDIR /app

COPY . .

RUN apt-get install -y python3-pip
RUN pip install -r requirements.txt

RUN chmod +x ./app.py

CMD ["python3", "app.py"]