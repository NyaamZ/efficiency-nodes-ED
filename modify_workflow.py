import os
import json
import re
import copy
from PIL import Image
from PIL import ImageFile
from PIL.PngImagePlugin import PngInfo

ImageFile.LOAD_TRUNCATED_IMAGES = True 
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

SimpleText_prototype = {"id": 1302, "type": "Simple Text \ud83d\udcacED", "pos": [520, 860], "size": [580, 370], "flags": {"pinned": True}, "order": 9, "mode": 0, "inputs": [], "outputs": [{"name": "STRING", "type": "STRING", "slot_index": 0, "links": [2440]}], "title": "Simple Text (Negative)", "properties": {"cnr_id": "efficiency-nodes-ED", "ver": "496cb53406df62c14c425d6b814afc99f5c8a31c", "Node name for S&R": "Simple Text \ud83d\udcacED"}, "widgets_values": ["bad quality, worst quality, worst detail,sketch,censor, skinny, skindentation, copyright name, watermark, copyright notice, sign, artist name, (hair intakes:1.4), (hair behind ear:1.4),"], "color": "#323", "bgcolor": "#535", "shape": 2}


def get_prompt(image_path):
    is_modified = False
    compress_level = 4
    
    img = Image.open(image_path)
    info = img.info
    
    print (f"> open {image_path} file")

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
                        is_modified = True
            
            if "type" in node:                
                if node["type"] == "Efficient Loader 💬ED":
                    if "Synchronize widget with image size" in node["properties"]:
                        del workflow["nodes"][i]["properties"]['Synchronize widget with image size']
                        is_modified = True
                    if len(node["widgets_values"]) == 14:
                        del workflow["nodes"][i]["widgets_values"][10:12]
                        is_modified = True

                elif node["type"] == "FaceDetailer 💬ED":
                    if len(node["widgets_values"]) == 32:
                        del workflow["nodes"][i]["widgets_values"][29]
                        is_modified = True
                        
                elif node["type"] == "PrimitiveNode" and node["outputs"][0]["name"] == "STRING":
                    
                    for link in workflow["links"]:
                        link_target_id = str(link[3])
                        if link_target_id in prompt and prompt[link_target_id]["class_type"] == "Efficient Loader 💬ED":
                            simple_text = copy.deepcopy(SimpleText_prototype)
                            simple_text["id"] = node["id"]
                            simple_text["pos"] = node["pos"]
                            simple_text["size"] = node["size"]
                            simple_text["flags"] = node["flags"]
                            simple_text["outputs"][0]["links"] = node["outputs"][0]["links"]
                            simple_text["widgets_values"] = node["widgets_values"]
                            if "color" in node:
                                simple_text["color"] = node["color"]
                            if "bgcolor" in node:
                                simple_text["bgcolor"] = node["bgcolor"]

                            workflow["nodes"][i] = simple_text
                            print(f"PrimitiveNode(id:{node['id']}) has been replaced with Simple Text (Efficient Loader 💬ED(id:{link_target_id}))\n")
                            is_modified = True
                            break

         
        metadata = PngInfo()
        if prompt is not None:
            metadata.add_text("prompt", json.dumps(prompt))
        if workflow is not None:
            metadata.add_text("workflow", json.dumps(workflow))

        img.save(image_path, pnginfo=metadata, compress_level=compress_level)
        if is_modified:
            print (f">> {image_path} workflow has been modified")
   
    return

print ("\n\n\n")
search(current_dir)
print ("\n\n\nThe workflows have been successfully modified!!")