file_name = "woodetect-faq-1000.jsonl"
word_to_check = input("Enter the word to remove: ")

with open(file_name, 'r') as input_file, open("output_file.jsonl", 'w') as output_file:
    for line in input_file:
        if word_to_check not in line:
            output_file.write(line)
        else:
            print("Line removed: {}".format(line))

import os
os.rename("output_file.jsonl", file_name)

print("Lines containing '{}' have been removed from the file.".format(word_to_check))
