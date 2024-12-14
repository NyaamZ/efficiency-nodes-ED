# Efficiency Nodes ExtendeD - Expansion of Efficiency Nodes for ComfyUI. Significant UX improvements.
# by NyaamZ - 2023 - 2024
# https://github.com/LucianoCirino/efficiency-nodes-ED

#from torch import Tensor
#from PIL import Image, ImageOps, ImageDraw, ImageFont
#from PIL.PngImagePlugin import PngInfo
#import numpy as np
import torch

#import ast
from pathlib import Path #for embedding stacker
#from importlib import import_module
import os
import sys
#import copy
#import subprocess
#import json
#import psutil

# Get the absolute path of various directories
my_dir = os.path.dirname(os.path.abspath(__file__))
custom_nodes_dir = os.path.abspath(os.path.join(my_dir, '..'))
efficiency_nodes_dir = os.path.abspath(os.path.join(custom_nodes_dir, 'efficiency-nodes-comfyui'))
comfy_dir = os.path.abspath(os.path.join(my_dir, '..', '..'))

# Append comfy_dir to sys.path & import files
sys.path.append(comfy_dir)
from nodes import CLIPSetLastLayer, CLIPTextEncode, PreviewImage, LoadImage, SaveImage, MAX_RESOLUTION, InpaintModelConditioning, RepeatLatentBatch, ImageBatch, ImageScale
from nodes import NODE_CLASS_MAPPINGS as nodes_NODE_CLASS_MAPPINGS
#import nodes
from comfy_extras.nodes_upscale_model import UpscaleModelLoader, ImageUpscaleWithModel
from server import PromptServer

#from comfy_extras.nodes_clip_sdxl import CLIPTextEncodeSDXL, CLIPTextEncodeSDXLRefiner
#import comfy.sample
#import comfy.samplers
import comfy.sd
import comfy.utils

#import comfy.latent_formats

sys.path.remove(comfy_dir)

sys.path.append(efficiency_nodes_dir)
from tsc_utils import *
efficiency_nodes_py_dir = os.path.abspath(os.path.join(efficiency_nodes_dir, 'py'))
sys.path.append(efficiency_nodes_py_dir)
from bnk_adv_encode import AdvancedCLIPTextEncode
sys.path.remove(efficiency_nodes_py_dir)
sys.path.remove(efficiency_nodes_dir)

# Append custom_nodes_dir to sys.path
sys.path.append(custom_nodes_dir)


#################################################################
#################################################################
#                                                          ED                                                               #
#################################################################
#################################################################

SCHEDULERS = comfy.samplers.KSampler.SCHEDULERS + ["AYS SD1", "AYS SDXL", "AYS SVD"]

############## ED rgthree Context
_all_ed_context_input_output_data = {
  "base_ctx": ("base_ctx", "RGTHREE_CONTEXT", "CONTEXT"),
  "model": ("model", "MODEL", "MODEL"),
  #"refiner_model": ("refiner_model", "MODEL", "REFINER_MODEL"),
  "clip": ("clip", "CLIP", "CLIP"),
  #"refiner_clip": ("refiner_clip", "CLIP", "REFINER_CLIP"),
  "vae": ("vae", "VAE", "VAE"),
  "positive": ("positive", "CONDITIONING", "POSITIVE"),
  #"refiner_positive": ("positive", "CONDITIONING", "REFINER_POSITIVE"),
  "negative": ("negative", "CONDITIONING", "NEGATIVE"),
  #"refiner_negative": ("negative", "CONDITIONING", "REFINER_NEGATIVE"),
  "latent": ("latent", "LATENT", "LATENT"),
  "images": ("images", "IMAGE", "IMAGE"),
  "seed": ("seed", "INT", "SEED"),
  "steps": ("steps", "INT", "STEPS"),
  "step_refiner": ("step_refiner", "INT", "STEP_REFINER"),
  "cfg": ("cfg", "FLOAT", "CFG"),
  "ckpt_name": ("ckpt_name", folder_paths.get_filename_list("checkpoints"), "CKPT_NAME"),
  "sampler": ("sampler", comfy.samplers.KSampler.SAMPLERS, "SAMPLER"),
  "scheduler": ("scheduler", SCHEDULERS, "SCHEDULER"),
  "clip_width": ("clip_width", "INT", "CLIP_WIDTH"),
  "clip_height": ("clip_height", "INT", "CLIP_HEIGHT"),
  "text_pos_g": ("text_pos_g", "STRING", "TEXT_POS_G"),
  "text_pos_l": ("text_pos_l", "STRING", "TEXT_POS_L"),
  "text_neg_g": ("text_neg_g", "STRING", "TEXT_NEG_G"),
  "text_neg_l": ("text_neg_l", "STRING", "TEXT_NEG_L"),
  "mask": ("mask", "MASK", "MASK"),
  "control_net": ("control_net", "CONTROL_NET", "CONTROL_NET"),
  "lora_stack": ("lora_stack", "LORA_STACK", "LORA_STACK"),
}

def new_context_ed(base_ctx, **kwargs):
    """Creates a new context from the provided data, with an optional base ctx to start."""
    context = base_ctx if base_ctx is not None else None
    new_ctx = {}
    for key in _all_ed_context_input_output_data:
        if key == "base_ctx":
            continue
        v = kwargs[key] if key in kwargs else None
        new_ctx[key] = v if v is not None else context[key] if context is not None and key in context else None
    return new_ctx

def context_2_tuple_ed(ctx, inputs_list=None):
    """Returns a tuple for returning in the order of the inputs list."""
    if inputs_list is None:
        inputs_list = _all_ed_context_input_output_data.keys()
    tup_list = [ctx,]
    for key in inputs_list:
        if key == "base_ctx":
            continue
        tup_list.append(ctx[key] if ctx is not None and key in ctx else None)
    return tuple(tup_list)

# def get_widget_value(self, extra_pnginfo, prompt, node_name, widget_name):
    # workflow = extra_pnginfo["workflow"] if "workflow" in extra_pnginfo else { "nodes": [] }
    # node_id = None
    # for node in workflow["nodes"]:
        # name = node["type"]
        # if "properties" in node:
            # if "Node name for S&R" in node["properties"]:
                # name = node["properties"]["Node name for S&R"]
        # if name == node_name:
            # node_id = node["id"]
            # break
        # if "title" in node:
            # name = node["title"]
        # if name == node_name:
            # node_id = node["id"]
            # break
    # if node_id is not None:
        # values = prompt[str(node_id)]
        # if "inputs" in values:
            # if widget_name in values["inputs"]:
                # value = values["inputs"][widget_name]
                # if isinstance(value, list):
                    # raise ValueError("Converted widgets are not supported via named reference, use the inputs instead.")
                # return value
        # raise NameError(f"Widget not found: {node_name}.{widget_name}")
    # raise NameError(f"Node not found: {node_name}.{widget_name}")
        
#======= CASHE
cashe_ed = {
    "ultra_bbox_detector": [],
    "ultra_segm_detector": [],
    "sam_model": [],
    "ultimate_sd_upscaler": []
}

def cashload_ed(cashe_type, model_name):
    global cashe_ed
    for entry in cashe_ed[cashe_type]:
        if entry[0] == model_name:
            print(f"\033[36mED node use {cashe_type} cashe: {entry[0]}\033[0m")
            return entry[1]
    return None
    
def cashsave_ed(cashe_type, model_name, model, max_cashe):
    global cashe_ed
    if len(cashe_ed[cashe_type])>= max_cashe:
        cashe_ed[cashe_type].pop(0)
    cashe_ed[cashe_type].append([model_name, model])
    print(f"\033[36mED node save {cashe_type} cashe: {model_name}\033[0m")
    return

############################################################################################################
def populate_items(names, type):
    idx = None
    item_name = None
    for idx, item_name in enumerate(names):
        
        file_name = os.path.splitext(item_name)[0]
        file_path = folder_paths.get_full_path(type, item_name)

        if file_path is None:
            names[idx] = {
                "content": item_name,
                "image": None,
            }
            continue

        file_path_no_ext = os.path.splitext(file_path)[0]

        for ext in ["png", "jpg", "jpeg", "preview.png", "preview.jpeg"]:
            has_image = os.path.isfile(file_path_no_ext + "." + ext)
            if has_image:
                item_image = f"{file_name}.{ext}"
                break

        names[idx] = {
            "content": item_name,
            "image": f"{type}/{item_image}" if has_image else None,
        }

#####################################################################################

