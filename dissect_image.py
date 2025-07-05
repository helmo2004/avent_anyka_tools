#!env python3
import os
import re
import shutil
import sys
import argparse

type PartitionTableEntry = tuple[str, int, int, bytes]


def parse_args():
    parser = argparse.ArgumentParser(description="Dissect a Avent Anyka binary image to its partions. \n Can be used for SCD92x(Parent only) SCD88x SCD89x")
    parser.add_argument("--force", "-f", action="store_true", help="Force delete the output folder if it exists and contains data")
    parser.add_argument("inputfile", help="Path to the input file")
    parser.add_argument("output_folder", help="Path to the output directory")
    return parser.parse_args()


def prepare_output_folder(args):
    if os.path.exists(args.output_folder):
        if os.listdir(args.output_folder):
            if args.force:
                # Remove the folder and its contents, then recreate it
                shutil.rmtree(args.output_folder)
                os.makedirs(args.output_folder)
            else:
                # Folder exists and is not empty, but --force was not set
                print(f"Error: Output folder '{args.utput_folder}' is not empty. Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)
        else:
            # Folder exists but is empty
            pass
    else:
        # Folder does not exist, create it
        os.makedirs(args.output_folder)


def write_bin_to_file(data: bytes, filename: str):
    with open(filename, "wb") as f:
        f.write(data)


def write_to_file(data: str, filename: str):
    with open(filename, "w") as f:
        f.write(data)


def get_partition_table(data:bytes) -> list[PartitionTableEntry]:
    # correct partition table contains KERNEL2
    match=re.search(pattern=b"mtdparts=spi0.0:(.+?KERNEL2.+?)\x00", string=data)
    if match:
        entries = []
        for entry in match.group(1).split(b","):
            line_match = re.match(rb"(.*)K@0x(.*)\((.*)\)", entry)
            if not line_match:
                raise Exception("cannot match line: " + entry)
            name = line_match.group(3).decode("utf-8")
            offset = int(line_match.group(2), 16)
            size = int(line_match.group(1)) * 1024
            partition_data = data[offset:offset + size]
            entries.append((name, offset, size, partition_data))
        return entries
    else:
        raise Exception("cannot find table")

  
def dump_uboot_env(partition_table:list[PartitionTableEntry], args):
    for name, offset, size, partition_data in partition_table:
        if name.startswith("ENV"):
            env_list_bytes = partition_data[4:].rstrip(b"\0").split(b"\0")
            env_list_utf8 = [line.decode("utf-8") for line in env_list_bytes]
            env = "\n".join(env_list_utf8)
            write_to_file(env, f"{args.output_folder}/{name}.txt")
            

def dump_partition_table(table:list[PartitionTableEntry], args):
    lines = []
    
    lines.append("Partition    Offset   Size ")
    lines.append("---------------------------")
    for name, offset, size, _ in table:
        lines.append(f"{name:10s}   {offset:06X}   {size//1024:4d}K")
    write_to_file("\n".join(lines), f"{args.output_folder}/partition_table.txt")


def main():
    args = parse_args()

    prepare_output_folder(args)

    with open(args.inputfile, "rb") as f:
        data = f.read()

    partition_table = get_partition_table(data)
    dump_partition_table(partition_table, args)
    for partition_name, _, _, partition_data in partition_table:
        write_bin_to_file(partition_data, f"{args.output_folder}/{partition_name}.bin")
   
    dump_uboot_env(partition_table, args)
           

if __name__ == "__main__":
    main()
