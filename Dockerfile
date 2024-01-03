FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y wget

ENV DEBIAN_FRONTEND=noninteractive

# Installing NVIDIA and CUDA 12.2 drivers for ubuntu 22.04
#
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
RUN mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
RUN wget https://developer.download.nvidia.com/compute/cuda/12.2.2/local_installers/cuda-repo-ubuntu2204-12-2-local_12.2.2-535.104.05-1_amd64.deb
RUN dpkg -i cuda-repo-ubuntu2204-12-2-local_12.2.2-535.104.05-1_amd64.deb
RUN cp /var/cuda-repo-ubuntu2204-12-2-local/cuda-F73B257B-keyring.gpg /usr/share/keyrings/
RUN apt-get update
RUN apt-get -y install cuda

WORKDIR /app

COPY . .

RUN apt-get install -y python3-pip
RUN pip3 install -r requirements.txt

RUN chmod +x ./app.py

CMD ["python3", "app.py"]