# LoRA Stacker ED
class LoRA_Stacker_ED:
    modes = ["simple", "advanced"]
    MAX_LORA_COUNT = 9

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "input_mode": (cls.modes,),
                "lora_count": ("INT", {"default": 3, "min": 0, "max": cls.MAX_LORA_COUNT, "step": 1}),
            }
        }        
        inputs["required"][f"lora_name_{1}"] = (["None"] + folder_paths.get_filename_list("loras"),)
        populate_items(inputs["required"][f"lora_name_{1}"][0], "loras")
        loras = inputs["required"][f"lora_name_{1}"]
        for i in range(1, cls.MAX_LORA_COUNT):
            inputs["required"][f"lora_name_{i}"] = loras
            inputs["required"][f"lora_wt_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"model_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"clip_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})        

        inputs["optional"] = {
            "lora_stack": ("LORA_STACK",)
        }
        return inputs

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("LORA_STACK",)
    FUNCTION = "lora_stacker_ed"
    CATEGORY = "Efficiency Nodes/Stackers"

    def lora_stacker_ed(self, input_mode, lora_count, lora_stack=None, **kwargs):
        if lora_count > 0:
            for i in range(1, self.MAX_LORA_COUNT):
                kwargs[f"lora_name_{i}"] = kwargs[f"lora_name_{i}"]["content"]
            # Extract values from kwargs
            loras = [kwargs.get(f"lora_name_{i}") for i in range(1, lora_count + 1)]

            # Create a list of tuples using provided parameters, exclude tuples with lora_name as "None"
            if input_mode == "simple":
                weights = [kwargs.get(f"lora_wt_{i}") for i in range(1, lora_count + 1)]
                loras = [(lora_name, lora_weight, lora_weight) for lora_name, lora_weight in zip(loras, weights) if lora_name != "None"]
            else:
                model_strs = [kwargs.get(f"model_str_{i}") for i in range(1, lora_count + 1)]
                clip_strs = [kwargs.get(f"clip_str_{i}") for i in range(1, lora_count + 1)]
                loras = [(lora_name, model_str, clip_str) for lora_name, model_str, clip_str in zip(loras, model_strs, clip_strs) if lora_name != "None"]
        else:
            loras = []
        
        # If lora_stack is not None, extend the loras list with lora_stack
        if lora_stack is not None:
            loras.extend([l for l in lora_stack if l[0] != "None"])
        #print(f"\033[36mloras:{(loras,)}\033[0m") 
        return (loras,)

##########################################################################################################

# Embedding Stacker ED
class Embedding_Stacker_ED:

    MAX_EMBEDDING_COUNT = 9

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "positive_embeddings_count": ("INT", {"default": 0, "min": 0, "max": cls.MAX_EMBEDDING_COUNT, "step": 1}),
                "negative_embeddings_count": ("INT", {"default": 3, "min": 0, "max": cls.MAX_EMBEDDING_COUNT, "step": 1}),
            }
        }        
        inputs["required"][f"positive_embedding_{1}"] = (["None"] + folder_paths.get_filename_list("embeddings"),)
        populate_items(inputs["required"][f"positive_embedding_{1}"][0], "embeddings")
        embeddings = inputs["required"][f"positive_embedding_{1}"]
        for i in range(1, cls.MAX_EMBEDDING_COUNT):
            inputs["required"][f"positive_embedding_{i}"] = embeddings
            inputs["required"][f"positive_emphasis_{i}"] = ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.05})
        for i in range(1, cls.MAX_EMBEDDING_COUNT):
            inputs["required"][f"negative_embedding_{i}"] = embeddings
            inputs["required"][f"negative_emphasis_{i}"] = ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.05})

        inputs["optional"] = {
            "lora_stack": ("LORA_STACK",)
        }
        return inputs

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("LORA_STACK",)
    FUNCTION = "embedding_stacker"
    CATEGORY = "Efficiency Nodes/Stackers"

    def embedding_stacker(self, positive_embeddings_count, negative_embeddings_count, lora_stack=None, **kwargs):
        # POSITIVE EMBEDDING
        if positive_embeddings_count > 0:
            for i in range(1, Embedding_Stacker_ED.MAX_EMBEDDING_COUNT):
                kwargs[f"positive_embedding_{i}"] = kwargs[f"positive_embedding_{i}"]["content"]

            # Extract values from kwargs
            pos_embs = [kwargs.get(f"positive_embedding_{i}") for i in range(1, positive_embeddings_count + 1)]
            # Create a list of tuples using provided parameters, exclude tuples with lora_name as "None"
            pos_emps = [kwargs.get(f"positive_emphasis_{i}") for i in range(1, positive_embeddings_count + 1)]
            pos_embs = [("POS_EMBEDDING", pos_emb, round(pos_emp, 2)) for pos_emb, pos_emp in zip(pos_embs, pos_emps) if pos_emb != "None"]
        else:
            pos_embs = []
        
        # NEGTIVE EMBEDDING
        if negative_embeddings_count > 0:
            for i in range(1, Embedding_Stacker_ED.MAX_EMBEDDING_COUNT):
                kwargs[f"negative_embedding_{i}"] = kwargs[f"negative_embedding_{i}"]["content"]
            # Extract values from kwargs
            neg_embs = [kwargs.get(f"negative_embedding_{i}") for i in range(1, negative_embeddings_count + 1)]
            # Create a list of tuples using provided parameters, exclude tuples with lora_name as "None"
            neg_emps = [kwargs.get(f"negative_emphasis_{i}") for i in range(1, negative_embeddings_count + 1)]
            neg_embs = [("NEG_EMBEDDING", neg_emb, round(neg_emp, 2)) for neg_emb, neg_emp in zip(neg_embs, neg_emps) if neg_emb != "None"]
        else:
            neg_embs = []
        
        loras = pos_embs + neg_embs        
        # If lora_stack is not None, extend the loras list with lora_stack
        if lora_stack is not None:
            loras.extend([l for l in lora_stack if l[0] != "None"])
        #print(f"\033[36mlorasEmbedding:{(loras,)}\033[0m") 
        return (loras,)

    def embedding_process(lora_stack, positive, negative, positive_refiner, negative_refiner):
        if lora_stack is None:
            return (lora_stack, positive, negative, positive_refiner, negative_refiner)
    
        new_lora_stack = []
        pos = positive
        neg = negative
        pos_refiner = positive_refiner
        neg_refiner = negative_refiner
    
        for entry in lora_stack:
            if entry[0] == "POS_EMBEDDING":
                emb = "embedding:" + Path(entry[1]).stem        
                if entry[2] != 1:
                    emb = f"({emb}:{entry[2]})"
                pos = f"{positive.rstrip(' ,')}, {emb},"
                positive = pos
                if positive_refiner is not None:
                    pos_refiner = f"{positive_refiner.rstrip(' ,')}, {emb},"
                    positive_refiner = pos_refiner
            elif entry[0] == "NEG_EMBEDDING":
                emb = "embedding:" + Path(entry[1]).stem        
                if entry[2] != 1:
                    emb = f"({emb}:{entry[2]})"
                neg = f"{negative.rstrip(' ,')}, {emb},"
                negative = neg
                if negative_refiner is not None:
                    neg_refiner = f"{negative_refiner.rstrip(' ,')}, {emb},"
                    negative_refiner = neg_refiner
            else:
                new_lora_stack.append(entry)
                
        if len(new_lora_stack) == 0:
            new_lora_stack = None
        #print(f"\033[36mpos:{pos}\033[0m")
        #print(f"\033[36mneg:{neg}\033[0m")
        return (new_lora_stack, pos, neg, pos_refiner, neg_refiner)

####################################################################################

# Apply LoRA Stack ED
class Apply_LoRA_Stack_ED:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": { },
                    "optional": {
                                "context": ("RGTHREE_CONTEXT",),
                                "model": ("MODEL",),
                                "clip": ("CLIP",),
                                "vae": ("VAE",),
                                "positive": ("CONDITIONING",),
                                "negative": ("CONDITIONING",),
                                "latent": ("LATENT",),
                                "images": ("IMAGE",),
                                "seed": ("INT", {"forceInput": True}),
                        },
                    }

    RETURN_TYPES = ("RGTHREE_CONTEXT", "MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING", "LATENT", "IMAGE", "INT",)
    RETURN_NAMES = ("CONTEXT", "MODEL", "CLIP", "VAE", "POSITIVE" ,"NEGATIVE", "LATENT", "IMAGE", "SEED",)
    FUNCTION = "apply_lora_ed"
    CATEGORY = "Efficiency Nodes/Stackers"
    
    def apply_load_lora(lora_params, ckpt, clip, show_node=True):
        
        def recursive_load_lora(lora_params, ckpt, clip, folder_paths, lora_count):
            if len(lora_params) == 0:
                return ckpt, clip

            lora_name, strength_model, strength_clip = lora_params[0]
            
            if os.path.isabs(lora_name):
                lora_path = lora_name
            else:
                lora_path = folder_paths.get_full_path("loras", lora_name)
            
            lora_count += 1
            lora_model_info = f"{os.path.splitext(os.path.basename(lora_name))[0]}({round(strength_model, 2)},{round(strength_clip, 2)})"
            print(f"  [{lora_count}] lora(mod,clip): {lora_model_info}")
            lora_model, lora_clip = comfy.sd.load_lora_for_models(ckpt, clip, comfy.utils.load_torch_file(lora_path), strength_model, strength_clip)

            # Call the function again with the new lora_model and lora_clip and the remaining tuples
            return recursive_load_lora(lora_params[1:], lora_model, lora_clip, folder_paths, lora_count)
        
        if (show_node):
            print(f"\033[36mApply LoRA Stack 💬ED - Lora load(Not use Cashe):\033[0m")
        print(f"Lora:")
        lora_count = 0
        
        # Unpack lora parameters from the first element of the list for now
        lora_name, strength_model, strength_clip = lora_params[0]
        lora_model, lora_clip = recursive_load_lora(lora_params, ckpt, clip, folder_paths, lora_count)

        return lora_model, lora_clip


    def apply_lora_ed(self, context=None, **kwargs):
        ctx = new_context_ed(context, **kwargs)  
    
        _, model, clip, vae, positive, negative, latent, images, seed, lora_stack  = context_2_tuple_ed(ctx,["model", "clip", "vae", "positive", "negative", "latent", "images", "seed", "lora_stack"])
        
        if lora_stack:
            lora_params = []
            lora_params.extend(lora_stack)
            model, clip = Apply_LoRA_Stack_ED.apply_load_lora(lora_params, model, clip)
            lora_stack = None
            ctx = new_context_ed(context, model=model, clip=clip, lora_stack=lora_stack)
        
        return (ctx, model, clip, vae, positive, negative, latent, images, seed,)

###############################################################################################################

