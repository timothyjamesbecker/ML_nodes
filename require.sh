#!/bin/bash

#cp data/ML_nodes/require.sh ./ && chgrp root require.sh && chown root require.sh && chmod a+x require.sh && ./require.sh > install.log

#build your R install of 3.5
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9
sed -i '$ a deb http://lib.stat.cmu.edu/R/CRAN/bin/linux/ubuntu xenial-cran35/' /etc/apt/sources.list
add-apt-repository ppa:alex-p/tesseract-ocr

#deb https://cloud.r-project.org/bin/linux/ubuntu xenial-cran35/

#apt installs
apt-get update && apt-get install -y \
ant \
build-essential \
openjdk-8-jdk-headless \
cmake \
g++ \
gfortran \
git \
maven \
wget \
nano \
screen \
system-config-lvm \
docker.io \
libffi6 \
libffi-dev \
libssl1.0.0 \
libssl-dev \
libblas3 \
libblas-dev \
liblapack3 \
liblapack-dev \
libcurl4-openssl-dev \
libxml2-dev \
libncurses5-dev \
libbz2-dev \
zlib1g-dev \
r-base \
tesseract-ocr \
libtesseract-dev \
python \
python-dev \
python-pip \
python-numpy \
python-scipy \
python-sklearn \
python-h5py \
&& apt-get clean

#proxy server setup for head nodes
apt-get install squid
cp /etc/squid.squid.conf .etc/squid.conf.old
chmod a-w /etc/squid/squid.conf.old

#mysql python interface
mkdir /software
cd /software
git clone https://github.com/mysql/mysql-connector-python.git
cd mysql-connector-python
python ./setup.py build
python ./setup.py install
cd /

#spark install setup
cd /software
wget http://mirror.reverse.net/pub/apache/spark/spark-2.3.1/spark-2.3.1-bin-hadoop2.7.tgz
tar -xzf spark-2.3.1-bin-hadoop2.7.tgz
rm spark-2.3.1-bin-hadoop2.7.tgz
mv spark-2.3.1-bin-hadoop2.7 /software/spark
chgrp -R root /software/spark
chown -R root /software/spark
cd / 
#modify /etc/environment PATH and SPARK_HOME
sed -i '1 c PATH="/usr/local/sbin:/usr/local/bin:/sur/sbin:/usr/bin:/sbin:/bin:/software/spark/bin"' /etc/environment
sed -i '$ a SPARK_HOME="/software/spark"' /etc/environment
export PATH=$PATH":/software/spark/bin"
export SPARK_HOME="/software/spark"
sed -i '$ a export PATH=$PATH":/software/spark/bin"' ~/.bashrc
sed -i '$ a export SPARK_HOME="/software/spark"' ~/.bachrc
echo 'PATH is now set to: '$PATH
echo 'SPARK_HOME is now set to: '$SPARK_HOME

#cuda install setup from nvidia installers...

#R installers
Rscript --save -e "install.packages('sparklyr'); install.packages('ggplot2')"
Rscript --save -e "source('https://bioconductor.org/biocLite.R'); biocLite('DNAcopy'); biocLite('cn.mops'); biocLite('ballgown');"

#pip installers
pip install -I argparse
pip install -Iv 'cython>=0.24.0,<0.25.0'
pip install -Iv 'pyspark>2.3,<=2.3.1'
pip install -I piexif
pip install -I opencv-contrib-python
pip install -I pytesseract
pip install -I tensorflow
#tensorflow-gpu
pip install -I  chainer

#remote and bio installs
pip install -I paramiko
pip install -I subprocess32
pip install -Iv 'pysam>=0.9.0,<0.9.2'
