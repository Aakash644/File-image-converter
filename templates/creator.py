import os
import zipfile
import openai

def get_user_input():
    # Step 1: Take input from the user
    project_description = input("Enter the description of the project you want to build: ")
    return project_description

def generate_file_structure(description):
    # Step 2: Send the prompt to ChatGPT to generate the file structure
    openai.api_key = "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"  # Replace with your actual API key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate a file structure for a project described as: {description}. Limit the structure to a maximum of 20 files."}
        ]
    )

    file_structure = response['choices'][0]['message']['content']
    return file_structure

def generate_files(file_structure, description):
    # Step 3: Generate each of the files from the file structure
    openai.api_key = "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"  # Replace with your actual API key

    for file_info in file_structure:
        file_path = file_info['path']
        file_prompt = file_info['prompt']

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate the content for a file in the project described as: {description}. File path: {file_path}. {file_prompt}"}
            ]
        )

        file_content = response['choices'][0]['message']['content']
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(file_content)

def create_zip_archive():
    # Step 4: Create a zip archive of the generated files
    zip_file_name = "generated_project.zip"
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file != zip_file_name:
                    zipf.write(os.path.join(root, file))
    print(f"Project files have been zipped into {zip_file_name}")

def main():
    description = get_user_input()
    file_structure = generate_file_structure(description)
    if file_structure:
        generate_files(file_structure, description)
        create_zip_archive()

if __name__ == "__main__":
    main()