# Efficient Loader ED    
class EfficientLoader_ED():

    Paint_Mode = {
        "✍️ Txt2Img": 1,
        "🦱 Img2Img": 2,
        "🎨 Inpaint(Ksampler)": 3,
        "🎨 Inpaint(MaskDetailer)": 4,
    }

    @classmethod
    def INPUT_TYPES(cls):
        types = {"required": { "ckpt_name": (["🔌 model_opt input"] + folder_paths.get_filename_list("checkpoints"),),
                              "vae_name": (["Baked VAE"] + folder_paths.get_filename_list("vae"),),
                              "clip_skip": ("INT", {"default": -2, "min": -24, "max": 0, "step": 1}),                        
                              "paint_mode": ( list(EfficientLoader_ED.Paint_Mode.keys()), {"default": "✍️ Txt2Img"}),
                              "batch_size": ("INT", {"default": 1, "min": 1, "max": 262144}),
                              "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                              "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                              "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                              "scheduler": (SCHEDULERS,),
                              "positive": ("STRING", {"default": "","multiline": True, "dynamicPrompts": True}),
                              "negative": ("STRING", {"default": "", "multiline": True, "dynamicPrompts": True}),
                              "image_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 1}),
                              "image_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 1}),
                              },
                "optional": {
                             "lora_stack": ("LORA_STACK",),
                             "cnet_stack": ("CONTROL_NET_STACK",),
                             "pixels": ("IMAGE",),
                             "mask": ("MASK",),
                             "model_opt": ("MODEL",),
                             "clip_opt": ("CLIP",)},
                "hidden": { "prompt": "PROMPT",
                            "my_unique_id": "UNIQUE_ID",
                            "extra_pnginfo": "EXTRA_PNGINFO",}
                }
        names = types["required"]["ckpt_name"][0]
        populate_items(names, "checkpoints")        
        return types

    RETURN_TYPES = ("RGTHREE_CONTEXT", "MODEL", "CONDITIONING", "CONDITIONING", "LATENT", "VAE", "DEPENDENCIES",)
    RETURN_NAMES = ("CONTEXT", "MODEL", "CONDITIONING+", "CONDITIONING-", "LATENT", "VAE", "DEPENDENCIES",)
    FUNCTION = "efficientloader_ed"
    CATEGORY = "Efficiency Nodes/Loaders"
        
    def efficientloader_ed(self, vae_name, clip_skip, paint_mode, batch_size, 
                        seed, cfg, sampler_name, scheduler,
                        positive, negative, image_width, image_height, lora_stack=None, cnet_stack=None,
                        pixels=None, mask=None, model_opt=None, clip_opt=None,
                        refiner_name="None", positive_refiner=None, negative_refiner=None, ascore=None, prompt=None,
                        my_unique_id=None, extra_pnginfo=None, loader_type="regular", **kwargs):
        
        global loaded_objects        
        ckpt_name  = kwargs["ckpt_name"]["content"]
        
        # Clean globally stored objects
        globals_cleanup(prompt)

        # Retrieve cache numbers
        vae_cache, ckpt_cache, lora_cache, refn_cache = get_cache_numbers("Efficient Loader")
        
        # Embedding stacker process
        lora_stack, positive, negative, positive_refiner, negative_refiner = Embedding_Stacker_ED.embedding_process(lora_stack, positive, negative, positive_refiner, negative_refiner)
        
        
        # def workflow_to_map(workflow):
        # nodes = {}
        # links = {}
        # for link in workflow['links']:
        # links[link[0]] = link[1:]
        # for node in workflow['nodes']:
        # nodes[str(node['id'])] = node
        # return nodes, links
        # for link in nodes[my_unique_id]['outputs'][0]['links']:
        # link_node_id = links[link][2]

                # for node in workflow["nodes"]:
                    # node_id = node["id"]
                    # if node["type"] == "Apply LoRA 💬ED" and node["id"] == link_node_id:
                        # if node["properties"]["Turn on Applry Lora"] == True:
                            # print(f"\033[36mEfficient Loader ED:Apply LoRA ED is linked, Lora loading is pending.\033[0m")
                            # use_apply_lora = True
                        # break        
        
        # GET PROPERTIES #
        this_sync = True
        tiled_vae_encode = False
        vae_encode_tile_size = 512
        use_apply_lora = False
        token_normalization = "none"
        weight_interpretation = "comfy"
        
        if extra_pnginfo and "workflow" in extra_pnginfo:
            workflow = extra_pnginfo["workflow"]
            #nodes, links = workflow_to_map(workflow)
            for node in workflow["nodes"]:
                if node["id"] == int(my_unique_id):
                    tiled_vae_encode = node["properties"]["Use tiled VAE encode"]
                    this_sync = node["properties"]["Synchronize widget with image size"]
                    token_normalization = node["properties"]["Token normalization"]
                    weight_interpretation = node["properties"]["Weight interpretation"]
                if node["type"] == "Apply LoRA Stack 💬ED" and not use_apply_lora:
                    if node["properties"]["Turn on Apply Lora"] == True:
                        print(f"\033[36mEfficient Loader ED:Apply LoRA Stack ED is exist, loading Lora is pending.\033[0m")
                        use_apply_lora = True
       
        if ckpt_name == "🔌 model_opt input" and model_opt is None:
            raise Exception("Efficient Loader ED: ckpt_name or model_opt is required.\n\n\n\n\n\n")
        
        if ckpt_name == "🔌 model_opt input":
            if model_opt is None:
                raise Exception("Efficient Loader ED: ckpt_name or model_opt is required.\n\n\n\n\n\n")        
            if clip_opt is None:
                raise Exception("Efficient Loader ED: clip_opt is required when using model_opt.\n\n\n\n\n\n")            
            
            loaded_objects["ckpt"] = []
            loaded_objects["lora"] = []
            lora_params = []
            model = model_opt
            clip =clip_opt
            loaded_objects["ckpt"].append(("using model_opt", None, None, None, [my_unique_id]))
        
        elif  lora_stack and not use_apply_lora:
            # Initialize an empty list to store LoRa parameters.
            lora_params = []

            # Check if lora_name is not the string "None" and if so, add its parameters.
            # if lora_name != "None":
                # lora_params.append((lora_name, lora_model_strength, lora_clip_strength))

            # If lora_stack is not None or an empty list, extend lora_params with its items.
            if lora_stack:
                lora_params.extend(lora_stack)
                lora_stack = None

            # Load LoRa(s)
            model, clip = load_lora(lora_params, ckpt_name, my_unique_id, cache=lora_cache, ckpt_cache=ckpt_cache, cache_overwrite=True)

            #if vae_name == "Baked VAE":
                #vae = get_bvae_by_ckpt_name(ckpt_name)
        else:
            #global loaded_objects
            loaded_objects["lora"] = []
            model, clip, vae = load_checkpoint(ckpt_name, my_unique_id, cache=ckpt_cache, cache_overwrite=True)
            lora_params = None
            
        # Check for custom VAE
        if vae_name != "Baked VAE":
            vae = load_vae(vae_name, my_unique_id, cache=vae_cache, cache_overwrite=True)
        else:
            vae = get_bvae_by_ckpt_name(ckpt_name)
            loaded_objects["vae"] = []
            loaded_objects["vae"].append(("Baked vae", vae, [my_unique_id]))
                            
        ############################# END EDITED ############################
     
        ##Load Refiner Checkpoint if given
        # if refiner_name != "None":
            # refiner_model, refiner_clip, _ = load_checkpoint(refiner_name, my_unique_id, output_vae=False,
                                                             # cache=refn_cache, cache_overwrite=True, ckpt_type="refn")
        # else:
            # refiner_model = refiner_clip = None

        ##Extract clip_skips
        # refiner_clip_skip = clip_skip[1] if loader_type == "sdxl" else None
        # clip_skip = clip_skip[0] if loader_type == "sdxl" else clip_skip

        ##Encode prompt based on loader_type
        # positive_encoded, negative_encoded, clip, refiner_positive_encoded, refiner_negative_encoded, refiner_clip = \
            # encode_prompts(positive, negative, token_normalization, weight_interpretation, clip, clip_skip,
                           # refiner_clip, refiner_clip_skip, ascore, loader_type == "sdxl",
                           # image_width, image_height)
        
        ##Refiner positive encoded 
        # if loader_type == "sdxl" and refiner_clip and refiner_clip_skip and ascore:
            # if positive_refiner:
                # refiner_positive_encoded = None
                # refiner_positive_encoded = bnk_adv_encode.AdvancedCLIPTextEncode().encode(refiner_clip, positive_refiner, token_normalization, weight_interpretation)[0]
                # refiner_positive_encoded = bnk_adv_encode.AddCLIPSDXLRParams().encode(refiner_positive_encoded, image_width, image_height, ascore[0])[0]
            # if negative_refiner:
                # refiner_negative_encoded = None
                # refiner_negative_encoded = bnk_adv_encode.AdvancedCLIPTextEncode().encode(refiner_clip, negative_refiner, token_normalization, weight_interpretation)[0]
                # refiner_negative_encoded = bnk_adv_encode.AddCLIPSDXLRParams().encode(refiner_negative_encoded, image_width, image_height, ascore[1])[0]
        
        ############################### PROMPT ENCODING ############################
        refiner_model = refiner_clip = refiner_clip_skip = None
        
        modle_type = None
        if hasattr(model, "model"):
            modle_type = model.model.__class__.__name__            
        
        if ckpt_name == "🔌 model_opt input":
            print(f"\033[38;5;173mEfficient Loader ED : model from model_opt input, Ignore clip skip\033[0m")
        elif modle_type == "Flux":
            print(f"\033[38;5;173mEfficient Loader ED : model type is {modle_type}, Ignore clip skip\033[0m")
        elif clip_skip == 0:
            print(f"\033[38;5;173mEfficient Loader ED : clip skip is 0, Ignore clip skip\033[0m")
        else:
            clip = CLIPSetLastLayer().set_last_layer(clip, clip_skip)[0]
        
        #Encode prompt
        if token_normalization != "none" or weight_interpretation != "comfy":
            # Encode prompt based on loader_type
            print(f"\033[38;5;173mEfficientLoader ED: Using AdvancedCLIPTextEncode (token normalization - {token_normalization}, weight interpretation - {weight_interpretation})\033[0m")
            positive_encoded = AdvancedCLIPTextEncode().encode(clip, positive, token_normalization, weight_interpretation)[0]
            negative_encoded = AdvancedCLIPTextEncode().encode(clip, negative, token_normalization, weight_interpretation)[0]
        else:
            positive_encoded = CLIPTextEncode().encode(clip, positive)[0]
            negative_encoded = CLIPTextEncode().encode(clip, negative)[0]

        # Apply ControlNet Stack if given
        if cnet_stack:
            controlnet_conditioning = TSC_Apply_ControlNet_Stack().apply_cnet_stack(positive_encoded, negative_encoded, cnet_stack)
            positive_encoded, negative_encoded = controlnet_conditioning[0], controlnet_conditioning[1]


        ################################### LATENT ##############################
        #✍️ Txt2Img         
        if paint_mode == "✍️ Txt2Img":
            # Create Empty Latent
            latent_t = torch.zeros([batch_size, 4, image_height // 8, image_width // 8]).cpu()
            samples_latent = {"samples":latent_t}
        else:
            if pixels is None:
                raise Exception("Efficient Loader ED: Img2Img or Inpaint mode requires an image.\n\n\n\n\n\n")
            
            #VAE Encode
            if tiled_vae_encode:
                latent_t = vae.encode_tiled(pixels[:,:,:,:3], tile_x=vae_encode_tile_size, tile_y=vae_encode_tile_size, )
            else:
                latent_t = vae.encode(pixels[:,:,:,:3])
            k = {"samples":latent_t}
            _, image_height, image_width, _ = pixels.shape
            
            # 🎨 Inpaint
            if paint_mode == "🎨 Inpaint(Ksampler)":
                if  mask is None:
                    raise Exception("Efficient Loader ED: Inpaint mode requires an Mask.\n\n\n\n\n\n")
                (positive_encoded, negative_encoded, k) = InpaintModelConditioning().encode(positive_encoded, negative_encoded, pixels, vae, mask)
                
            elif paint_mode == "🎨 Inpaint(MaskDetailer)":
                if  mask is None:
                    raise Exception("Efficient Loader ED: Inpaint mode requires an Mask.\n\n\n\n\n\n")

            #RepeatLatentBatch
            samples_latent = RepeatLatentBatch().repeat(k, batch_size)[0]
            
            # change image_width and image_height widget from image size
            if this_sync:
                PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "image_width", "type": "text", "data": image_width})
                PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "image_height", "type": "text", "data": image_height})
        ################################### LATENT END##############################

        ###print_loaded_objects_entries()
        print_loaded_objects_entries(my_unique_id, prompt)
        
        ### lora apply when using model_opt
        if ckpt_name == "🔌 model_opt input":            
            if  lora_stack and not use_apply_lora:
                lora_params.extend(lora_stack)
                lora_stack = None
                model, clip = Apply_LoRA_Stack_ED.apply_load_lora(lora_params, model, clip, False)                
            
        # Data for XY Plot
        dependencies = (vae_name, ckpt_name, clip, clip_skip, refiner_name, refiner_clip, refiner_clip_skip,
                        positive, negative, token_normalization, weight_interpretation, ascore,
                        image_width, image_height, lora_params, cnet_stack)
                
        context = new_context_ed(None, model=model, clip=clip, vae=vae, positive=positive_encoded, negative=negative_encoded, 
                latent=samples_latent, images=pixels, seed=seed, step_refiner=batch_size, cfg=cfg, ckpt_name=ckpt_name, sampler=sampler_name, scheduler=scheduler, clip_width=image_width, clip_height=image_height, text_pos_g=positive, text_neg_g=negative, mask=mask, lora_stack=lora_stack)

        return (context, model, positive_encoded, negative_encoded, samples_latent, vae, dependencies,)

#####################################################################################################

# Load Image ED
prompt_blacklist_ed = set([
    'filename_prefix', 'file'
])

class LoadImage_ED(LoadImage):
    upscale_methods = ["do not upscale", "nearest-exact", "bilinear", "area", "bicubic", "lanczos"]
    proportion_methods = ["disabled", "based on width", "based on height", "disabled & crop center"]
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required": {
                              "image": (sorted(files), {"image_upload": True}),
                              "upscale_method": (s.upscale_methods,),
                              "width": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 1}),
                              "height": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 1}),
                              "keep_proportions": (s.proportion_methods,),},
                    "hidden": { "my_unique_id": "UNIQUE_ID",}
                    }
    CATEGORY = "Efficiency Nodes/Image"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING",)
    RETURN_NAMES = ("IMAGE", "MASK", "PROMPT_TEXT",)
    FUNCTION = "load_image"

    def load_image(self, image, upscale_method, width, height, keep_proportions, my_unique_id):        
        output_image, output_mask = super().load_image(image)
        
        #################################################
        image_path = folder_paths.get_annotated_filepath(image)
        info = Image.open(image_path).info

        positive = ""
        negative = ""
        text = ""
        prompt_dicts = {}
        node_inputs = {}

        def get_node_inputs(x):
            if x in node_inputs:
                return node_inputs[x]
            else:
                node_inputs[x] = None

                obj = nodes_NODE_CLASS_MAPPINGS.get(x, None)
                if obj is not None:
                    input_types = obj.INPUT_TYPES()
                    node_inputs[x] = input_types
                    return input_types
                else:
                    return None

        if isinstance(info, dict) and 'workflow' in info:
            prompt = json.loads(info['prompt'])
            for k, v in prompt.items():
                input_types = get_node_inputs(v['class_type'])
                if input_types is not None:
                    inputs = input_types['required'].copy()
                    if 'optional' in input_types:
                        inputs.update(input_types['optional'])

                    for name, value in inputs.items():
                        if name in prompt_blacklist_ed:
                            continue
                        
                        if value[0] == 'STRING' and name in v['inputs'] and not isinstance(v['inputs'][name], list):
                            prompt_dicts[f"{k}.{name.strip()}"] = (v['class_type'], v['inputs'][name])
                        if value[0] == 'INT' and name in v['inputs'] and name.lower() == 'seed':
                            prompt_dicts[f"{k}.{name.strip()}"] = (v['class_type'], v['inputs'][name])

            for k, v in prompt_dicts.items():
                text += f"{k} [{v[0]}] ==> {v[1]}\n"

            #positive = prompt_dicts.get(positive_id.strip(), "")
            #negative = prompt_dicts.get(negative_id.strip(), "")
        else:
            text = "There is no prompt information within the image."

        _, image_height, image_width, _ = output_image.shape
        text += "\nImage Size: " + str(image_width) + " x " + str(image_height )
        
        ## Upscale image & Mask
        if upscale_method != "do not upscale":            
            crop = "center" if keep_proportions == "disabled & crop center" else "disabled"
            
            if keep_proportions == "based on width" or keep_proportions == "based on height":
                oh, ow = (image_height, image_width)
                width = ow if width == 0 else width
                height = oh if height == 0 else height
                ratio = (width / ow) if keep_proportions == "based on width" else (height / oh)
                width = round(ow*ratio)
                height = round(oh*ratio)
                PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "width", "type": "text", "data": width})
                PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "height", "type": "text", "data": height})
            
            output_image = ImageScale().upscale(output_image, upscale_method, width, height, crop)[0] 
            
            if output_mask is not None:
                if upscale_method == "lanczos":
                    upscale_method = "bicubic"
                t = output_mask.unsqueeze(1)
                t = comfy.utils.common_upscale(t, width, height, upscale_method, crop)
                output_mask = t.squeeze(1)
        
        return (output_image, output_mask, text,)

    @classmethod
    def IS_CHANGED(s, image, upscale_method, width, height, keep_proportions, my_unique_id):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image, upscale_method, width, height, keep_proportions, my_unique_id):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True

