#!/usr/bin/env python3
"""
Script to generate payload for Func0_compile: clone Linux kernel, extract necessary header files.
"""

import os
import shutil
from git import Repo
from google.cloud import storage

# Function Configuration
APP_NAME = "App0_softwareCompile"
FUNC_NAME = "Func0_compile"
REPO_URL = "https://github.com/torvalds/linux.git"
TAG_NAME = "v6.13"

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

# Directory paths
CLONE_PARENT_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)
CLONE_DIR = os.path.join(CLONE_PARENT_DIR, "linux")

PAYLOAD_dirs = {
    "small": os.path.join(CLONE_PARENT_DIR, "payload_small"),
    "medium": os.path.join(CLONE_PARENT_DIR, "payload_medium"),
    "large": os.path.join(CLONE_PARENT_DIR, "payload_large"),
}

C_FILES = {
    "small": "drivers/firmware/efi/libstub/find.c",
    "medium": "drivers/hwmon/jc42.c",
    "large": "net/wireless/nl80211.c"
}


# Essential header directories for compilation
small_HEADER_DIRS = [
    "arch/x86/include/asm",
    "arch/x86/include/uapi/asm",
    "arch/x86/include/generated/asm",
    "arch/x86/include/generated/uapi/asm",
    "include/generated/uapi/linux",
    "include/generated",
    "include/linux",
    "include/vdso",
    "include/uapi/linux",
    "include/uapi/linux/byteorder",
    "include/asm-generic",
    "include/asm-generic/bitops",
    "include/uapi/asm-generic"
]

medium_HEADER_DIRS = [
    "arch/x86/include/asm",
    "arch/x86/include/uapi/asm",
    "arch/x86/include/generated/asm",
    "arch/x86/include/generated/uapi/asm",
    "arch/x86/include/asm/fpu",
    "arch/x86/include/asm/vdso",
    "arch/x86/include/asm/shared",
    "arch/x86/include/asm/xen",
    "include/generated/uapi/linux",
    "include/generated",
    "include/linux",
    "include/linux/atomic",
    "include/linux/sched",
    "include/linux/device",
    "include/linux/regulator",
    "include/linux/byteorder",
    "include/acpi",
    "include/acpi/platform",
    "include/vdso",
    "include/xen",
    "include/xen/interface/hvm",
    "include/uapi/linux",
    "include/uapi/linux/byteorder",
    "include/uapi/linux/hdlc",
    "include/uapi/regulator",
    "include/asm-generic",
    "include/asm-generic/bitops",
    "include/uapi/asm-generic"
]

large_HEADER_DIRS = [
    "arch/x86/include/asm",
    "arch/x86/include/uapi/asm",
    "arch/x86/include/generated/asm",
    "arch/x86/include/generated/uapi/asm",
    "arch/x86/include/asm/fpu",
    "arch/x86/include/asm/vdso",
    "arch/x86/include/asm/shared",
    "arch/x86/include/asm/xen",
    "include/generated/uapi/linux",
    "include/generated",
    "include/linux",
    "include/linux/atomic",
    "include/linux/sched",
    "include/linux/device",
    "include/linux/regulator",
    "include/linux/byteorder",
    "include/linux/lsm",
    "include/linux/unaligned",
    "include/linux/netfilter",
    "include/acpi",
    "include/acpi/platform",
    "include/vdso",
    "include/xen",
    "include/xen/interface/hvm",
    "include/uapi/linux",
    "include/uapi/linux/byteorder",
    "include/uapi/regulator",
    "include/uapi/linux/netfilter",
    "include/asm-generic",
    "include/asm-generic/bitops",
    "include/uapi/asm-generic",
    "include/net",
    "include/net/netns",
    "include/dt-bindings/leds",
    "include/trace",
    "net/wireless",
]

HEADER_DIRS = {
    "small": small_HEADER_DIRS,
    "medium": medium_HEADER_DIRS,
    "large": large_HEADER_DIRS
}

def clone_linux_repo():
    """Clone Linux repository if it doesn't exist."""
    os.makedirs(CLONE_PARENT_DIR)
    Repo.clone_from(REPO_URL, CLONE_DIR, depth=1, branch=TAG_NAME)
    print(f"Linux Repository (tag {TAG_NAME}) cloned into {CLONE_DIR}")

    """Run necessary kernel build preparation commands."""
    os.chdir(CLONE_DIR)
    os.system("make defconfig > /dev/null 2>&1 && make prepare > /dev/null 2>&1")

def collect_header_files(size):
    """Collect all necessary header files."""
    h_files = []
    for root, _, files in os.walk(CLONE_DIR):
        rel_root = os.path.relpath(root, CLONE_DIR)
        if rel_root in HEADER_DIRS[size]:
            h_files.extend(
                os.path.join(root, f) for f in files if f.endswith(".h")
            )
    return h_files

