#! /usr/bin/env python3
"""
Script to generate payload for Func2_test: clone libvpx, build libvpx, upload test binaries to GCP bucket.
"""

import os
import shutil
import subprocess
from git import Repo
from google.cloud import storage

# Function Configuration
APP_NAME = "App0_softwareCompile"
FUNC_NAME = "Func2_test"
REPO_URL = "https://github.com/webmproject/libvpx.git"
TAG_NAME = "v1.15.0"
REPO_URL_GTEST_PARALLEL = "https://github.com/google/gtest-parallel.git"


# raise error if Environment variables are not set
if os.getenv("GCP_PROJECT") is None or os.getenv("GCP_BUCKET") is None:
    raise ValueError("GCP_PROJECT and GCP_BUCKET must be set")

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

# Directory paths
CLONE_PARENT_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)
CLONE_DIR = os.path.join(CLONE_PARENT_DIR, "libvpx")
CLONE_GTEST_PARALLEL_DIR = os.path.join(CLONE_PARENT_DIR, "gtest-parallel")

PAYLOAD_DIRS = {
    "small": os.path.join(CLONE_PARENT_DIR, "payload_small"),
    "medium": os.path.join(CLONE_PARENT_DIR, "payload_medium"),
    "large": os.path.join(CLONE_PARENT_DIR, "payload_large"),
}

small_TEST_DATA = []

medium_TEST_DATA = [
    "vp90-2-03-size-226x226.webm",
    "vp90-2-08-tile_1x2_frame_parallel.webm",
    "vp90-2-08-tile_1x4_frame_parallel.webm",
    "vp90-2-08-tile_1x8_frame_parallel.webm",
    "vp90-2-08-tile_1x2.webm",
    "vp90-2-08-tile_1x4.webm",
    "vp90-2-08-tile_1x8.webm",
    "vp90-2-08-tile-4x1.webm",
    "vp90-2-08-tile-4x4.webm",
    "vp90-2-14-resize-fp-tiles-1-16.webm",
    "vp90-2-14-resize-fp-tiles-1-2-4-8-16.webm",
    "vp90-2-14-resize-fp-tiles-1-2.webm",
    "vp90-2-14-resize-fp-tiles-1-4.webm",
    "vp90-2-14-resize-fp-tiles-16-1.webm",
    "vp90-2-14-resize-fp-tiles-16-2.webm",
    "vp90-2-14-resize-fp-tiles-16-4.webm",
    "vp90-2-14-resize-fp-tiles-16-8-4-2-1.webm",
    "vp90-2-14-resize-fp-tiles-16-8.webm",
    "vp90-2-14-resize-fp-tiles-1-8.webm",
    "vp90-2-14-resize-fp-tiles-2-16.webm",
    "vp90-2-14-resize-fp-tiles-2-1.webm",
    "vp90-2-14-resize-fp-tiles-2-4.webm",
    "vp90-2-14-resize-fp-tiles-2-8.webm",
    "vp90-2-14-resize-fp-tiles-4-16.webm",
    "vp90-2-14-resize-fp-tiles-4-1.webm",
    "vp90-2-14-resize-fp-tiles-4-2.webm",
    "vp90-2-14-resize-fp-tiles-4-8.webm",
    "vp90-2-14-resize-fp-tiles-8-16.webm",
    "vp90-2-14-resize-fp-tiles-8-1.webm",
    "vp90-2-14-resize-fp-tiles-8-2.webm",
    "vp90-2-14-resize-fp-tiles-8-4.webm",
]

large_TEST_DATA = open("large_test_files.txt", "r").read().splitlines()

TEST_DATA = {
    "small": small_TEST_DATA,
    "medium": medium_TEST_DATA,
    "large": large_TEST_DATA,
}

def generate_libvpx_test_binary():
    """Clone libvpx repository if it doesn't exist."""
    Repo.clone_from(REPO_URL, CLONE_DIR, depth=1, branch=TAG_NAME)
    print(f"Libvpx Repository (tag {TAG_NAME}) cloned into {CLONE_DIR}")
    
    """Run necessary libvpx build preparation commands."""
    os.chdir(f"{CLONE_DIR}/build")
    os.system("../configure > /dev/null 2>&1")
    os.system("make -j$(nproc) > /dev/null 2>&1")
    os.system("make testdata -j$(nproc) > /dev/null 2>&1")
    print(f"Libvpx Repository (tag {TAG_NAME}) built into {CLONE_DIR}")