# Save Image ED
class SaveImage_ED(SaveImage):

    @classmethod
    def INPUT_TYPES(s):
        return {"required": { },
                    "optional": {
                        "context_opt": ("RGTHREE_CONTEXT",),
                        "image_opt": ("IMAGE",),
                        "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                    },
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"},
                }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "Efficiency Nodes/Image"

    def save_images(self, context_opt=None, image_opt=None, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None, unique_id=None):
        images = None
        
        if context_opt is not None:
            _, images = context_2_tuple_ed(context_opt,["images"])
        if image_opt is not None:
            images = image_opt
        
        if images is not None:
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": unique_id, "widget_name": "play_sound", "type": "sound", "data": "play_sound"})
        
            return super().save_images(images, filename_prefix=filename_prefix, prompt=prompt, extra_pnginfo=extra_pnginfo)
        else:
            return { "ui": { "images": list() } }

###############################################################################################################

MAX_CASHE_ED_CONTROLNET = 1

# Control Net Script ED
class Control_Net_Script_ED:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"control_net": ("CONTROL_NET",),
                             "image": ("IMAGE",),
                             "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                             "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                             "end_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001})},
                "optional": {"cnet_stack": ("CONTROL_NET_STACK",),
                                   "script": ("SCRIPT",)},
                }

    RETURN_TYPES = ("SCRIPT",)
    RETURN_NAMES = ("SCRIPT",)
    FUNCTION = "control_net_script_ed"
    CATEGORY = "Efficiency Nodes/Scripts"

    def control_net_script_ed(self, control_net, image, strength, start_percent, end_percent, cnet_stack=None, script=None):
        script = script or {}        
        # If control_net_stack is None, initialize as an empty list        
        cnet_stack = [] if cnet_stack is None else cnet_stack

        # Extend the control_net_stack with the new tuple
        cnet_stack.extend([(control_net, image, strength, start_percent, end_percent)])
        script["control_net"] = (cnet_stack)
        return (script,)

###############################################################################################################

# Refiner Script ED
class Refiner_Script_ED:
    set_seed_cfg_sampler = {
        "from context": 1,
        "from node only": 2,
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                            "set_seed_cfg_sampler": (list(Refiner_Script_ED.set_seed_cfg_sampler.keys()), {"default": "from context"}),
                            "add_noise": (["enable", "disable"], ),
                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "steps": ("INT", {"default": 6, "min": 1, "max": 10000}),
                            "cfg": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 100.0}),
                            "sampler_name": (comfy.samplers.KSampler.SAMPLERS, {"default": "dpmpp_sde"}),
                            "scheduler": (SCHEDULERS, {"default": "karras"}),
                            "start_at_step": ("INT", {"default": 3, "min": 0, "max": 10000}),
                            "end_at_step": ("INT", {"default": 6, "min": 0, "max": 10000}),
                            "ignore_batch_size": ("BOOLEAN", {"default": True}),
                            "do_refine_only": ("BOOLEAN", {"default": True}),
                        },
                "optional": {"context_opt": ("RGTHREE_CONTEXT",),
                            "refiner_model_opt": ("MODEL",),
                            "refiner_clip_opt": ("CLIP",),
                            "refiner_vae_opt": ("VAE",),
                            "script": ("SCRIPT",),},
                "hidden": {"my_unique_id": "UNIQUE_ID",},}
    RETURN_TYPES = ("SCRIPT",)
    RETURN_NAMES = ("SCRIPT",)
    FUNCTION = "refiner_script_ed"
    CATEGORY = "Efficiency Nodes/Scripts"

    def refiner_script_ed(self, set_seed_cfg_sampler, add_noise, seed, steps, cfg, sampler_name, scheduler, start_at_step, end_at_step, ignore_batch_size, do_refine_only, context_opt=None, refiner_model_opt=None, refiner_clip_opt=None, refiner_vae_opt=None, script=None, my_unique_id=None):
        script = script or {}
        
        if refiner_model_opt is not None:
            if refiner_clip_opt is not None and refiner_vae_opt is not None:
                refiner_model = refiner_model_opt
                refiner_clip = refiner_clip_opt
                refiner_vae = refiner_vae_opt
            else:
                raise Exception("Refiner Script ED: refiner_clip and refiner_vae are required.\n\n\n\n\n\n")
        elif context_opt is not None:
            # Unpack from CONTEXT 
            _, refiner_model, refiner_clip, refiner_vae, c_seed, c_cfg, c_sampler, c_scheduler, = context_2_tuple_ed(context_opt,["model", "clip", "vae", "seed", "cfg", "sampler", "scheduler"])
            if set_seed_cfg_sampler == "from context":
                if c_seed is None:
                    raise Exception("KSampler (Efficient) ED: No seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
                else:
                    seed = c_seed
                    PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                    cfg = c_cfg
                    PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
                    sampler_name = c_sampler
                    PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "sampler_name", "type": "text", "data": sampler_name})
                    scheduler = c_scheduler
                    PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "scheduler", "type": "text", "data": scheduler})
        else:
            refiner_model = None
        
        if refiner_model is not None:
            refiner_script = (refiner_model, refiner_clip, refiner_vae, add_noise, seed, steps, cfg, sampler_name, scheduler, start_at_step, end_at_step, ignore_batch_size, do_refine_only)
            #print(f"\033[38;5;173mRefiner Script ED: Refiner script loading. steps:{steps}, start step:{start_at_step}, end step:{end_at_step}\033[0m")
            script["refiner_script"] = refiner_script
        
        return (script,)

###############################################################################################################

# Int Holder ED
class Int_Holder_ED:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"output_int": ("INT", {"default": 0, "min": 0, "max": sys.maxsize, "step": 1}),},
            "optional": {"int_opt": ("INT", {"forceInput": True}),},
            "hidden": {"my_unique_id": "UNIQUE_ID",},
        }

    FUNCTION = "store_value"
    RETURN_TYPES = ("INT", )
    RETURN_NAMES = ("INT",)
    OUTPUT_NODE = True
    CATEGORY = "Efficiency Nodes/Simple Eval"    

    def store_value(self, output_int, int_opt=None, my_unique_id=None):
        if int_opt is not None:
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "output_int", "type": "text", "data": int_opt})
            output_int = int_opt
        return (output_int,)


##############################################################################################################
# NODE MAPPING
##############################################################################################################

NODE_CLASS_MAPPINGS = {
    #ED
    "Efficient Loader 💬ED": EfficientLoader_ED,
    #"KSampler (Efficient) 💬ED": KSampler_ED,
    #"KSampler TEXT (Eff.) 💬ED": KSamplerTEXT_ED,    
    "Load Image 💬ED": LoadImage_ED,
    "Save Image 🔔ED": SaveImage_ED,
    "Control Net Script 💬ED": Control_Net_Script_ED,
    "Refiner Script 💬ED": Refiner_Script_ED,
    "Embedding Stacker 💬ED": Embedding_Stacker_ED,
    "Apply LoRA Stack 💬ED": Apply_LoRA_Stack_ED,
    "LoRA Stacker 💬ED": LoRA_Stacker_ED,
    "Int Holder 💬ED": Int_Holder_ED,
}

#=================================================================================
##################################       KSampler (Efficient) ED      ##################################

