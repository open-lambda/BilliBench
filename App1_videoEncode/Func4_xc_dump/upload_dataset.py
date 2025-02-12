#!/usr/bin/env python3
"""
Script to generate payload for Func4_xc_dump: 
download xc-dump tool from alfalfa repo, download vpxenc tool from libvpx repo, download video frames and transfer to y4m format, and upload it to GCP bucket    .
"""

import os
import shutil
import requests
from git import Repo
from google.cloud import storage

# Function Configuration
APP_NAME = "App1_videoEncode"
FUNC_NAME = "Func4_xc_dump"
ALFALFA_REPO_URL = "https://github.com/Tingjia980311/alfalfa.git"
LIBVPX_REPO_URL = "https://github.com/webmproject/libvpx.git"
DAALA_REPO_URL = "https://github.com/Tingjia980311/daala_tools.git"

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

# Directory paths
CLONE_PARENT_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)
ALFALFA_DIR = os.path.join(CLONE_PARENT_DIR, "alfalfa")
LIBVPX_DIR = os.path.join(CLONE_PARENT_DIR, "libvpx")
DAALA_DIR = os.path.join(CLONE_PARENT_DIR, "daala_tools")
FRAME_DIR = os.path.join(CLONE_PARENT_DIR, "frames")

PAYLOAD_DIRS = {
    "small": os.path.join(CLONE_PARENT_DIR, "payload_small"),
    "medium": os.path.join(CLONE_PARENT_DIR, "payload_medium"),
    "large": os.path.join(CLONE_PARENT_DIR, "payload_large"),
}

frame_sizes = {
    "small": 24,
    "medium": 60,
    "large": 240,
}

def clone_alfalfa_repo():
    """Clone alfalfa repository if it doesn't exist."""
    Repo.clone_from(ALFALFA_REPO_URL, ALFALFA_DIR)
    print(f"Alfalfa Repository cloned into {ALFALFA_DIR}")

    """Run necessary alfalfa build commands."""
    os.chdir(ALFALFA_DIR)
    # $ ./autogen.sh
    # $ ./configure
    # $ make -j$(nproc)
    # $ sudo make install
    os.system("./autogen.sh")
    os.system("./configure")
    os.system("make -j$(nproc) STATIC=1")
    
    print(f"Alfalfa Repository built into {ALFALFA_DIR}")

def clone_libvpx_repo():
    """Clone libvpx repository if it doesn't exist."""
    Repo.clone_from(LIBVPX_REPO_URL, LIBVPX_DIR)
    print(f"Libvpx Repository cloned into {LIBVPX_DIR}")

    """Run necessary libvpx build commands."""
    os.chdir(f"{LIBVPX_DIR}/build")
    os.system("../configure")
    os.system("make -j$(nproc)")
    print(f"Libvpx Repository built into {LIBVPX_DIR}")

def clone_daala_repo():
    """Clone Daala repository if it doesn't exist."""
    Repo.clone_from(DAALA_REPO_URL, DAALA_DIR)
    print(f"Daala Repository cloned into {DAALA_DIR}")

    """Run necessary build preparation commands."""
    os.chdir(DAALA_DIR)
    os.system("make -j$(nproc) STATIC=1")
    print(f"Daala Repository built into {DAALA_DIR}")

def download_video_frames():
    """Download video frames from the internet."""
    for i in range(500, 500 + frame_sizes['large']):
        frame_path = os.path.join(FRAME_DIR, f"{i:08d}.png")
        url = f"https://media.xiph.org/sintel/sintel-1k-png16/{i:08d}.png"
        response = requests.get(url)
        with open(frame_path, "wb") as f:
            f.write(response.content)

def setup_payload_directory():
    """Setup payload directory."""
    for size, payload_dir in PAYLOAD_DIRS.items():
        os.makedirs(payload_dir)
        os.chdir(payload_dir)

        # Copy frame files
        for i in range(frame_sizes[size]):
            frame_path = os.path.join(FRAME_DIR, f"{(500 + i):08d}.png")
            shutil.copy(frame_path, os.path.join(PAYLOAD_DIRS[size], f"{(500 + i):08d}.png"))   

        # Copy png2y4m executable
        shutil.copy(os.path.join(DAALA_DIR, "png2y4m"), os.path.join(payload_dir, "png2y4m"))

        # run png2y4m to transfer frames to y4m format
        os.system(f"./png2y4m %08d.png -o output.y4m")
        
        # rm all png files and png2y4m executable
        for file in os.listdir(payload_dir):
            if file.endswith(".png") or file == "png2y4m":
                os.remove(os.path.join(payload_dir, file))
        
        # Copy vpxenc executable
        shutil.copy(os.path.join(LIBVPX_DIR, "build", "vpxenc"), os.path.join(payload_dir, "vpxenc"))

        # Copy xc-dump executable
        shutil.copy(os.path.join(ALFALFA_DIR, "src", "frontend", "xc-dump"), os.path.join(payload_dir, "xc-dump"))


def upload_to_gcp(zip_file):
    """Upload zip file to gcp."""
    blob = bucket.blob(os.path.join(FUNC_NAME, os.path.basename(zip_file)))
    blob.upload_from_filename(zip_file)

def main():
    """Main execution function."""
    try:
        # remove all files in clone_parent_dir
        if os.path.exists(CLONE_PARENT_DIR):
            shutil.rmtree(CLONE_PARENT_DIR)
        os.makedirs(CLONE_PARENT_DIR)
        os.makedirs(FRAME_DIR)  
        
        clone_alfalfa_repo()
        clone_libvpx_repo()
        clone_daala_repo()
        download_video_frames()
        setup_payload_directory()   
        
        # zip each payload directory
        for size, payload_dir in PAYLOAD_DIRS.items():
            shutil.make_archive(payload_dir, 'zip', payload_dir)
            
            zip_file = os.path.join(CLONE_PARENT_DIR, f"payload_{size}.zip")
            print(zip_file)
            upload_to_gcp(zip_file)     

    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())   



