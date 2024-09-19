import tempfile


def image_to_path(image) -> str:
    """
    Create a temporary file from an image and return its path.
    """
    with tempfile.NamedTemporaryFile(delete=False , suffix='.png') as tmp_file:
        image.save(tmp_file, format='PNG')
        tmp_file_path = tmp_file.name
    return tmp_file_path