if os.path.exists(os.path.join(custom_nodes_dir, "efficiency-nodes-comfyui")):
    printout = "Attempting to add 'KSampler (Efficient) ED' Node (efficiency-nodes-comfyui add-on)..."
    print(f"{message('Efficiency Nodes ED:')} {printout}", end="")
    
    try:    
        if "KSampler (Efficient)" in nodes_NODE_CLASS_MAPPINGS and "Apply ControlNet Stack" in nodes_NODE_CLASS_MAPPINGS:
            TSC_KSampler = nodes_NODE_CLASS_MAPPINGS["KSampler (Efficient)"]
            TSC_Apply_ControlNet_Stack = nodes_NODE_CLASS_MAPPINGS["Apply ControlNet Stack"]
        else:
            raise Exception("'Efficiency Nodes for ComfyUI' is not installed.")

        # KSampler (Efficient) ED
        class KSampler_ED():

            set_seed_cfg_from = {
                "from node to ctx": 1,
                "from context": 2,
                "from node only": 3,
            }

            @classmethod
            def INPUT_TYPES(cls):
                return {"required":
                            {"context": ("RGTHREE_CONTEXT",),
                            "set_seed_cfg_sampler": (list(KSampler_ED.set_seed_cfg_from.keys()), {"default": "from context"}),
                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                            "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                            "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                            "scheduler": (SCHEDULERS,),
                            "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                            "preview_method": (["auto", "latent2rgb", "taesd", "vae_decoded_only", "none"],),
                            },
                        "optional": {
                            #"vae_decode": (["true", "true (tiled)", "false"],),
                            "guide_size": ("FLOAT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                            "guide_size_for": ("BOOLEAN", {"default": True, "label_on": "mask bbox", "label_off": "crop region"}),
                            "max_size": ("FLOAT", {"default": 1216, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                            "feather": ("INT", {"default": 15, "min": 0, "max": 100, "step": 1}),
                            "crop_factor": ("FLOAT", {"default": 3.0, "min": 1.0, "max": 10, "step": 0.1}),
                            "cycle": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                            "script": ("SCRIPT",),
                            "detailer_hook": ("DETAILER_HOOK",),
                            },
                        "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},}

            RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE", "INT",)
            RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE", "STEPS_INT",)
            OUTPUT_NODE = True
            FUNCTION = "sample_ed"
            CATEGORY = "Efficiency Nodes/Sampling"

            def sample_ed(self, context, set_seed_cfg_sampler, seed, steps, cfg, sampler_name, scheduler, preview_method, 
                        vae_decode="true", guide_size=512, guide_size_for=False, max_size=1216, feather=15, crop_factor=3, cycle=1,
                        t_positive=None, t_negative=None, denoise=1.0, refiner_denoise=1.0, prompt=None, 
                        extra_pnginfo=None, my_unique_id=None, script=None, detailer_hook=None,
                        add_noise=None, start_at_step=None, end_at_step=None,
                        return_with_leftover_noise=None, sampler_type="regular"):

                # Unpack from CONTEXT 
                _, model, clip, vae, positive, negative, latent_image, optional_image, c_batch, c_seed, c_cfg, c_sampler, c_scheduler, positive_prompt, mask = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative", "latent", "images", "step_refiner", "seed", "cfg", "sampler", "scheduler", "text_pos_g", "mask"])
        
                mask_detailer_mode = False
                drop_size = 5
                inpaint_model = False
                noise_mask_feather = 20
                if sampler_type=="regular" and extra_pnginfo and "workflow" in extra_pnginfo:
                    workflow = extra_pnginfo["workflow"]
                    for node in workflow["nodes"]:
                        if node["id"] == int(my_unique_id):
                            mask_detailer_mode = node["properties"]["MaskDetailer mode"]
                            drop_size = int(node["properties"]["(MaskDetailer) drop size"])
                            inpaint_model = node["properties"]["(MaskDetailer) inpaint model enable"]
                            noise_mask_feather = int(node["properties"]["(MaskDetailer) noise mask feather"])
                            if node["properties"]["Use tiled VAE decode"]:
                                vae_decode = "true (tiled)"
                            else:
                                vae_decode = "true"
                            break
                
                if t_positive:
                    positive = t_positive
                if t_negative:
                    negative = t_negative
                if model is None:
                    raise Exception("KSampler (Efficient) ED: Model is None. \n\n\n\n\n\n")                
                if latent_image is None:
                    raise Exception("KSampler (Efficient) ED requires 'Latent' for sampling.\n\n\n\n\n\n")        
        
                if set_seed_cfg_sampler == "from context":
                    if c_seed is None:
                        raise Exception("KSampler (Efficient) ED: No seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
                    else:
                        seed = c_seed
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                        cfg = c_cfg
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
                        sampler_name = c_sampler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "sampler_name", "type": "text", "data": sampler_name})
                        scheduler = c_scheduler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "scheduler", "type": "text", "data": scheduler})
                elif set_seed_cfg_sampler =="from node to ctx":
                    context = new_context_ed(context, seed=seed, cfg=cfg, sampler=sampler_name, scheduler=scheduler)
            
                #---------------------------------------------------------------------------------------------------------------
                def keys_exist_in_script(*keys):
                    return any(key in script for key in keys) if script else False
                
                ####################################### ED Control net script
                if keys_exist_in_script("control_net"):
                    cnet_stack = script["control_net"]
                    #script.pop("control_net", None)
                    print(f"\033[38;5;173mKSampler ED: Apply control net from script\033[0m")
                    controlnet_conditioning = TSC_Apply_ControlNet_Stack().apply_cnet_stack(positive, negative, cnet_stack)
                    positive, negative = controlnet_conditioning[0], controlnet_conditioning[1]
                    context = new_context_ed(context, positive=positive, negative=negative)
                
                refiner_model = None
                # refiner script
                if keys_exist_in_script("refiner_script"):                    
                    refiner_model, refiner_clip, refiner_vae, refiner_add_noise, refiner_seed, refiner_steps, refiner_cfg, refiner_sampler_name, refiner_scheduler, refiner_start_at_step, refiner_end_at_step, refiner_ignore_batch_size, do_refine_only = script["refiner_script"]
                    
                    if do_refine_only:
                        denoise = 0                    
                    # use KSamplerAdvanced
                    if denoise == 1.0:
                        sampler_type = "advanced"
                        add_noise = "enable"
                        start_at_step = 0
                        end_at_step = 10000
                        return_with_leftover_noise = "enable"                 

                if mask_detailer_mode:
                    if not Impact_ed_loading_success:
                        raise Exception("KSampler (Efficient) ED: Inpaint(MaskDetailer) mode is only available when Impact ED loading is successful.\n\n\n\n\n\n")

                    print(f"\033[38;5;173mKSampler ED: use MaskDetailer(ImpactPack) for inpainting\033[0m")
                    mask_mode = True
                    refiner_ratio = 0.2
                    output_images, _, _ = MaskDetailer_ED.mask_sampling(optional_image, mask, model, clip, vae, positive, negative,
                            guide_size, guide_size_for, max_size, mask_mode,
                            seed, steps, cfg, sampler_name, scheduler, denoise,
                            feather, crop_factor, drop_size, refiner_ratio, c_batch, cycle, 
                            detailer_hook, inpaint_model, noise_mask_feather)
                            
                    result_ui = PreviewImage().save_images(output_images, prompt=prompt, extra_pnginfo=extra_pnginfo)["ui"]
                    context = new_context_ed(context, images=output_images) #RE
                    result = (context, output_images, steps,)
            
                else:
                    return_dict = TSC_KSampler().sample(model, seed, steps, cfg, sampler_name, scheduler, 
                        positive, negative, latent_image, preview_method, vae_decode, denoise=denoise, prompt=prompt, 
                        extra_pnginfo=extra_pnginfo, my_unique_id=my_unique_id,
                        optional_vae=vae, script=script, add_noise=add_noise, start_at_step=start_at_step, end_at_step=end_at_step,
                        return_with_leftover_noise=return_with_leftover_noise, sampler_type=sampler_type)               
        
                    _, _, _, latent_list, _, output_images = return_dict["result"]
                    result_ui = return_dict["ui"]
            
                    context = new_context_ed(context, latent=latent_list, images=output_images) #RE
                    result = (context, output_images, steps)
                
                # apply refiner script 
                if refiner_model is not None:          
                    refiner_positive = CLIPTextEncode().encode(refiner_clip, positive_prompt)[0]
                    refiner_negative = CLIPTextEncode().encode(refiner_clip, "")[0]
                    
                    if refiner_ignore_batch_size:
                        refiner_images = output_images = output_images[0:1].clone()                        
                    else:
                        refiner_images = output_images
                    
                    #VAE Encode
                    if "tiled" in vae_decode:
                        k = refiner_vae.encode_tiled(refiner_images[:,:,:,:3], tile_x=320, tile_y=320, )
                    else:
                        k = refiner_vae.encode(refiner_images[:,:,:,:3])
                    latent_image = {"samples":k}
                    
                    print(f"\033[38;5;173mKSampler ED: Running refiner script. steps:{refiner_steps}, start step:{refiner_start_at_step}, end step:{refiner_end_at_step}\033[0m")
                    return_dict = TSC_KSampler().sample(refiner_model, refiner_seed, refiner_steps, refiner_cfg, refiner_sampler_name, refiner_scheduler, refiner_positive, refiner_negative, latent_image, preview_method, vae_decode, denoise=1.0, prompt=prompt, extra_pnginfo=extra_pnginfo, my_unique_id=my_unique_id, optional_vae=refiner_vae, script=None, add_noise=refiner_add_noise, start_at_step=refiner_start_at_step, end_at_step=refiner_end_at_step, return_with_leftover_noise=return_with_leftover_noise, sampler_type="advanced")
                    
                    _, _, _, latent_list, _, refiner_images = return_dict["result"]                    
                    result_ui = return_dict["ui"]
                    output_images = ImageBatch().batch(output_images, refiner_images)[0]
                    
                    context = new_context_ed(context, latent=latent_list, images=output_images) #RE
                    result = (context, output_images, steps)                    
                
                return {"ui": result_ui, "result": result}
        
        NODE_CLASS_MAPPINGS.update({"KSampler (Efficient) 💬ED": KSampler_ED})

####################################  KSamplerTEXT ED #for BackGround Make  ###############################

        class KSamplerTEXT_ED():
            @classmethod
            def INPUT_TYPES(cls):
                return {"required":
                            {"context": ("RGTHREE_CONTEXT",),
                            "set_seed_cfg_sampler": (list(KSampler_ED.set_seed_cfg_from.keys()), {"default": "from context"}),
                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                            "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                            "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                            "scheduler": (SCHEDULERS,),
                            "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                            "preview_method": (["auto", "latent2rgb", "taesd", "vae_decoded_only", "none"],),
                            "vae_decode": (["true", "true (tiled)", "false"],),
                            "positive": ("STRING", {"default": "","multiline": True}),
                            "negative": ("STRING", {"default": "", "multiline": True}),
                            },
                        #"optional": {
                            #"script": ("SCRIPT",),},
                        "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},
                        }

            RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE",)
            RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE",)
            OUTPUT_NODE = True
            FUNCTION = "backgroundmake_ed"
            CATEGORY = "Efficiency Nodes/Sampling"

            def backgroundmake_ed(self, context, set_seed_cfg_sampler, seed, steps, cfg, sampler_name, scheduler, preview_method,
                    vae_decode, positive=None, negative=None, denoise=1.0, refiner_denoise=1.0, 
                    prompt=None, extra_pnginfo=None, my_unique_id=None,
                    script=None, add_noise=None, start_at_step=None, end_at_step=None,
                    return_with_leftover_noise=None, sampler_type="regular"):
        
                def get_latent_size(samples):
                    size_dict = {}
                    i = 0
                    for tensor in samples['samples'][0]:
                        if not isinstance(tensor, torch.Tensor):
                            cstr(f'Input should be a torch.Tensor').error.print()
                        shape = tensor.shape
                        tensor_height = shape[-2]
                        tensor_width = shape[-1]
                        size_dict.update({i:[tensor_width, tensor_height]})
                    return ( size_dict[0][0] * 8, size_dict[0][1] * 8 )
        
                _, model, clip, vae, optional_latent, optional_image, c_seed, c_cfg, c_sampler, c_scheduler = context_2_tuple_ed(context,["model", "clip", "vae", "latent", "images", "seed", "cfg", "sampler", "scheduler"])
                
                if model is None:
                    raise Exception("KSampler TEXT ED: Model is None. \n\n\n\n\n\n")                
                if optional_latent is None:
                    raise Exception("KSampler TEXT ED requires 'Latent' for sampling.\n\n\n\n\n\n")        
        
                if set_seed_cfg_sampler == "from context":
                    if c_seed is None:
                        raise Exception("KSampler TEXT (Eff.) 💬ED: No seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
                    else:
                        seed = c_seed
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                        cfg = c_cfg
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
                        sampler_name = c_sampler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "sampler_name", "type": "text", "data": sampler_name})
                        scheduler = c_scheduler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "scheduler", "type": "text", "data": scheduler})
                elif set_seed_cfg_sampler =="from node to ctx":
                    context = new_context_ed(context, seed=seed, cfg=cfg, sampler=sampler_name, scheduler=scheduler)                
                
                if optional_latent is not None:
                    image_width, image_height  = get_latent_size(optional_latent)
                    print(f"KSampler TEXT ED: size get from latent (width {image_width} x height {image_height})")
                elif optional_image is not None:
                    _, image_height, image_width, _ = optional_image.shape
                    print(f"KSampler TEXT ED: size get from image (width {image_width} x height {image_height})")
                else:
                    raise Exception("KSamplerTEXT ED: Reference image or latent is required.\n\n\n\n\n\n")
        
                batch_size = 1
                latent_t = torch.zeros([batch_size, 4, image_height // 8, image_width // 8]).cpu()
                latent_image = {"samples":latent_t}
                
                positive_encoded = CLIPTextEncode().encode(clip, positive)[0]
                negative_encoded = CLIPTextEncode().encode(clip, negative)[0]
                
                return_dict = TSC_KSampler().sample(model, seed, steps, cfg, sampler_name, scheduler, 
                        positive_encoded, negative_encoded, latent_image, preview_method, vae_decode, denoise=denoise, prompt=prompt, 
                        extra_pnginfo=extra_pnginfo, my_unique_id=my_unique_id,
                        optional_vae=vae, script=script, add_noise=add_noise, start_at_step=start_at_step, end_at_step=end_at_step,
                        return_with_leftover_noise=return_with_leftover_noise, sampler_type="regular")                        
        
                _, _, _, latent_list, _, output_images = return_dict["result"]
                                
                context = new_context_ed(context, latent=latent_list, images=output_images)                                
                return (context, output_images)

        NODE_CLASS_MAPPINGS.update({"KSampler Text 💬ED": KSamplerTEXT_ED})
        
        print(f"\r{message('Efficiency Nodes ED:')} {printout}{success('Success!')}")

    except Exception:
        print(f"\r{message('Efficiency Nodes ED:')} {printout}{error('Failed!')}")

#=================================================================================
##################################                FaceDetailer_ED       ##################################

Impact_ed_loading_success = False
MAX_CASHE_ED_FACE = 1

if os.path.exists(os.path.join(custom_nodes_dir, "ComfyUI-Impact-Pack")):
    printout = "Attempting to add 'FaceDetailer ED & MaskDetailer ED' Node (Impact Pack add-on)..."
    print(f"{message('Efficiency Nodes ED:')} {printout}", end="")
    
    try:    
        if "FaceDetailer" in nodes_NODE_CLASS_MAPPINGS and "MaskDetailerPipe" in nodes_NODE_CLASS_MAPPINGS and "DetailerForEachDebug" in nodes_NODE_CLASS_MAPPINGS:
            FaceDetailer = nodes_NODE_CLASS_MAPPINGS["FaceDetailer"]
            MaskDetailerPipe = nodes_NODE_CLASS_MAPPINGS["MaskDetailerPipe"]
            DetailerForEachDebug = nodes_NODE_CLASS_MAPPINGS["DetailerForEachDebug"]
        else:
            raise Exception("'Impact Pack' is not installed.")
        
        if "UltralyticsDetectorProvider" in nodes_NODE_CLASS_MAPPINGS and "SAMLoader" in nodes_NODE_CLASS_MAPPINGS:
            UltralyticsDetectorProvider = nodes_NODE_CLASS_MAPPINGS["UltralyticsDetectorProvider"]
            SAMLoader = nodes_NODE_CLASS_MAPPINGS["SAMLoader"]
        else:
            raise Exception("'UltralyticsDetectorProvider' or 'SAMLoader' are not found.")
        
        def detector_model(model_name, type):    
            detector_type = "ultra_" + type + "_detector"
            if model_name is None or model_name == "None":
                return None                
            cash = cashload_ed(detector_type, model_name)
            if cash is not None:
                return (cash)
            
            if type == "bbox":
                model, _ = UltralyticsDetectorProvider().doit(model_name)
            else:
                _, model = UltralyticsDetectorProvider().doit(model_name)         
            cashsave_ed(detector_type, model_name, model, MAX_CASHE_ED_FACE)
            return (model)
                
        def load_sam_model(model_name, device_mode):
            if model_name == "None" or model_name is None:                
                return None
            cash = cashload_ed("sam_model", model_name)
            if cash is not None:
                return (cash)
            (sam, ) = SAMLoader().load_model(model_name, device_mode)
            cashsave_ed("sam_model", model_name, sam, MAX_CASHE_ED_FACE)
            return (sam)

        # Face Detailer ED
        class FaceDetailer_ED():
            @classmethod
            def INPUT_TYPES(s):
                bboxs = ["bbox/"+x for x in folder_paths.get_filename_list("ultralytics_bbox")] + ["segm/"+x for x in folder_paths.get_filename_list("ultralytics_segm")]
                segms = ["None"] + ["segm/"+x for x in folder_paths.get_filename_list("ultralytics_segm")]
                sams = ["None"] + [x for x in folder_paths.get_filename_list("sams") if 'hq' not in x]
                return {"required": {
                            "context": ("RGTHREE_CONTEXT",),
                            "set_seed_cfg_sampler": (list(KSampler_ED.set_seed_cfg_from.keys()), {"default": "from context"}),
                            "bbox_detector": (bboxs, ),
                            "segm_detector_opt": (segms, ),
                            "sam_model_opt": (sams, ), 
                            "sam_mode": (["AUTO", "Prefer GPU", "CPU"],),
                     
                            "guide_size": ("FLOAT", {"default": 384, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                            "guide_size_for": ("BOOLEAN", {"default": True, "label_on": "bbox", "label_off": "crop_region"}),
                            "max_size": ("FLOAT", {"default": 1024, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                            "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                            "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                            "scheduler": (SCHEDULERS,),
                            "denoise": ("FLOAT", {"default": 0.5, "min": 0.0001, "max": 1.0, "step": 0.01}),
                            "feather": ("INT", {"default": 5, "min": 0, "max": 100, "step": 1}),
                            "noise_mask": ("BOOLEAN", {"default": True, "label_on": "enabled", "label_off": "disabled"}),
                            "force_inpaint": ("BOOLEAN", {"default": True, "label_on": "enabled", "label_off": "disabled"}),

                            "bbox_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                            "bbox_dilation": ("INT", {"default": 10, "min": -512, "max": 512, "step": 1}),
                            "bbox_crop_factor": ("FLOAT", {"default": 3.0, "min": 1.0, "max": 10, "step": 0.1}),

                            "sam_detection_hint": (["center-1", "horizontal-2", "vertical-2", "rect-4", "diamond-4", "mask-area", "mask-points", "mask-point-bbox", "none"],),
                            "sam_dilation": ("INT", {"default": 0, "min": -512, "max": 512, "step": 1}),
                            "sam_threshold": ("FLOAT", {"default": 0.93, "min": 0.0, "max": 1.0, "step": 0.01}),
                            "sam_bbox_expansion": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                            "sam_mask_hint_threshold": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
                            "sam_mask_hint_use_negative": (["False", "Small", "Outter"],),
                            "drop_size": ("INT", {"min": 1, "max": MAX_RESOLUTION, "step": 1, "default": 10}),                     
                            "cycle": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                            },
                        "optional": {
                            "image_opt": ("IMAGE",),
                            "detailer_hook": ("DETAILER_HOOK",),
                            "wildcard": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                            "inpaint_model": ("BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}),
                            "noise_mask_feather": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                        },
                        "hidden": {"my_unique_id": "UNIQUE_ID",},
                    }

            RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE", "IMAGE", "IMAGE", "MASK", "IMAGE",)
            RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE", "CROPPED_REFINED", "CROPPED_ENHANCED_ALPHA", "MASK", "CNET_IMAGES",)
            OUTPUT_IS_LIST = (False, False, True, True, False, True,)    
            FUNCTION = "doit_ed"
            CATEGORY = "Efficiency Nodes/Image"

            def doit_ed(self, context, set_seed_cfg_sampler, bbox_detector, segm_detector_opt, sam_model_opt, sam_mode, 
                    guide_size, guide_size_for, 
                    max_size, seed, steps, cfg, sampler_name, scheduler, denoise, feather, noise_mask, force_inpaint,
                    bbox_threshold, bbox_dilation, bbox_crop_factor,
                    sam_detection_hint, sam_dilation, sam_threshold, sam_bbox_expansion, sam_mask_hint_threshold,
                    sam_mask_hint_use_negative, drop_size, wildcard="", image_opt=None, cycle=1,
                    detailer_hook=None, inpaint_model=False, noise_mask_feather=0, my_unique_id=None):
        
                _, model, clip, vae, positive, negative, image, c_seed, c_steps, c_cfg, c_sampler, c_scheduler = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative",  "images", "seed", "steps", "cfg", "sampler", "scheduler"])
        
                if image_opt is not None:       
                    image = image_opt
                    print(f"FaceDetailer ED: Using image_opt instead of context image.")
        
                if set_seed_cfg_sampler == "from context":
                    if c_seed is None:
                        raise Exception("FaceDetailer ED: No seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
                    else:
                        seed = c_seed
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                        if c_steps is not None:
                            steps = c_steps
                            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "steps", "type": "text", "data": steps})
                        cfg = c_cfg
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
                        sampler_name = c_sampler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "sampler_name", "type": "text", "data": sampler_name})
                        scheduler = c_scheduler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "scheduler", "type": "text", "data": scheduler})
                elif set_seed_cfg_sampler =="from node to ctx":
                    context = new_context_ed(context, seed=seed, cfg=cfg, sampler=sampler_name, scheduler=scheduler)      
        
                bbox_detector = detector_model(bbox_detector, "bbox")
                segm_detector_opt = detector_model(segm_detector_opt, "segm")
                sam_model_opt = load_sam_model(sam_model_opt, sam_mode)                
                
                result_img, result_cropped_enhanced, result_cropped_enhanced_alpha, result_mask, _, result_cnet_images = \
                    FaceDetailer().doit(image, model, clip, vae, guide_size, guide_size_for, max_size, 
                    seed, steps, cfg, sampler_name, scheduler, positive, negative, denoise, feather, noise_mask, force_inpaint,
                    bbox_threshold, bbox_dilation, bbox_crop_factor, sam_detection_hint, sam_dilation, 
                    sam_threshold, sam_bbox_expansion, sam_mask_hint_threshold,
                    sam_mask_hint_use_negative, drop_size, bbox_detector, wildcard, cycle=cycle,
                    sam_model_opt=sam_model_opt, segm_detector_opt=segm_detector_opt, detailer_hook=detailer_hook, 
                    inpaint_model=inpaint_model, noise_mask_feather=noise_mask_feather)

                context = new_context_ed(context, images=result_img) #RE 
                return (context, result_img, result_cropped_enhanced, result_cropped_enhanced_alpha, result_mask, result_cnet_images,)
            
        NODE_CLASS_MAPPINGS.update({"FaceDetailer 💬ED": FaceDetailer_ED})        

##################################                MaskDetailer_ED       ##################################
        
        # Mask Detailer ED
        class MaskDetailer_ED():
            @classmethod
            def INPUT_TYPES(s):
                return {"required": {
                            "context": ("RGTHREE_CONTEXT",),
                            "set_seed_cfg_sampler_batch": (list(KSampler_ED.set_seed_cfg_from.keys()), {"default": "from context"}),

                            "guide_size": ("FLOAT", {"default": 384, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                            "guide_size_for": ("BOOLEAN", {"default": True, "label_on": "mask bbox", "label_off": "crop region"}),
                            "max_size": ("FLOAT", {"default": 1024, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                            "mask_mode": ("BOOLEAN", {"default": True, "label_on": "masked only", "label_off": "whole"}),

                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                            "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                            "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                            "scheduler": (SCHEDULERS,),
                            "denoise": ("FLOAT", {"default": 0.5, "min": 0.0001, "max": 1.0, "step": 0.01}),

                            "feather": ("INT", {"default": 5, "min": 0, "max": 100, "step": 1}),
                            "crop_factor": ("FLOAT", {"default": 3.0, "min": 1.0, "max": 10, "step": 0.1}),
                            "drop_size": ("INT", {"min": 1, "max": MAX_RESOLUTION, "step": 1, "default": 10}),
                            "refiner_ratio": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                            "batch_size": ("INT", {"default": 1, "min": 1, "max": 100}),

                            "cycle": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                        },
                        "optional": {
                            "image_opt": ("IMAGE",),
                            "mask_opt": ("MASK", ),
                            "detailer_hook": ("DETAILER_HOOK",),
                            "inpaint_model": ("BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}),
                            "noise_mask_feather": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                        },
                        "hidden": {"my_unique_id": "UNIQUE_ID",},
                    }

            RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE", "IMAGE", "IMAGE", )
            RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE", "CROPPED_REFINED", "CROPPED_ENHANCED_ALPHA", )
            OUTPUT_IS_LIST = (False, False, True, True,)
            FUNCTION = "doit_ed"

            CATEGORY = "Efficiency Nodes/Image"

            def mask_sampling(image, mask, model, clip, vae, positive, negative, guide_size, guide_size_for, max_size, mask_mode,
                    seed, steps, cfg, sampler_name, scheduler, denoise,
                    feather, crop_factor, drop_size, refiner_ratio, batch_size, cycle, 
                    detailer_hook, inpaint_model, noise_mask_feather):
                
                basic_pipe = (model, clip, vae, positive, negative)
                
                enhanced_img_batch, cropped_enhanced_list, cropped_enhanced_alpha_list, _, _ = \
                    MaskDetailerPipe().doit(image, mask, basic_pipe, guide_size, guide_size_for, max_size, mask_mode,
                    seed, steps, cfg, sampler_name, scheduler, denoise, feather, crop_factor, drop_size, refiner_ratio, 
                    batch_size, cycle, None, detailer_hook, inpaint_model, noise_mask_feather)
                return (enhanced_img_batch, cropped_enhanced_list, cropped_enhanced_alpha_list)                
                
            def doit_ed(self, context, set_seed_cfg_sampler_batch, guide_size, guide_size_for, max_size, mask_mode,
                    seed, steps, cfg, sampler_name, scheduler, denoise,
                    feather, crop_factor, drop_size, refiner_ratio, batch_size, cycle=1,
                    image_opt=None, mask_opt=None, detailer_hook=None, inpaint_model=False, noise_mask_feather=0, my_unique_id=None):
        
                _, model, clip, vae, positive, negative, image, c_batch, c_seed, c_steps, c_cfg, c_sampler, c_scheduler, mask = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative",  "images", "step_refiner", "seed", "steps", "cfg", "sampler", "scheduler", "mask"])
        
                if image_opt is not None:
                    image = image_opt
                    print(f"MaskDetailer ED: Using image_opt instead of context image.")
                if mask_opt is not None:
                    mask = mask_opt
                    print(f"MaskDetailer ED: Using mask_opt instead of context mask.")
        
                if set_seed_cfg_sampler_batch == "from context":
                    if c_seed is None:
                        raise Exception("MaskDetailer ED: No seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
                    else:
                        seed = c_seed
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                        if c_steps is not None:
                            steps = c_steps
                            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "steps", "type": "text", "data": steps})
                        cfg = c_cfg
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
                        sampler_name = c_sampler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "sampler_name", "type": "text", "data": sampler_name})
                        scheduler = c_scheduler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "scheduler", "type": "text", "data": scheduler})
                        batch_size = c_batch
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "batch_size", "type": "text", "data": batch_size})
                elif set_seed_cfg_sampler =="from node to ctx":
                    context = new_context_ed(context, seed=seed, cfg=cfg, sampler=sampler_name, scheduler=scheduler)      
                
                enhanced_img_batch, cropped_enhanced_list, cropped_enhanced_alpha_list = \
                    MaskDetailer_ED.mask_sampling(image, mask, model, clip, vae, positive, negative,
                    guide_size, guide_size_for, max_size, mask_mode,
                    seed, steps, cfg, sampler_name, scheduler, denoise,
                    feather, crop_factor, drop_size, refiner_ratio, batch_size, cycle,
                    detailer_hook, inpaint_model, noise_mask_feather)

                context = new_context_ed(context, images=enhanced_img_batch) #RE 
                return (context, enhanced_img_batch, cropped_enhanced_list, cropped_enhanced_alpha_list,)

        NODE_CLASS_MAPPINGS.update({"MaskDetailer 💬ED": MaskDetailer_ED})

