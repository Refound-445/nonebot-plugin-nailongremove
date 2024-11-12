import os
import json
num=0
def create_metadata_jsonl(root_folder, output_file):

    for subdir in os.listdir(root_folder):

        if not os.path.isdir(os.path.join(root_folder, subdir)):
            continue

        label = subdir
        output_name = os.path.join(root_folder, label, output_file)
        with open(output_name, 'w') as outfile:
            for file in os.listdir(os.path.join(root_folder, subdir)):

                if file.endswith('.jpg'):

                    metadata = {
                        "id": os.path.basename(file).split('.')[0],
                        "file_name": f'{file}',
                        "label": label
                    }

                    outfile.write(json.dumps(metadata) + "\n")
            print(f"Metadata file '{output_name}' has been created successfully.")



root_folder = 'nailongClassification'
output_file = 'metadata.jsonl'

create_metadata_jsonl(root_folder, output_file)