def setup_payload_directory():
    """Setup payload directory with necessary files."""
    for size, payload_dir in PAYLOAD_dirs.items():
        header_files = collect_header_files(size)
        os.makedirs(payload_dir)

        # Copy header files
        for h_file in header_files:
            rel_path = os.path.relpath(h_file, CLONE_DIR)
            dest_path = os.path.join(payload_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy(h_file, dest_path)

        # Copy c file
        source_file = C_FILES[size]
        os.makedirs(os.path.join(payload_dir, os.path.dirname(source_file)), exist_ok=True)
        shutil.copy(os.path.join(CLONE_DIR, source_file), 
                    os.path.join(payload_dir, source_file))

def generate_makefile():
    """
    Generate a Makefile for the payload directory.
    """
    # Define flags for different sizes
    define_flags = {
        "small": "-D__KERNEL__ -DKBUILD_BASENAME=\\\"find\\\" -DKBUILD_MODNAME=\\\"find\\\" -D__KBUILD_MODNAME=kmod_find",
        "medium": "-D__KERNEL__ -DMODULE -DKBUILD_BASENAME=\\\"jc42\\\" -DKBUILD_MODNAME=\\\"jc42\\\" -D__KBUILD_MODNAME=kmod_jc42 -DCC_USING_FENTRY",
        "large": "-D__KERNEL__ -DMODULE -DKBUILD_BASENAME=\\\"nl80211\\\" -DKBUILD_MODNAME=\\\"nl80211\\\" -D__KBUILD_MODNAME=kmod_nl80211 -DCC_USING_FENTRY",
    }

    machine_flags = {
        "small": "-mcmodel=small -m64 -mno-red-zone -mno-mmx -mno-sse",
        "medium": "-mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx -mno-80387 -mno-fp-ret-in-387 -mno-red-zone \
                   -m64 -mpreferred-stack-boundary=3 -mskip-rax-setup -mtune=generic -mcmodel=kernel \
                   -mindirect-branch=thunk-extern -mindirect-branch-register -mfunction-return=thunk-extern \
                   -mrecord-mcount -mfentry",
        "large": "-mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx -mno-80387 -mno-fp-ret-in-387 -mno-red-zone \
                  -m64 -mpreferred-stack-boundary=3 -mskip-rax-setup -mtune=generic -mcmodel=kernel \
                  -mindirect-branch=thunk-extern -mindirect-branch-register -mfunction-return=thunk-extern \
                  -mrecord-mcount -mfentry",
    }

    feature_flags = {
        "small": "-fPIC -fno-strict-aliasing -fshort-wchar -fno-asynchronous-unwind-tables \
                   -ffreestanding -fno-stack-protector",
        "medium": "-fcf-protection=none -falign-jumps=1 -falign-loops=1 -fpatchable-function-entry=16,16 -O2 \
                   -fstack-protector-strong -pg -falign-functions=16 -fshort-wchar -funsigned-char \
                   -fno-common -fno-PIE -fno-strict-aliasing -fno-jump-tables -fno-delete-null-pointer-checks \
                   -fno-omit-frame-pointer -fno-optimize-sibling-calls -fno-stack-clash-protection \
                   -fno-strict-overflow -fno-stack-check -fconserve-stack -fno-asynchronous-unwind-tables",
        "large": "-fcf-protection=none -falign-jumps=1 -falign-loops=1 -fpatchable-function-entry=16,16 -O2 \
                  -fstack-protector-strong -pg -falign-functions=16 -fshort-wchar -funsigned-char \
                  -fno-common -fno-PIE -fno-strict-aliasing -fno-jump-tables -fno-delete-null-pointer-checks \
                  -fno-omit-frame-pointer -fno-optimize-sibling-calls -fno-stack-clash-protection \
                  -fno-strict-overflow -fno-stack-check -fconserve-stack -fno-asynchronous-unwind-tables",
    }

    other_flag = "-c -Wno-attributes"

    include_flag = "-I arch/x86/include \
                   -I arch/x86/include/uapi \
                   -I arch/x86/include/generated \
                   -I arch/x86/include/generated/uapi \
                   -I include \
                   -I include/uapi \
                   -I include/generated/uapi \
                   -include include/linux/compiler-version.h \
                   -include include/linux/kconfig.h \
                   -include include/linux/compiler_types.h \
                   -include include/linux/hidden.h"

    # Write to Makefile
    for size, payload_dir in PAYLOAD_dirs.items():
        with open(os.path.join(payload_dir, "Makefile"), "w") as f:
            f.write("CC=gcc\n")
            f.write(f"CFLAGS={feature_flags[size]}\n")
            f.write(f"CFLAGS+={define_flags[size]}\n")
            f.write(f"CFLAGS+={machine_flags[size]}\n")
            f.write(f"CFLAGS+={other_flag}\n")
            f.write(f"INCLUDES={include_flag}\n")
            f.write(f"SRC={C_FILES[size]}\n")
            f.write("OUT=output.o\n")
            f.write("all:\n\t$(CC) $(CFLAGS) $(INCLUDES) -o $(OUT) $(SRC)\n")

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
        clone_linux_repo()
        setup_payload_directory()
        generate_makefile()
        # zip each payload directory
        for size, payload_dir in PAYLOAD_dirs.items():
            shutil.make_archive(payload_dir, "zip", payload_dir)

            zip_file = os.path.join(CLONE_PARENT_DIR, f"payload_{size}.zip")
            print(zip_file)
            upload_to_gcp(zip_file)

    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())