##################################                Detailer (SEGS) ED       ##################################

        # Detailer (SEGS) ED
        class DetailerForEach_ED():
            @classmethod
            def INPUT_TYPES(s):
                return {"required": {
                            "context": ("RGTHREE_CONTEXT",),
                            "segs": ("SEGS", ),
                            "set_seed_cfg_sampler": (list(KSampler_ED.set_seed_cfg_from.keys()), {"default": "from context"}),

                            "guide_size": ("FLOAT", {"default": 384, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                            "guide_size_for": ("BOOLEAN", {"default": True, "label_on": "mask bbox", "label_off": "crop region"}),
                            "max_size": ("FLOAT", {"default": 1024, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                            "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                            "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                            "scheduler": (SCHEDULERS,),
                            "denoise": ("FLOAT", {"default": 0.5, "min": 0.0001, "max": 1.0, "step": 0.01}),
                            "feather": ("INT", {"default": 5, "min": 0, "max": 100, "step": 1}),
                            
                            "noise_mask": ("BOOLEAN", {"default": True, "label_on": "enabled", "label_off": "disabled"}),
                            "force_inpaint": ("BOOLEAN", {"default": True, "label_on": "enabled", "label_off": "disabled"}),
                            "wildcard": ("STRING", {"multiline": True, "dynamicPrompts": False}),

                            "cycle": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                        },
                        "optional": {
                            "image_opt": ("IMAGE",),
                            "detailer_hook": ("DETAILER_HOOK",),
                            "inpaint_model": ("BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}),
                            "noise_mask_feather": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                        },
                        "hidden": {"my_unique_id": "UNIQUE_ID",},
                    }

            RETURN_TYPES = ("RGTHREE_CONTEXT", "SEGS", "IMAGE", "IMAGE", "IMAGE", "IMAGE", )
            RETURN_NAMES = ("CONTEXT", "SEGS", "OUTPUT_IMAGE", "CROPPED_REFINED", "CROPPED_REFINED_ALPHA", "CNET_IMAGES",)
            OUTPUT_IS_LIST = (False, False, False, True, True, True)
            
            FUNCTION = "doit_ed"

            CATEGORY = "Efficiency Nodes/Image"          
                
            def doit_ed(self, context, set_seed_cfg_sampler, segs, guide_size, guide_size_for, max_size, 
                    seed, steps, cfg, sampler_name, scheduler,
                    denoise, feather, noise_mask, force_inpaint, wildcard, cycle=1,
                    image_opt=None, detailer_hook=None, refiner_basic_pipe_opt=None,
                    inpaint_model=False, noise_mask_feather=0, my_unique_id=None):
                
                _, model, clip, vae, positive, negative, image, c_batch, c_seed, c_steps, c_cfg, c_sampler, c_scheduler, mask = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative",  "images", "step_refiner", "seed", "steps", "cfg", "sampler", "scheduler", "mask"])
        
                if image_opt is not None:
                    image = image_opt
                    print(f"Detailer (SEGS) ED: Using image_opt instead of context image.")
                
                if len(image) > 1:
                    raise Exception('[Impact Pack] ERROR: Detailer (SEGS) ED does not allow image batches.\nPlease refer to https://github.com/ltdrdata/ComfyUI-extension-tutorials/blob/Main/ComfyUI-Impact-Pack/tutorial/batching-detailer.md for more information.')
        
                if set_seed_cfg_sampler == "from context":
                    if c_seed is None:
                        raise Exception("Detailer (SEGS) ED: No seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
                    else:
                        seed = c_seed
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                        if c_steps is not None:
                            steps = c_steps
                            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "steps", "type": "text", "data": steps})
                        cfg = c_cfg
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
                        sampler_name = c_sampler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "sampler_name", "type": "text", "data": sampler_name})
                        scheduler = c_scheduler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "scheduler", "type": "text", "data": scheduler})
                elif set_seed_cfg_sampler =="from node to ctx":
                    context = new_context_ed(context, seed=seed, cfg=cfg, sampler=sampler_name, scheduler=scheduler)

                enhanced_img, _, cropped_enhanced, cropped_enhanced_alpha, cnet_pil_list = \
                    DetailerForEachDebug().doit(image, segs, model, clip, vae, guide_size, guide_size_for, 
                    max_size, seed, steps, cfg, sampler_name, scheduler, positive, negative, denoise,
                    feather, noise_mask, force_inpaint, wildcard, detailer_hook=detailer_hook,
                    cycle=cycle, inpaint_model=inpaint_model, noise_mask_feather=noise_mask_feather)
 
                context = new_context_ed(context, images=enhanced_img) #RE 
                return (context, segs, enhanced_img, cropped_enhanced, cropped_enhanced_alpha, cnet_pil_list,)

        NODE_CLASS_MAPPINGS.update({"Detailer (SEGS) 💬ED": DetailerForEach_ED})

        Impact_ed_loading_success = True        
        print(f"\r{message('Efficiency Nodes ED:')} {printout}{success('Success!')}")

    except Exception:
        print(f"\r{message('Efficiency Nodes ED:')} {printout}{error('Failed!')}")


