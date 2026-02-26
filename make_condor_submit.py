import json

# Read your JSON bundle file
with open("Big_2024_MC_file.json") as f:
    cache = json.load(f)

submit_filename = "submit.jdl"

with open(submit_filename, "w") as sub:

    # Basic condor settings
    sub.write("executable = run_job.sh\n")
    sub.write("universe   = vanilla\n")
    sub.write('+JobFlavour = "nextweek"\n')
    sub.write("stream_output = True\n")
    sub.write("stream_error  = True\n\n")

    sub.write("should_transfer_files = YES\n")
    sub.write("WhenToTransferOutput  = ON_EXIT\n")
    sub.write("notification = never\n")
    sub.write("getenv     = True\n\n")

    sub.write("Transfer_Input_Files = .\n")
    sub.write("request_cpus = 1\n")
    sub.write("request_memory = 8 GB\n")
    sub.write("request_disk = 50 GB\n\n")

    sub.write("output = logs/$(Cluster)_$(Process).out\n")
    sub.write("error  = logs/$(Cluster)_$(Process).err\n")
    sub.write("log    = logs/$(Cluster).log\n\n")

    # Loop over all processes and parts
    for process, parts in cache.items():
        for part in parts.keys():
            sub.write(f"arguments = {process} {part}\n")
            sub.write("queue\n\n")

print(f"Condor submit file '{submit_filename}' created successfully.")

