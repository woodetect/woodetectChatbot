# code to convert every column "text" of a jsonl to txt import json

# specify the path of the input jsonl file
input_file = "/path/to/input.jsonl"

# specify the path of the output txt file
output_file = "/path/to/output.txt"

import json

input_file = "woodetect-faq-1000.jsonl"
output_file = "woodetect-faq.txt"

# open the input and output files
with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
    # loop through each line in the input file
    for line in f_in:
        # parse the json object from the line
        obj = json.loads(line)
        # write the "text" column to the output file
        f_out.write(obj["text"] + "\n")
