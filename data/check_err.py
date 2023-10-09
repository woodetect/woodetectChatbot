import json

def check_jsonl_file(file_path):
    try:
        with open(file_path, 'r') as file:
            line_number = 1
            for line in file:
                try:
                    json_object = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Error on line {line_number}: {e}")
                    print("Line content causing the error:", line)
                    break

                # If you need to do additional processing with the valid JSON object, you can do it here.

                line_number += 1

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")


# Example usage:
jsonl_file_path = 'woodetect-faq.jsonl'
check_jsonl_file(jsonl_file_path)
print("fine")
