def remove_newlines(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            content = f.read()

        # Remove newline characters from the content
        content_without_newlines = content.replace('\n', '')

        # Write the modified content to the output file
        with open(output_file, 'w') as f:
            f.write(content_without_newlines)

        print(f"Newlines removed from '{input_file}'. Output saved to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")


def add_newline_after_closing_brace(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            content = f.read()

        # Add a newline after every occurrence of the closing curly brace `}`
        content_with_newlines = content.replace('}', '}\n')

        # Write the modified content to the output file
        with open(output_file, 'w') as f:
            f.write(content_with_newlines)

        print(f"Newline added after every '}}' in '{input_file}'. Output saved to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")


# Example usage:
input_file_path = 'woodetect-qa.jsonl'
output_file_path_remove_newlines = 'woodetect-faq.json'
output_file_path_add_newlines = 'woodetect-faq.json'

remove_newlines(input_file_path, output_file_path_remove_newlines)
add_newline_after_closing_brace(output_file_path_remove_newlines, output_file_path_add_newlines)
