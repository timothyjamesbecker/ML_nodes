#!/bin/bash

#cp data/ML_nodes/require.sh ./ && chgrp root require.sh && chown root require.sh && chmod a+x require.sh && ./require.sh > install.log

#build your R install of 3.5
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9
sed -i '$ a deb http://lib.stat.cmu.edu/R/CRAN/bin/linux/ubuntu xenial-cran35/' /etc/apt/sources.list

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
python \
python-dev \
python-pip \
&& apt-get clean

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
mv spark-2.3.1-bin-hadoop2.7 /opt/spark
cd / 
#modify /etc/environment PATH and SPARK_HOME
sed -i '$ a PATH=$PATH":/opt/spark/bin"' /etc/environment
sed -i '$ a SPARK_HOME="/opt/spark"' /etc/environment
export PATH=$PATH":/opt/spark/bin"
export SPARK_HOME="/opt/spark"
sed -i '$ a export PATH=$PATH":/opt/spark/bin"' ~/.bashrc
sed -i '$ a export SPARK_HOME="/opt/spark"' ~/.bachrc
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
pip install -Iv 'h5py>=2.8.0,<2.8.1'
pip install -Iv 'numpy>=1.15,<=1.16'
pip install -I scipy
pip install -I scikit-learn
#pip install -I opencv3
pip install -Iv 'tensorflow>=1.9.0,<1.9.1'
#tensorflow-gpu
pip install -I  chainer


#remote and bio installs
pip install -I paramiko
pip install -I subprocess32
pip install -Iv 'pysam>=0.9.0,<0.9.2'