def generate_small_test_binary():
    """Generate small test binary."""
    # The sample Google Test code as a multi-line string.
    cpp_code  = r"// sample_test.cpp" + "\n"
    cpp_code += r"#include <gtest/gtest.h>" + "\n"
    cpp_code += r"// A simple test case" + "\n"
    cpp_code += r"TEST(SimpleTest, Equality) {" + "\n"
    cpp_code += r"    EXPECT_EQ(1, 1);" + "\n"
    cpp_code += r"}" + "\n"
    cpp_code += r"// Main entry point for Google Test." + "\n"  
    cpp_code += r"int main(int argc, char **argv) {" + "\n"
    cpp_code += r"    ::testing::InitGoogleTest(&argc, argv);" + "\n"
    cpp_code += r"    return RUN_ALL_TESTS();" + "\n"
    cpp_code += r"}" + "\n"

    # Write the cpp code to a file
    with open(f"{CLONE_PARENT_DIR}/sample_test.cpp", "w") as f:
        f.write(cpp_code)
    
    os.chdir(f"{CLONE_PARENT_DIR}")
    # Compile the test binary
    compile_cmd = [
        "g++", "-std=c++11", "sample_test.cpp", "-o", "sample_test",
        "-pthread", "-lgtest", "-lgtest_main"
    ]

    # Run the compilation command
    result = subprocess.run(compile_cmd, capture_output=True, text=True)

    # Check if compilation succeeded.
    if result.returncode == 0:
        print("Compilation succeeded!")
    else:
        print("Compilation failed!")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        raise Exception("Compilation failed!")

def setup_payload_directory():
    """Setup payload directory with a subset of test binaries."""
    for size, payload_dir in PAYLOAD_DIRS.items():
        os.makedirs(payload_dir, exist_ok=True)
        if size == "small":
            # copy the sample test binary to the payload directory 
            shutil.copy(f"{CLONE_PARENT_DIR}/sample_test", f"{payload_dir}/{size}_test_binary")
        else:
            # copy the libvpx test binary to the payload directory
            shutil.copy(f"{CLONE_DIR}/build/test_libvpx", f"{payload_dir}/{size}_test_binary")

        # copy the test data to the payload directory
        for test_data in TEST_DATA[size]:
            shutil.copy(f"{CLONE_DIR}/build/{test_data}", f"{payload_dir}/{test_data}")


def upload_to_gcp(test_binary_file):
    """Upload zip file to gcp."""
    blob = bucket.blob(os.path.join(FUNC_NAME, os.path.basename(test_binary_file)))
    blob.upload_from_filename(test_binary_file)

def upload_gtest_parallel():
    """Clone gtest parallel repository."""
    Repo.clone_from(REPO_URL_GTEST_PARALLEL, CLONE_GTEST_PARALLEL_DIR)
    print(f"Gtest Parallel Repository cloned into {CLONE_GTEST_PARALLEL_DIR}")
    # upload the gtest-parallel and gtest_parallel.py to gcp
    upload_to_gcp(f"{CLONE_GTEST_PARALLEL_DIR}/gtest-parallel")
    upload_to_gcp(f"{CLONE_GTEST_PARALLEL_DIR}/gtest_parallel.py")

def main():
    """Main function."""
    try:
        # upload the test binary and test data to gcp
        if os.path.exists(CLONE_PARENT_DIR):
            shutil.rmtree(CLONE_PARENT_DIR)
        os.makedirs(CLONE_PARENT_DIR)

        generate_libvpx_test_binary()
        generate_small_test_binary()
        setup_payload_directory()

        # upload each test binary to gcp
        for size, payload_dir in PAYLOAD_DIRS.items():
            shutil.make_archive(payload_dir, "zip", payload_dir)

            zip_file = os.path.join(CLONE_PARENT_DIR, f"payload_{size}.zip")
            print(zip_file)
            upload_to_gcp(zip_file)

        # upload the gtest-parallel tool to gcp
        upload_gtest_parallel()

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    main()