
import subprocess
import os



def run_minicpvm(model_m:str,
                 model_mmproj:str,
                 executable_path:str,
                 prompt:str,
                 image_url:str,
                 verbose:bool=False) -> str:
    """
    Run the vision model with MPS acceleration.

    Parameters
    ----------
    model_m : str
        The path to the model file.
    model_mmproj : str
        The path to the multimodal projector file.
    executable_path : str
        The path to the executable: llama-minicpmv-cli.
    prompt : str
        The prompt to start generation with.
    image_url : str
        The url of the image to run the model on.

    Returns
    -------
    str
        The generated text from the vision model.
    """
    
    print("Running with wrapper (MPS)") if verbose else None

    if not os.path.isfile(executable_path):
        raise FileNotFoundError(f"The executable '{executable_path}' was not found.")
    
    # check if the model files exist
    if not os.path.isfile(model_m):
        raise FileNotFoundError(f"The model file '{model_m}' was not found.")
    
    if not os.path.isfile(model_mmproj):
        raise FileNotFoundError(f"The model file '{model_mmproj}' was not found.")

    run_command = [executable_path,
                   "-m", model_m,
                   "--mmproj", model_mmproj,
                   "--image", image_url,
                   "--temp", "0.1",
                   "-p", prompt]
    print(run_command) if verbose else None

    result = subprocess.run(run_command , capture_output=True , text=True)
    return result.stdout