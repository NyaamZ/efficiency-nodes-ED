import os
import json
import re
from PIL import Image
from PIL.PngImagePlugin import PngInfo

current_dir = os.path.dirname(__file__)

def search(dirname):
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        if os.path.isdir(full_filename):
            search(full_filename)
        else:
            ext = os.path.splitext(full_filename)[-1]
            if ext == '.png': 
                get_prompt(full_filename)

def get_prompt(image_path):
    compress_level = 4
    
    img = Image.open(image_path)
    info = img.info

    if isinstance(info, dict) and 'prompt' in info and 'workflow' in info:
        prompt = json.loads(info['prompt'])
        workflow = json.loads(info['workflow'])
        
        for node in prompt:            
            for v in prompt[node]['inputs']:            
                if isinstance(prompt[node]['inputs'][v], dict):
                    if "content" in prompt[node]['inputs'][v] and "image" in prompt[node]['inputs'][v]:
                        prompt[node]['inputs'][v] = prompt[node]['inputs'][v]["content"]                        
                        
        for i, node in enumerate(workflow["nodes"]):
            if "widgets_values" in node:
                for j, value in enumerate(node["widgets_values"]):
                    if isinstance(value, dict) and 'content' in value:
                        workflow["nodes"][i]["widgets_values"][j] = value['content']                      
         
        metadata = PngInfo()
        if prompt is not None:
            metadata.add_text("prompt", json.dumps(prompt))
        if workflow is not None:
            metadata.add_text("workflow", json.dumps(workflow))

        img.save(image_path, pnginfo=metadata, compress_level=compress_level)
        print (f">> {image_path} workflow has been modified")
   
    return

print ("\n\n\n")
search(current_dir)
print ("\n\n\nmodify workflow is ENDED!")