###############
def load_upscale_model(model_name):
    cash = cashload_ed("ultimate_sd_upscaler", model_name)
    if cash is not None:
        return (cash)
    (model, ) = UpscaleModelLoader().load_model(model_name)
    cashsave_ed("ultimate_sd_upscaler", model_name, model, MAX_CASHE_ED_ULTIMATE_UPSCALE)
    return (model)


#=================================================================================#
##################################       UltimateSDUpscale ED       ##################################
MAX_CASHE_ED_ULTIMATE_UPSCALE = 1

if os.path.exists(os.path.join(custom_nodes_dir, "ComfyUI_UltimateSDUpscale")):
    printout = "Attempting to add 'UltimateSDUpscale ED' Node (UltimateSDUpscale add-on)..."
    print(f"{message('Efficiency Nodes ED:')} {printout}", end="")
    try:
        if "UltimateSDUpscale" in nodes_NODE_CLASS_MAPPINGS:
            UltimateSDUpscale = nodes_NODE_CLASS_MAPPINGS["UltimateSDUpscale"]
        else:
            raise Exception("'Ultimate SD Upscale' is not installed.")

        # Ultimate SD Upscale ED
        class UltimateSDUpscaleED():
            set_tile_size_from_what = {
                "Image size": 1,
                "Canvas size": 2,
                "Node setting": 3,
            }
            @classmethod
            def INPUT_TYPES(s):
                return {"required": 
                        {
                        "context": ("RGTHREE_CONTEXT",),
                        "set_seed_cfg_sampler": (list(KSampler_ED.set_seed_cfg_from.keys()), {"default": "from context"}),
                        "upscale_model": (folder_paths.get_filename_list("upscale_models"), ),
                        "upscale_by": ("FLOAT", {"default": 2, "min": 0.05, "max": 4, "step": 0.05}),
                        "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                        "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "step": 1}),
                        "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                        "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                        "scheduler": (SCHEDULERS,),                        
                        "denoise": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                        # Upscale Params
                        #"mode_type": (list(UltimateSDUpscaleED.MODES.keys()),),
                        "mode_type": UltimateSDUpscale().INPUT_TYPES()["required"]["mode_type"],
                        "set_tile_size_from": (list(UltimateSDUpscaleED.set_tile_size_from_what.keys()), {"default": "Image size"}),
                        "tile_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                        "tile_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
                        "mask_blur": ("INT", {"default": 8, "min": 0, "max": 64, "step": 1}),
                        "tile_padding": ("INT", {"default": 32, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                        # Seam fix params
                        #"seam_fix_mode": (list(UltimateSDUpscaleED.SEAM_FIX_MODES.keys()),),
                        "seam_fix_mode": UltimateSDUpscale().INPUT_TYPES()["required"]["seam_fix_mode"],
                        "seam_fix_denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                        "seam_fix_width": ("INT", {"default": 64, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                        "seam_fix_mask_blur": ("INT", {"default": 8, "min": 0, "max": 64, "step": 1}),
                        "seam_fix_padding": ("INT", {"default": 16, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                        # Misc
                        "force_uniform_tiles": ("BOOLEAN", {"default": True}),
                        "tiled_decode": ("BOOLEAN", {"default": False}),
                    },
                    "optional": {"image_opt": ("IMAGE",),},
                    "hidden": {"my_unique_id": "UNIQUE_ID",},}

            RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE", "IMAGE")
            RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE", "SOURCE_IMAGE")
            FUNCTION = "upscale_ed"
            CATEGORY = "Efficiency Nodes/Image"

            def upscale_ed(self, context, set_seed_cfg_sampler, upscale_model, upscale_by, 
                        seed, steps, cfg, sampler_name, scheduler, denoise, 
                        mode_type, set_tile_size_from, tile_width, tile_height, mask_blur, tile_padding,
                        seam_fix_mode, seam_fix_denoise, seam_fix_mask_blur,
                        seam_fix_width, seam_fix_padding, force_uniform_tiles, tiled_decode, image_opt=None, my_unique_id=None):
        
                _, model, clip, vae, positive, negative, image, c_seed, c_steps, c_cfg, c_sampler, c_scheduler = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative",  "images", "seed", "steps", "cfg", "sampler", "scheduler"])
                
                if image_opt is not None:
                    image = image_opt
                    print(f"UltimateSDUpscale ED: Using image_opt instead of context image.")
                if set_seed_cfg_sampler == "from context":
                    if c_seed is None:
                        raise Exception("UltimateSDUpscale ED: No seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
                    else:
                        seed = c_seed
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                        if c_steps is not None:
                            steps = c_steps
                            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "steps", "type": "text", "data": steps})
                        cfg = c_cfg
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
                        sampler_name = c_sampler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "sampler_name", "type": "text", "data": sampler_name})
                        scheduler = c_scheduler
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "scheduler", "type": "text", "data": scheduler})
                elif set_seed_cfg_sampler =="from node to ctx":
                    context = new_context_ed(context, seed=seed, cfg=cfg, sampler=sampler_name, scheduler=scheduler)
            
                if set_tile_size_from == "Image size":
                    _, tile_height, tile_width, _ = image.shape
                    PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "tile_width", "type": "text", "data": tile_width})
                    PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "tile_height", "type": "text", "data": tile_height})
                elif set_tile_size_from == "Canvas size":
                    _, tile_height, tile_width, _ = image.shape
                    tile_height = tile_height * upscale_by
                    tile_width = tile_width * upscale_by
                    PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "tile_width", "type": "text", "data": tile_width})
                    PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "tile_height", "type": "text", "data": tile_height})
                
                upscaler = load_upscale_model(upscale_model)        
                        
                tensor = UltimateSDUpscale().upscale(image, model, positive, negative, vae, upscale_by, seed,
                        steps, cfg, sampler_name, scheduler, denoise, upscaler,
                        mode_type, tile_width, tile_height, mask_blur, tile_padding,
                        seam_fix_mode, seam_fix_denoise, seam_fix_mask_blur,
                        seam_fix_width, seam_fix_padding, force_uniform_tiles, tiled_decode)[0]
                
                context = new_context_ed(context, images=tensor) #RE        
                return (context, tensor, image,)

        NODE_CLASS_MAPPINGS.update({"Ultimate SD Upscale 💬ED": UltimateSDUpscaleED})

        print(f"\r{message('Efficiency Nodes ED:')} {printout}{success('Success!')}")

    except Exception:
        print(f"\r{message('Efficiency Nodes ED:')} {printout}{error('Failed!')}")


