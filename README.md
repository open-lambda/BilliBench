# BilliBench

BilliBench is a benchmark for serverless billing models in the paper "Making Serverless Pay-For-Use a Reality with Leopard". The function suite enables an analysis of SLIM assumptions of existing serverless billing models across a variety of resource usage patterns. 

## Usage

For each function, we provide (1) a script to generate the payload and upload to Google Cloud Storage as buckets, and (2) a script to run the function. Please follow the instructions below to run these scripts.

### Environment Variables
To run the function, you need to set the environment variables `GCP_PROJECT` and `GCP_BUCKET` to your own GCP project and bucket, and `BENCH_HOME` to the path of the BilliBench repository.

```bash
export GCP_PROJECT=<your-gcp-project>
export GCP_BUCKET=<your-gcp-bucket>
export BENCH_HOME=<path-to-billi-bench-repo>
```

### Install Dependencies

#### Setup GCP CLI
```bash
sudo apt-get update

# 1. Add the Cloud SDK distribution URI as a package source
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# 2. Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# 3. Update and install the Google Cloud SDK
sudo apt-get update
sudo apt-get install google-cloud-sdk

gcloud init
gcloud auth login
gcloud auth application-default login
```

#### Install necessary packages for payload generation

##### Func0_compile and Func1_ar: these functions prepare the payload from Linux kernel code and .o files compiled from the kernel source code. Install the following packages to compile the kernel source code:
```bash
sudo apt-get install flex bison libelf-dev libssl-dev
```

##### Func2_test: this function runs the test suite of the libvpx library. Install the following packages to compile the libvpx library test executables:
```bash
sudo apt-get update
sudo apt-get install nasm yasm doxygen curl coreutils libgtest-dev
```

##### Func3_videoEncode, Func4_videoDecode, and Func5_xc_enc: these functions encode and decode video files using the libvpx, daala, and alfalfa libraries. Install the following packages to compile the libvpx, daala, and alfalfa libraries:
```bash
sudo apt-get update
sudo apt-get install libpng-dev zlib1g-dev libtool libtool-bin libogg-dev
sudo apt install pkg-config yasm libxinerama-dev libxcursor-dev libglu1-mesa-dev libboost-all-dev libx264-dev libxrandr-dev libxi-dev libglew-dev libglfw3-dev libjpeg-dev

# change x264 to version 0.157.r2969
git clone https://github.com/ShiftMediaProject/x264.git
cd x264/
git checkout 0.157.r2969
./configure --prefix=/usr/local --enable-shared
make -j & sudo make install
sudo ldconfig
sudo cp /usr/local/lib/libx264.* /usr/lib/x86_64-linux-gnu/
```


#### Install Python Dependencies for BilliBench function execution
```bash
pip install -r requirement.txt
```

