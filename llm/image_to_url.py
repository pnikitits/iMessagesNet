import base64



def local_image_to_data_url(image_path: str) -> str:
    """
    Convert a local image to a data URL.

    Parameters
    ----------
    image_path : str
        The path to the image.

    Returns
    -------
    str
        The data URL of the image.
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_string}"
