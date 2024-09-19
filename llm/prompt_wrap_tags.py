from typing import Literal


def prompt_wrap_tags(prompt:str , model_type:Literal["mistral", "llama"]):
    if model_type == "mistral":
        prompt = "[INST] " + prompt + "[/INST]"
    elif model_type == "llama":
        prompt = "<|begin_of_text|><|start_header_id|>user<|end_header_id|> " + prompt + " <|start_header_id|>assistant<|end_header_id|>"
    return prompt