#=================================================================================#
##################################       SUPIR Upscaler ED       ##################################

if os.path.exists(os.path.join(custom_nodes_dir, "ComfyUI-SUPIR")):
    printout = "Attempting to add 'SUPIR Upscaler ED' Node (SUPIR add-on)..."
    print(f"{message('Efficiency Nodes ED:')} {printout}", end="")
    try:
        if "SUPIR_model_loader_v2" in nodes_NODE_CLASS_MAPPINGS:
            SUPIR_model_loader_v2 = nodes_NODE_CLASS_MAPPINGS["SUPIR_model_loader_v2"]
            SUPIR_first_stage = nodes_NODE_CLASS_MAPPINGS["SUPIR_first_stage"]
            SUPIR_encode = nodes_NODE_CLASS_MAPPINGS["SUPIR_encode"]
            SUPIR_decode = nodes_NODE_CLASS_MAPPINGS["SUPIR_decode"]
            SUPIR_conditioner = nodes_NODE_CLASS_MAPPINGS["SUPIR_conditioner"]
            SUPIR_sample = nodes_NODE_CLASS_MAPPINGS["SUPIR_sample"]
        else:
            raise Exception("'SUPIR' is not installed.")        
        
#######################################################################################################
        # SUPIR model loader ED
        class SUPIR_Model_Loader_ED:
            @classmethod
            def INPUT_TYPES(s):
                return {"required": {
                    "context": ("RGTHREE_CONTEXT",),
                    "upscale_model": (["🚫 Do not upscale"] + folder_paths.get_filename_list("upscale_models"), ),
                    "upscale_by": ("FLOAT", {"default": 2, "min": 0.05, "max": 4, "step": 0.05}),
                    "rescale_method": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],),
                    "supir_model": (folder_paths.get_filename_list("checkpoints"),),
                    "fp8_unet": ("BOOLEAN", {"default": False}),
                    "diffusion_dtype": (['fp16', 'bf16', 'fp32', 'auto'], {"default": 'auto'}),
                    },
                    "optional": {
                        "high_vram": ("BOOLEAN", {"default": False}),
                    }
                }
        
            RETURN_TYPES = ("RGTHREE_CONTEXT", "SUPIRMODEL", "SUPIRVAE", "IMAGE")
            RETURN_NAMES = ("CONTEXT", "SUPIR_MODEL","SUPIR_VAE", "UPSCALED_IMAGE")
            FUNCTION = "process_ed"
            CATEGORY = "Efficiency Nodes/Loaders"
            DESCRIPTION = """
Loads the SUPIR model and merges it with the SDXL model.  

Diffusion type should be kept on auto, unless you have issues loading the model.  
fp8_unet casts the unet weights to torch.float8_e4m3fn, which saves a lot of VRAM but has slight quality impact.  
high_vram: uses Accelerate to load weights to GPU, slightly faster model loading.
"""
        
            def upscale(upscale_model, image, upscale_by, rescale_method):
                samples = image.movedim(-1,1)
                width = round(samples.shape[3])
                height = round(samples.shape[2])
                target_width = round(samples.shape[3] * upscale_by)
                target_height = round(samples.shape[2] * upscale_by)
                samples = ImageUpscaleWithModel().upscale(upscale_model, image)[0].movedim(-1,1)

                upscaled_width = round(samples.shape[3])
                upscaled_height = round(samples.shape[2])

                if upscaled_width != target_width or upscaled_height != target_height:
                    samples = comfy.utils.common_upscale(samples, target_width, target_height, rescale_method, "disabled")
            
                samples = samples.movedim(1,-1)
                return (samples)
        
            def process_ed(self, context, upscale_model, upscale_by, rescale_method, supir_model, diffusion_dtype, fp8_unet, high_vram=False):
                
                _, model, clip, vae, image = context_2_tuple_ed(context,["model", "clip", "vae", "images"])
                
                if upscale_model != "🚫 Do not upscale":
                    upscaler = load_upscale_model(upscale_model)
                    upscaled_image = SUPIR_Model_Loader_ED.upscale(upscaler, image, upscale_by, rescale_method)
                else:
                    upscaled_image = image
                
                
                (sup_model, sup_vae) = SUPIR_model_loader_v2().process(supir_model, diffusion_dtype, fp8_unet, model, clip, vae, high_vram=False)
                return (context, sup_model, sup_vae, upscaled_image)       

        NODE_CLASS_MAPPINGS.update({"SUPIR model loader 💬ED": SUPIR_Model_Loader_ED})
        
#####################################################################################################
        # SUPIR Sampler ED
        class SUPIR_Sampler_ED():
            @classmethod
            def INPUT_TYPES(s):
                return {"required": 
                        {
                        "context": ("RGTHREE_CONTEXT",),
                        "SUPIR_model": ("SUPIRMODEL",),
                        "SUPIR_vae": ("SUPIRVAE",),                        
                        "set_seed_cfg_sampler": (list(KSampler_ED.set_seed_cfg_from.keys()), {"default": "from context"}),
                        "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                        "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "step": 1}),
                        "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                        "EDM_s_churn": ("INT", {"default": 5, "min": 0, "max": 40, "step": 1}),
                        "s_noise": ("FLOAT", {"default": 1.003, "min": 1.0, "max": 1.1, "step": 0.001}),
                        "DPMPP_eta": ("FLOAT", {"default": 1.0, "min": 0, "max": 10.0, "step": 0.01}),
                        "control_scale_start": ("FLOAT", {"default": 1.0, "min": 0, "max": 10.0, "step": 0.01}),
                        "control_scale_end": ("FLOAT", {"default": 1.0, "min": 0, "max": 10.0, "step": 0.01}),
                        "restore_cfg": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 20.0, "step": 0.01}),
                        "keep_model_loaded": ("BOOLEAN", {"default": False}),
                        "sampler": (['RestoreDPMPP2MSampler', 'RestoreEDMSampler', 'TiledRestoreDPMPP2MSampler',
                                         'TiledRestoreEDMSampler',], {"default": 'RestoreEDMSampler' }),
                        "use_tiled_vae": ("BOOLEAN", {"default": True}),
                        "vae_tile_size": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 64}),
                        #"decoder_tile_size": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 64}),
                        "encoder_dtype": (['bf16', 'fp32', 'auto' ], {"default": 'auto'}),
                    },
                    "optional": {
                        "image_opt": ("IMAGE",),
                        "sampler_tile_size": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 32}),
                        "sampler_tile_stride": ("INT", {"default": 512, "min": 32, "max": 2048, "step": 32}),
                    },
                    "hidden": {"my_unique_id": "UNIQUE_ID",},}

            RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE", "IMAGE")
            RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE", "SOURCE_IMAGE")
            FUNCTION = "process_ed"
            CATEGORY = "Efficiency Nodes/Image"
            DESCRIPTION = """
- **latent:**
Latent to sample from, when using SUPIR latent this is just for the noise shape,  
it's actually not used otherwise here. Identical to feeding this comfy empty latent.  
If fed anything else it's used as it is, no noise is added.  
- **cfg:**
Linearly scaled CFG is always used, first step will use the cfg_scale_start value,  
and that is interpolated to the cfg_scale_end value at last step.  
To disable scaling set these values to be the same.  
- **EDM_s_churn:**
controls the rate of adaptation of the diffusion process to changes in noise levels  
over time. Has no effect with DPMPP samplers.  
- **s_noise:**
This parameter directly controls the amount of noise added to the image at each  
step of the diffusion process.  
- **DPMPP_eta:**
Scaling factor that influences the diffusion process by adjusting how the denoising  
process adapts to changes in noise levels over time.
No effect with EDM samplers.  
- **control_scale:**
The strenght of the SUPIR control model, scales linearly from start to end.  
Lower values allow more freedom from the input image.  
- **restore_cfg:**
Controls the degree of restoration towards the original image during the diffusion   
process. It allows for dome fine-tuning of the process.  
- **samplers:**
EDM samplers need lots of steps but generally have better quality.  
DPMPP samplers work well with lower steps, good for lightning models.  
Tiled samplers enable tiled diffusion process, this is very slow but allows higher  
resolutions to be used by saving VRAM.  Tile size should be chosen so the image  
is evenly tiled.  Tile stride affects the overlap of the tiles.  Check the  
SUPIR Tiles -node for preview to understand how the image is tiled.

"""
  
            def process_ed(self, context, SUPIR_model, SUPIR_vae, set_seed_cfg_sampler, seed, steps, cfg, EDM_s_churn, s_noise, DPMPP_eta, control_scale_start, control_scale_end, restore_cfg, keep_model_loaded, sampler,
            use_tiled_vae, vae_tile_size, encoder_dtype, image_opt=None, sampler_tile_size=1024, sampler_tile_stride=512, my_unique_id=None):            
            
                _, positive_prompt, negative_prompt, source_image, c_seed, c_steps, c_cfg = context_2_tuple_ed(context,["text_pos_g", "text_neg_g",  "images", "seed", "steps", "cfg"])
                
                if image_opt is None:
                    image_opt = source_image
                
                if set_seed_cfg_sampler == "from context":
                    if c_seed is None:
                        raise Exception("UltimateSDUpscale ED: No seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
                    else:
                        seed = c_seed
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                        if c_steps is not None:
                            steps = c_steps
                            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "steps", "type": "text", "data": steps})
                        cfg = c_cfg
                        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
                elif set_seed_cfg_sampler =="from node to ctx":
                    context = new_context_ed(context, seed=seed, cfg=cfg)
            
                # SUPIR_first_stage
                (SUPIR_vae2, denoised_image, denoised_latent,) = SUPIR_first_stage().process(SUPIR_vae, image_opt, encoder_dtype, use_tiled_vae, vae_tile_size, vae_tile_size)
            
                # SUPIR_conditioner
                (positive_encoded, negative_encoded,) = SUPIR_conditioner().condition(SUPIR_model, denoised_latent, positive_prompt, negative_prompt, captions="")
            
                # SUPIR_encode
                SUPIR_latent = SUPIR_encode().encode(SUPIR_vae2, denoised_image, encoder_dtype, use_tiled_vae, vae_tile_size)[0]
            
                # SUPIR_sample
                SUPIR_latent = SUPIR_sample().sample(SUPIR_model, SUPIR_latent, steps, seed, cfg, EDM_s_churn, s_noise, positive_encoded,
                negative_encoded, cfg, control_scale_start, control_scale_end, restore_cfg, keep_model_loaded, DPMPP_eta,
                sampler, sampler_tile_size=1024, sampler_tile_stride=512)[0]
                
                # SUPIR_decode
                output_image = SUPIR_decode().decode(SUPIR_vae, SUPIR_latent, use_tiled_vae, vae_tile_size)[0]
                context = new_context_ed(context, images=output_image)
                
                return (context, output_image, source_image)

        NODE_CLASS_MAPPINGS.update({"SUPIR Sampler 💬ED": SUPIR_Sampler_ED})
        print(f"\r{message('Efficiency Nodes ED:')} {printout}{success('Success!')}")

    except Exception:
        print(f"\r{message('Efficiency Nodes ED:')} {printout}{error('Failed!')}")


#############################################################################################################