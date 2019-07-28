# FROM python:2.7.16-stretch
FROM ubuntu:16.04

ENV PYTHON_VERSION 2.7
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y \
    apt-utils \
    build-essential \
    ca-certificates \
    gcc \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    wget \
    unzip \
    curl \
    bzip2 \
    git \
    sudo \
    nano \
    vim \
    screen \
    libgtk2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

# Installation miniconda3
RUN curl -sSL http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -o /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -bfp /usr/local && \
    rm -rf /tmp/miniconda.sh

# # Set up conda environment
# RUN conda install -y python=${PYTHON_VERSION} && \
#     conda update -y conda

# RUN pip install --upgrade pip

COPY requirements_cpu.txt requirements.txt
RUN pip --no-cache-dir install -r requirements.txt && \
    rm requirements.txt
# RUN pip --no-cache-dir install && \
#     numpy && \
#     scikit-image && \
#     scipy && \
#     tensorflow~=1.4.1 && \
#     opencv-python~=3.4.2.17

RUN conda install -c conda-forge dlib=19.10

# Clean up
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    conda clean --all --yes

# Set default work directory
RUN mkdir /workspace
WORKDIR /workspace

CMD /bin/bash
