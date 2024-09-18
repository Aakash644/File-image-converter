def compress_image(input_path, output_path):
    try:
        # Compress the image using TinyPNG API
        source = tinify.from_file(input_path)
        source.to_file(output_path)

        print("Image compressed successfully.")
    except Exception as e:
        print(f"Error compressing image: {e}")
