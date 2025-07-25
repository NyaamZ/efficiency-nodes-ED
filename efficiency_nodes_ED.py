# Efficiency Nodes ExtendeD - Expansion of Efficiency Nodes for ComfyUI. Significant UX improvements.
# by NyaamZ - 2023 - 2025
# https://github.com/NyaamZ/efficiency-nodes-ED

# 00b4e6d4-922e-4a3b-943e-33a467587fe1

import os
import sys
import re
import nodes

from pathlib import Path #For embedding stacker ED
from functools import reduce # For regional ED

# Get the absolute path of various directories
my_dir = os.path.dirname(os.path.abspath(__file__))
custom_nodes_dir = os.path.abspath(os.path.join(my_dir, '..'))
efficiency_nodes_dir = os.path.abspath(os.path.join(custom_nodes_dir, 'efficiency-nodes-comfyui'))
comfy_dir = os.path.abspath(os.path.join(my_dir, '..', '..'))

# Append comfy_dir to sys.path & import files
sys.path.append(comfy_dir)
from comfy_extras.nodes_upscale_model import UpscaleModelLoader, ImageUpscaleWithModel
from comfy_extras.nodes_rebatch import LatentRebatch
from server import PromptServer

import comfy.sd
import comfy.utils

sys.path.remove(comfy_dir)

sys.path.append(efficiency_nodes_dir)
from tsc_utils import *
sys.path.remove(efficiency_nodes_dir)

# Append custom_nodes_dir to sys.path
sys.path.append(custom_nodes_dir)

NODES = nodes.NODE_CLASS_MAPPINGS
SCHEDULERS = comfy.samplers.KSampler.SCHEDULERS + ["AYS SD1", "AYS SDXL", "AYS SVD", "GITS"]

##############################################################################################################
##############################################################################################################
#                                                                                                   ED                                                                                                                #
##############################################################################################################
##############################################################################################################


##############################################################################################################
# ED rgthree Context
_all_ed_context_input_output_data = {
  "base_ctx": ("base_ctx", "RGTHREE_CONTEXT", "CONTEXT"),
  "model": ("model", "MODEL", "MODEL"),
  "clip": ("clip", "CLIP", "CLIP"),
  "vae": ("vae", "VAE", "VAE"),
  "positive": ("positive", "CONDITIONING", "POSITIVE"),
  "negative": ("negative", "CONDITIONING", "NEGATIVE"),
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
  "clip_encoder": ("clip_encoder", "CLIP_ENCODER", "CLIP_ENCODER"),
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

##############################################################################################################
# CASHE
cashe_ed = {
    "ultra_bbox_detector": [],
    "ultra_segm_detector": [],
    "sam_model": [],
    "upscaler": []
}
MAX_CASHE_UPSCALER = 2
MAX_CASHE_ULTRALYTICS = 2

class ED_Cashe:
    @staticmethod
    def cashload(cashe_type, model_name):
        global cashe_ed
        for entry in cashe_ed[cashe_type]:
            if entry[0] == model_name:
                print(f"\r{message('Efficiency Nodes ED:')} using saved {cashe_type} cashe - {entry[0]}")
                return entry[1]
        return None
        
    @staticmethod
    def cashsave(cashe_type, model_name, model, max_cashe):
        global cashe_ed
        if len(cashe_ed[cashe_type])>= max_cashe:
            cashe_ed[cashe_type].pop(0)
        cashe_ed[cashe_type].append([model_name, model])
        print(f"\r{message('Efficiency Nodes ED:')} save {cashe_type} cashe - {model_name}")
        return

############################################################################################################
# UTILS
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

class ED_Util:
    any_typ = AnyType("*")

    @staticmethod
    def try_install_custom_node(extension_name, custom_node_url):
        msg = f"To use this node, '{extension_name}' extension is required."
        
        try:
            import cm_global
            cm_global.try_call(api='cm.try-install-custom-node',
                               sender="Efficiency Nodes 💬ED", custom_node_url=custom_node_url, msg=msg)
        except Exception as e:
            print(msg)
            print(f"Efficiency Nodes ED - ComfyUI-Manager is outdated. The custom node installation feature is not available.")
            
        raise Exception(f"[ERROR] To use this node, you need to install '{extension_name}'")

    @staticmethod
    def get_image_size(image):
        samples = image.movedim(-1, 1)
        size = samples.shape[3], samples.shape[2]
        return size

    @staticmethod
    def get_latent_size(latent, ORIGINAL_VALUES=False):
        lc = latent.copy()
        size = lc["samples"].shape[3], lc["samples"].shape[2]
        if ORIGINAL_VALUES == False:
            size = size[0] * 8, size[1] * 8
        return size

    @staticmethod
    def apply_load_lora(lora_stack, ckpt, clip, show_node=""):
        lora_params = []
        lora_params.extend(lora_stack)
        
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
        
        if show_node:
            print(f"\033[36m{show_node} - Lora load(Not use cashe):\033[0m")
        print(f"Lora:")
        lora_count = 0
        
        # Unpack lora parameters from the first element of the list for now
        lora_name, strength_model, strength_clip = lora_params[0]
        lora_model, lora_clip = recursive_load_lora(lora_params, ckpt, clip, folder_paths, lora_count)

        return lora_model, lora_clip
        
    @staticmethod
    def strip_comments(text):
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " " # note: a space and not an empty string
            else:
                return s
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        return re.sub(pattern, replacer, text)

    @staticmethod
    def vae_encode(vae, pixels, is_tiled = False, tile_size = 512):
        if is_tiled:
            latent = nodes.VAEEncodeTiled().encode(vae, pixels, tile_size=tile_size, overlap=64, temporal_size=64, temporal_overlap=8)[0]
            print(f"\r{message('Efficient Nodes ED:')} use tiled VAE encode (tile size:{tile_size})")
        else:
            latent = nodes.VAEEncode().encode(vae, pixels)[0]
        return latent

    @staticmethod
    def vae_decode(vae, latent, is_tiled = False, tile_size = 512):
        if is_tiled:
            images = nodes.VAEDecodeTiled().decode(vae, latent, tile_size)[0]
            print(f"\r{message('Efficient Nodes ED:')} use tiled VAE decode (tile size:{tile_size})")
        else:
            images = nodes.VAEDecode().decode(vae, latent)[0]
        return images

    @staticmethod
    def ultra_detector_model(model_name, type):    
        detector_type = "ultra_" + type + "_detector"
        if model_name is None or model_name == "None":
            return None                
        cash = ED_Cashe.cashload(detector_type, model_name)
        if cash is not None:
            return cash
        
        if 'UltralyticsDetectorProvider' not in NODES:
            ED_Util.try_install_custom_node('ComfyUI Impact Subpack', 'https://github.com/ltdrdata/ComfyUI-Impact-Subpack')
        
        if type == "bbox":
            model = NODES['UltralyticsDetectorProvider']().doit(model_name)[0]
        else:
            model = NODES['UltralyticsDetectorProvider']().doit(model_name)[1]
        ED_Cashe.cashsave(detector_type, model_name, model, MAX_CASHE_ULTRALYTICS)
        return model

    @staticmethod
    def load_sam_model(model_name, device_mode):
        if model_name == "None" or model_name is None:                
            return None
        cash = ED_Cashe.cashload("sam_model", model_name)
        if cash is not None:
            return cash

        if 'SAMLoader' not in NODES:
            ED_Util.try_install_custom_node('ComfyUI Impact Subpack', 'https://github.com/ltdrdata/ComfyUI-Impact-Subpack')

        sam = NODES['SAMLoader']().load_model(model_name, device_mode)[0]
        ED_Cashe.cashsave("sam_model", model_name, sam, MAX_CASHE_ULTRALYTICS)
        return sam

    @staticmethod
    def load_upscale_model(model_name):
        cash = ED_Cashe.cashload("upscaler", model_name)
        if cash is not None:
            return cash
        model = UpscaleModelLoader().load_model(model_name)[0]
        ED_Cashe.cashsave("upscaler", model_name, model, MAX_CASHE_UPSCALER)
        return model

    @staticmethod
    def get_widget_value(prompt, node, widget_name):
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
        
        if node is not None and node["mode"] == 0:
            values = prompt[str(node["id"])]
            if "inputs" in values:
                if widget_name in values["inputs"]:
                    value = values["inputs"][widget_name]
                    if isinstance(value, list):
                        raise ValueError("Converted widgets are not supported via named reference, use the inputs instead.")
                    return value
            
        return None

    #@staticmethod
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

class wildcard_ED:
    wildcards_dir = os.path.abspath(os.path.join(custom_nodes_dir, "ComfyUI-Impact-Pack/wildcards"))
    
    @staticmethod
    def sq_wildcard(text, iterate_count):
        def read_wildcard(match, card_name, operation, counter, iterate_count):
            file_path = os.path.join(wildcard_ED.wildcards_dir, f"{card_name}.txt")
            
            if not os.path.isfile(file_path):
                raise Exception(f"Efficient nodes ED: wildcard file ({card_name}.txt) is not found.")

            with open(file_path, "r") as file:
                lines = file.readlines()

            counter = max(0, min(counter, len(lines) - 1))

            if operation == "ASC":
                counter = min(counter + iterate_count, len(lines) - 1)
            elif operation == "DSC":
                counter = max(counter - iterate_count, 0)
            else:
                operation = "FIX"

            result = lines[counter].strip()
            match_after = f"__{card_name}__#{operation}{counter}"

            print(f"     {match} >> {message('counter:')}: {warning('#' + operation + str(counter))}, {message('replaced text:')} {warning(result)}")
            return result, match_after

        global get_booru_tag_id, get_booru_tag_text_b
        text_b = get_booru_tag_text_b

        card_files, _ = folder_paths.recursive_search(wildcard_ED.wildcards_dir)

        pattern = r"(__[\w.\-+/*\\]+?__#[A-Z]{3}[0-9]*)"
        matches = re.findall(pattern, text)

        if matches:
            print(f"\r{message('Efficient nodes ED:')} sequential wildcards processing -")

            for match in matches:
                card_name, operation_counter = match.split('__#')
                card_name = card_name[2:]
                operation, counter = operation_counter[:3], int(operation_counter[3:])

                if card_name.replace('/', '\\') + ".txt" in card_files:
                    wc_text, match_after = read_wildcard(match, card_name, operation, counter, iterate_count)
                    text_b = text_b.replace(match, match_after)
                else:
                    raise Exception(f"Efficient nodes ED: wildcard file ({match}) is not found.")

                text = text.replace(match, wc_text)

            PromptServer.instance.send_sync("ed-node-feedback", {
                "node_id": get_booru_tag_id,
                "widget_name": "text_b",
                "type": "text",
                "data": text_b
            })

        return text

    @staticmethod
    def process(text, seed, iterate_count=0):
        text = wildcard_ED.sq_wildcard(text, iterate_count)

        if 'ImpactWildcardProcessor' not in NODES:
            ED_Util.try_install_custom_node('ComfyUI Impact Pack', 'https://github.com/ltdrdata/ComfyUI-Impact-Pack')

        return NODES['ImpactWildcardProcessor'].process(text=text, seed=seed)

class BNK_EncoderWrapper:
    
    def __init__(self, token_normalization, weight_interpretation):
        self.token_normalization = token_normalization
        self.weight_interpretation = weight_interpretation

    def encode(self, clip, text):
        if 'BNK_CLIPTextEncodeAdvanced' not in NODES:
            ED_Util.try_install_custom_node('Advanced CLIP Text Encode', 'https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb')

        return NODES['BNK_CLIPTextEncodeAdvanced']().encode(clip, text, self.token_normalization, self.weight_interpretation)

    @staticmethod
    def imp_encode(text, clip, clip_encoder=None):        
        if clip_encoder is None:
            return nodes.CLIPTextEncode().encode(clip, text)[0]
        else:
            return clip_encoder.encode(clip, text)[0]

##############################################################################################################
# LoRA Stacker ED
class LoRA_Stacker_ED:
    MODES = ["simple", "advanced"]
    MAX_LORA_COUNT = 9
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "input_mode": (cls.MODES,),
                "lora_count": ("INT", {"default": 3, "min": 0, "max": cls.MAX_LORA_COUNT, "step": 1}),
            }
        }        

        for i in range(1, cls.MAX_LORA_COUNT +1):
            inputs["required"][f"lora_name_{i}"] = (["None"] + folder_paths.get_filename_list("loras"),)
            inputs["required"][f"lora_wt_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"model_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})
            inputs["required"][f"clip_str_{i}"] = ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01})        

        inputs["optional"] = {
            "lora_stack": ("LORA_STACK",),
            "Clear LoRAs": (["Clear LoRAs"], ),
        }
        return inputs

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("LORA_STACK",)
    FUNCTION = "lora_stacker_ed"
    CATEGORY = "Efficiency Nodes/Stackers"

    def lora_stacker_ed(self, input_mode, lora_count, lora_stack=None, **kwargs):
        if lora_count > 0:
            # Extract values from kwargs
            loras = [kwargs.get(f"lora_name_{i}") for i in range(1, lora_count + 1)]

            # Create a list of tuples using provided parameters, exclude tuples with lora_name as "None"
            if input_mode == "simple":
                weights = [kwargs.get(f"lora_wt_{i}") for i in range(1, lora_count + 1)]
                loras = [(lora_name, lora_weight, lora_weight) for lora_name, lora_weight in zip(loras, weights) if lora_name != "None" and lora_weight != 0]
            else:
                model_strs = [kwargs.get(f"model_str_{i}") for i in range(1, lora_count + 1)]
                clip_strs = [kwargs.get(f"clip_str_{i}") for i in range(1, lora_count + 1)]
                loras = [(lora_name, model_str, clip_str) for lora_name, model_str, clip_str in zip(loras, model_strs, clip_strs) if lora_name != "None" and model_str != 0]
        else:
            loras = []
        
        # If lora_stack is not None, extend the loras list with lora_stack
        if lora_stack is not None:
            loras.extend([l for l in lora_stack if l[0] != "None"])
        #print(f"\033[36mloras:{(loras,)}\033[0m") 
        return (loras,)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return_value = True
        names = ["None"] + folder_paths.get_filename_list("loras")

        if kwargs['lora_count'] > 0:
            for i in range(1, cls.MAX_LORA_COUNT +1):                
                name = kwargs[f"lora_name_{i}"]
                if not name in names:
                    return_value = f"Lora not found: {name}"
                    raise Exception(f"\033[30m \033[101mLoRA Stacker ED: LoRA '{name}' is not found\033[0m")
                    break
        
        return return_value

##############################################################################################################
# Embedding Stacker ED
class Embedding_Stacker_ED:
    MAX_EMBEDDING_COUNT = 9
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "positive_embeddings_count": ("INT", {"default": 1, "min": 0, "max": cls.MAX_EMBEDDING_COUNT, "step": 1}),
                "negative_embeddings_count": ("INT", {"default": 3, "min": 0, "max": cls.MAX_EMBEDDING_COUNT, "step": 1}),
            }
        }
        
        for i in range(1, cls.MAX_EMBEDDING_COUNT +1):
            inputs["required"][f"positive_embedding_{i}"] = (["None"] + folder_paths.get_filename_list("embeddings"),)
            inputs["required"][f"positive_emphasis_{i}"] = ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.05})
        for i in range(1, cls.MAX_EMBEDDING_COUNT +1):
            inputs["required"][f"negative_embedding_{i}"] = (["None"] + folder_paths.get_filename_list("embeddings"),)
            inputs["required"][f"negative_emphasis_{i}"] = ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.05})

        inputs["optional"] = {
            "lora_stack": ("LORA_STACK",),
            "Clear embeddings": (["Clear embeddings"], ),
        }
        return inputs

    RETURN_TYPES = ("LORA_STACK",)
    RETURN_NAMES = ("LORA_STACK",)
    FUNCTION = "embedding_stacker"
    CATEGORY = "Efficiency Nodes/Stackers"

    def embedding_stacker(self, positive_embeddings_count, negative_embeddings_count, lora_stack=None, **kwargs):
        # POSITIVE EMBEDDING
        if positive_embeddings_count > 0:            
            # Extract values from kwargs
            pos_embs = [kwargs.get(f"positive_embedding_{i}") for i in range(1, positive_embeddings_count + 1)]
            # Create a list of tuples using provided parameters, exclude tuples with lora_name as "None"
            pos_emps = [kwargs.get(f"positive_emphasis_{i}") for i in range(1, positive_embeddings_count + 1)]
            pos_embs = [("POS_EMBEDDING", pos_emb, round(pos_emp, 2)) for pos_emb, pos_emp in zip(pos_embs, pos_emps) if pos_emb != "None" and pos_emp != 0]
        else:
            pos_embs = []
        
        # NEGTIVE EMBEDDING
        if negative_embeddings_count > 0:
            # Extract values from kwargs
            neg_embs = [kwargs.get(f"negative_embedding_{i}") for i in range(1, negative_embeddings_count + 1)]
            # Create a list of tuples using provided parameters, exclude tuples with lora_name as "None"
            neg_emps = [kwargs.get(f"negative_emphasis_{i}") for i in range(1, negative_embeddings_count + 1)]
            neg_embs = [("NEG_EMBEDDING", neg_emb, round(neg_emp, 2)) for neg_emb, neg_emp in zip(neg_embs, neg_emps) if neg_emb != "None" and neg_emp != 0]
        else:
            neg_embs = []
        
        loras = pos_embs + neg_embs        
        # If lora_stack is not None, extend the loras list with lora_stack
        if lora_stack is not None:
            loras.extend([l for l in lora_stack if l[0] != "None"])
        #print(f"\033[36mlorasEmbedding:{(loras,)}\033[0m") 
        return (loras,)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return_value = True
        names = ["None"] + folder_paths.get_filename_list("embeddings")

        if kwargs['positive_embeddings_count'] > 0:
            for i in range(1, cls.MAX_EMBEDDING_COUNT +1):                
                name = kwargs[f"positive_embedding_{i}"]
                if not name in names:
                    return_value = f"Embedding not found: {name}"
                    raise Exception(f"\033[30m \033[101mEmbedding Stacker ED: embedding '{name}' is not found\033[0m")
                    break
                    
        if kwargs['negative_embeddings_count'] > 0:
            for i in range(1, cls.MAX_EMBEDDING_COUNT +1):                
                name = kwargs[f"negative_embedding_{i}"]
                if not name in names:
                    return_value = f"Embedding not found: {name}"
                    raise Exception(f"\033[30m \033[101mEmbedding Stacker ED: embedding '{name}' is not found\033[0m")
                    break
        
        return return_value

    @staticmethod
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
                emb = "embedding:" + os.path.splitext(entry[1])[0]
                if entry[2] != 1:
                    emb = f"({emb}:{entry[2]})"
                pos = f"{positive.rstrip(' ,')}, {emb},"
                positive = pos
                if positive_refiner is not None:
                    pos_refiner = f"{positive_refiner.rstrip(' ,')}, {emb},"
                    positive_refiner = pos_refiner
            elif entry[0] == "NEG_EMBEDDING":
                emb = "embedding:" + os.path.splitext(entry[1])[0]    
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

##############################################################################################################
# Wildcard Encode ED
list_counter_map = {}
class WildcardEncode_ED:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"context": ("RGTHREE_CONTEXT",), },
                    "optional": {     
                                "model": ("MODEL",),
                                "clip": ("CLIP",),
                                "vae": ("VAE",),
                                "positive": ("CONDITIONING",),
                                "negative": ("CONDITIONING",),
                                "latent": ("LATENT",),
                                "images": ("IMAGE",),
                                "signal": (ED_Util.any_typ,),
                    },
                    "hidden": {"unique_id": "UNIQUE_ID"},
                    }

    RETURN_TYPES = ("RGTHREE_CONTEXT", "MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING", "LATENT", "IMAGE", "STRING",)
    RETURN_NAMES = ("CONTEXT", "MODEL", "CLIP", "VAE", "POSITIVE" ,"NEGATIVE", "LATENT", "IMAGE", "TEXT_POS",)
    FUNCTION = "wildcard_encode"
    CATEGORY = "Efficiency Nodes/Prompt"

    def wildcard_encode(self, context=None, signal=None, unique_id=None, **kwargs):
        ctx = new_context_ed(context, **kwargs)  
    
        _, model, clip, vae, positive, negative, latent, images, seed, batch_size, pos_prompt, lora_stack, clip_encoder = context_2_tuple_ed(ctx,["model", "clip", "vae", "positive", "negative", "latent", "images", "seed", "step_refiner", "text_pos_g", "lora_stack", "clip_encoder"])
        
        if pos_prompt:        
            #Process wildcard
            if unique_id not in list_counter_map:
                count = 0
            else:
                count = list_counter_map[unique_id]
            list_counter_map[unique_id] = count + 1
            
            if batch_size > 1:
                seed += count
            
            if not positive:
                pos_prompt = wildcard_ED.process(pos_prompt, seed, count)
                positive = BNK_EncoderWrapper.imp_encode(pos_prompt, clip, clip_encoder)
        
        if lora_stack:
            model, clip = ED_Util.apply_load_lora(lora_stack, model, clip, "Wildcard Encode ED")
            lora_stack = None

        ctx = new_context_ed(ctx, model=model, clip=clip, vae=vae, positive=positive, negative=negative, latent=latent, images=images, seed=seed, text_pos_g=pos_prompt)
        return (ctx, model, clip, vae, positive, negative, latent, images, pos_prompt,)

###############################################################################################################
# Efficient Loader ED    
class EfficientLoader_ED():
    @classmethod
    def INPUT_TYPES(cls):
        paint_mode = {
            "✍️ Txt2Img": 1,
            "🦱 Img2Img": 2,
            "🎨 Inpaint(Ksampler)": 3,
            "🎨 Inpaint(MaskDetailer)": 4,
        }
        inputs = {"required": { "ckpt_name": (["🔌 model_opt input"] + folder_paths.get_filename_list("checkpoints"),),
                              "vae_name": (["Baked VAE"] + folder_paths.get_filename_list("vae"),),
                              "clip_skip": ("INT", {"default": -2, "min": -24, "max": 0, "step": 1}),                        
                              "paint_mode": ( list(paint_mode.keys()), {"default": "✍️ Txt2Img"}),
                              "batch_size": ("INT", {"default": 1, "min": 1, "max": 262144}),
                              "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                              "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                              "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                              "scheduler": (SCHEDULERS,),
                              #"positive": ("STRING", {"default": "","multiline": True, "dynamicPrompts": True}),
                              #"negative": ("STRING", {"default": "", "multiline": True, "dynamicPrompts": True}),
                              "image_width": ("INT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 1}),
                              "image_height": ("INT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 1}),
                              },
                "optional": {
                             "lora_stack": ("LORA_STACK",),
                             "cnet_stack": ("CONTROL_NET_STACK",),
                             "pixels": ("IMAGE",),
                             "mask": ("MASK",),
                             "model_opt": ("MODEL",),
                             "clip_opt": ("CLIP",),
                             "positive": ("STRING", {"forceInput": True}),                             
                             "negative": ("STRING", {"forceInput": True}),},
                "hidden": { "prompt": "PROMPT",
                            "my_unique_id": "UNIQUE_ID",
                            "extra_pnginfo": "EXTRA_PNGINFO",}
                }
        return inputs

    RETURN_TYPES = ("RGTHREE_CONTEXT", "MODEL", "CONDITIONING", "CONDITIONING", "LATENT", "IMAGE", "CLIP", "DEPENDENCIES",)
    RETURN_NAMES = ("CONTEXT", "MODEL", "POSITIVE", "NEGATIVE", "LATENT", "IMAGE", "CLIP", "DEPENDENCIES",)
    OUTPUT_IS_LIST = (False, False, False, False, True, False, False, False,)
    FUNCTION = "efficientloader_ed"
    CATEGORY = "Efficiency Nodes/Loaders"
        
    def efficientloader_ed(self, ckpt_name, vae_name, clip_skip, paint_mode, batch_size, 
                        seed, cfg, sampler_name, scheduler, image_width, image_height, lora_stack=None, cnet_stack=None,
                        pixels=None, mask=None, model_opt=None, clip_opt=None, positive="", negative="",
                        refiner_name="None", positive_refiner=None, negative_refiner=None, ascore=None, prompt=None,
                        my_unique_id=None, extra_pnginfo=None, loader_type="regular"):
        
        global loaded_objects
        
        # Clean globally stored objects
        globals_cleanup(prompt)
        list_counter_map.clear()
        
        # Strip comments
        positive_prompt = ED_Util.strip_comments(positive)
        negative_prompt = ED_Util.strip_comments(negative)        

        # Embedding stacker process
        lora_stack, positive_prompt, negative_prompt, positive_refiner, negative_refiner = Embedding_Stacker_ED.embedding_process(lora_stack, positive_prompt, negative_prompt, positive_refiner, negative_refiner)     

        # GET PROPERTIES #  
        properties = self.get_properties(extra_pnginfo, my_unique_id, prompt)       

        # Model, clip, vae, lora_params 
        model, clip, vae, lora_stack, lora_params, is_flux_model = \
            self.load_model_clip_vae(properties, ckpt_name, vae_name, clip_skip,lora_stack, model_opt, clip_opt, prompt, my_unique_id)       

        #################### PROMPT ENCODING #####################
        #Encode prompt
        if not is_flux_model and (properties['token_normalization'] != "none" or properties['weight_interpretation'] != "comfy"):            
            print(f"\033[34mEfficient Loader ED : Use CLIP Text Encode Advanced  - token normalization : {properties['token_normalization']}, weight interpretation : {properties['weight_interpretation']}\033[0m")
            clip_encoder = BNK_EncoderWrapper(properties['token_normalization'], properties['weight_interpretation'])            
        else:
            clip_encoder = None

        negative_encoded = BNK_EncoderWrapper.imp_encode(negative_prompt, clip, clip_encoder)
        
        if is_flux_model or not properties['wildcard_node_exist'] or cnet_stack or not properties['use_latent_rebatch'] or batch_size == 1 or properties['use_apply_lora']:
            positive_prompt = wildcard_ED.process(positive_prompt, seed)
            positive_encoded = BNK_EncoderWrapper.imp_encode(positive_prompt, clip, clip_encoder)
        else:
            positive_encoded = None

        #################### LATENT PROCESSING ####################
        #✍️ Txt2Img         
        if paint_mode == "✍️ Txt2Img":
            # Create Empty Latent
            samples_latent = nodes.EmptyLatentImage().generate(image_width, image_height, batch_size)[0]
        else:
            if pixels is None:
                raise Exception("Efficient Loader ED: Img2Img or inpaint mode requires an image.\n\n\n\n\n\n")
            image_width, image_height = ED_Util.get_image_size(pixels)

            #VAE Encode
            latent_t = ED_Util.vae_encode(vae, pixels, properties['tiled_vae_encode'])
            
            # 🎨 Inpaint
            if paint_mode == "🎨 Inpaint(Ksampler)":
                if  mask is None:
                    raise Exception("Efficient Loader ED: inpaint mode requires an mask.\n\n\n\n\n\n")
                if not positive_encoded:
                    positive_prompt = wildcard_ED.process(positive_prompt, seed)
                    positive_encoded = BNK_EncoderWrapper.imp_encode(positive_prompt, clip, clip_encoder)
                    
                positive_encoded, negative_encoded, latent_t = nodes.InpaintModelConditioning().encode(positive_encoded, negative_encoded, pixels, vae, mask)
                
            elif paint_mode == "🎨 Inpaint(MaskDetailer)":
                if  mask is None:
                    raise Exception("Efficient Loader ED: inpaint mode requires an mask.\n\n\n\n\n\n")

            #RepeatLatentBatch
            samples_latent = nodes.RepeatLatentBatch().repeat(latent_t, batch_size)[0]            
            
            # change image_width and image_height widget from image size
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "image_width", "type": "text", "data": image_width})
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "image_height", "type": "text", "data": image_height})
        
        # LatentRebatch -> List
        if properties['use_latent_rebatch'] and paint_mode != "🎨 Inpaint(MaskDetailer)" and not properties['use_apply_lora']:
            latent_list = LatentRebatch().rebatch((samples_latent,), (1,))[0]
        else:
            latent_list = []
            latent_list.append(samples_latent)

        if positive_encoded:
            # Apply ControlNet and Regional Stack if given
            model, positive_encoded, negative_encoded = ED_Reg.apply_controlnet_region(cnet_stack, positive_encoded, negative_encoded, model, clip, seed, clip_encoder)
        
        # Data for XY Plot
        refiner_clip = refiner_clip_skip = None
        dependencies = (vae_name, ckpt_name, clip, clip_skip, refiner_name, refiner_clip, refiner_clip_skip,
                        positive_prompt, negative_prompt, properties['token_normalization'], properties['weight_interpretation'], ascore,
                        image_width, image_height, lora_params, cnet_stack)
                
        context = new_context_ed(None, model=model, clip=clip, vae=vae, positive=positive_encoded, negative=negative_encoded, 
                latent=samples_latent, images=pixels, seed=seed, step_refiner=batch_size, cfg=cfg, ckpt_name=ckpt_name, sampler=sampler_name, scheduler=scheduler, clip_width=image_width, clip_height=image_height, text_pos_g=positive_prompt, text_neg_g=negative_prompt, mask=mask, lora_stack=lora_stack, clip_encoder=clip_encoder)

        return (context, model, positive_encoded, negative_encoded, latent_list, pixels, clip, dependencies,)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return_value = True
        names = ["🔌 model_opt input"] + folder_paths.get_filename_list("checkpoints")

        name = kwargs["ckpt_name"]

        if not name in names:
            return_value = f"Checkpoint not found: {name}"
            raise Exception(f"\033[30m \033[101mEfficient Loader ED : checkpoint '{name}' is not found\033[0m")

        return return_value

    @staticmethod
    def get_properties(extra_pnginfo, my_unique_id, prompt):
        properties = {
            "tiled_vae_encode": False,
            "use_latent_rebatch": True,
            "use_apply_lora": False,
            "token_normalization": "none",
            "weight_interpretation": "comfy",
            "wildcard_node_exist": False,
        }
        
        if extra_pnginfo and "workflow" in extra_pnginfo:
            workflow = extra_pnginfo["workflow"]

            for node in workflow["nodes"]:
                if node["id"] == int(my_unique_id):
                    properties['tiled_vae_encode'] = node["properties"]["Use tiled VAE encode"]
                    if properties['use_latent_rebatch']:
                        properties['use_latent_rebatch'] = node["properties"]["Use Latent Rebatch"]
                    properties['token_normalization'] = node["properties"]["Token normalization"]
                    properties['weight_interpretation'] = node["properties"]["Weight interpretation"]

                if node["type"] == "Wildcard Encode 💬ED" and node["mode"] == 0:
                    properties['wildcard_node_exist'] = True
                    if not properties['use_apply_lora']:
                        if node["properties"]["Turn on Apply Lora"] == True:
                            print(f"\033[36mWildcard Encode ED: Turn on Apply Lora, loading Lora is pending.\033[0m")
                            properties['use_apply_lora'] = True

                if node["type"] == "KSampler (Efficient) 💬ED":
                    if node["mode"] != 0:
                        properties['use_latent_rebatch'] = False

                if node["type"] == "Refiner Script 💬ED" and node["mode"] == 0:
                    if ED_Util.get_widget_value(prompt, node, "ignore_batch_size") == True:
                        properties['use_latent_rebatch'] = False

        return properties

    @staticmethod
    def load_model_clip_vae(properties, ckpt_name, vae_name, clip_skip, lora_stack, model_opt, clip_opt, prompt, my_unique_id):
        # Retrieve cache numbers
        vae_cache, ckpt_cache, lora_cache, refn_cache = get_cache_numbers("Efficient Loader")

        global loaded_objects
        lora_params = None
        
        if lora_stack:
            lora_params = []
            lora_params.extend(lora_stack)
        
        if ckpt_name == "🔌 model_opt input":
            if model_opt is None:
                raise Exception("Efficient Loader ED: ckpt_name or model_opt is required.\n\n\n\n\n\n")        
            if clip_opt is None:
                raise Exception("Efficient Loader ED: clip_opt is required when using model_opt.\n\n\n\n\n\n")
            
            loaded_objects["ckpt"] = []
            loaded_objects["lora"] = []
            model = model_opt
            clip =clip_opt
            loaded_objects["ckpt"].append(("using model_opt", None, None, None, [my_unique_id]))
            
            if vae_name != "Baked VAE":
                vae = load_vae(vae_name, my_unique_id, cache=vae_cache, cache_overwrite=True)
            else:
                Exception("Efficient Loader ED: Baked VAE is None \n\n\n\n\n\n")
                
            ###print_loaded_objects_entries()
            print_loaded_objects_entries(my_unique_id, prompt)
            
            ### lora apply when using model_opt !!After print_loaded_objects_entries()!!
            if lora_stack and not properties['use_apply_lora']:
                model, clip = ED_Util.apply_load_lora(lora_stack, model, clip)
                lora_stack = None
        
        else:            
            if lora_stack and not properties['use_apply_lora']:   
                # Load LoRa(s)
                model, clip = load_lora(lora_params, ckpt_name, my_unique_id, cache=lora_cache, ckpt_cache=ckpt_cache, cache_overwrite=True)
                lora_stack = None
                
                if vae_name == "Baked VAE":
                    vae = get_bvae_by_ckpt_name(ckpt_name)                

            else:
                loaded_objects["lora"] = []
                model, clip, vae = load_checkpoint(ckpt_name, my_unique_id, cache=ckpt_cache, cache_overwrite=True)           
                
            # Check for custom VAE
            if vae_name != "Baked VAE":
                 vae = load_vae(vae_name, my_unique_id, cache=vae_cache, cache_overwrite=True)
            
            ###print_loaded_objects_entries()
            print_loaded_objects_entries(my_unique_id, prompt)        
        
        modle_type = None
        if hasattr(model, "model"):
            modle_type = model.model.__class__.__name__
        
        if modle_type == "Flux":
            print(f"\r{message('Efficient Loader ED :')}\033[38;5;173m model type is {modle_type}, ignore clip skip\033[0m")
            is_flux_model = True
        elif clip_skip == 0:
            print(f"\r{message('Efficient Loader ED :')}\033[38;5;173m clip skip is 0, ignore clip skip\033[0m")
            is_flux_model = False
        else:
            clip = nodes.CLIPSetLastLayer().set_last_layer(clip, clip_skip)[0]
            print(f"Clip skip: {clip_skip}")
            is_flux_model = False
           
        return model, clip, vae, lora_stack, lora_params, is_flux_model

#####################################################################################################
# Load Image ED
prompt_blacklist_ed = set([
    'filename_prefix', 'file'
])

class LoadImage_ED(nodes.LoadImage):
    UPSCALE_METHODS = ["🚫 Do not upscale", "nearest-exact", "bilinear", "area", "bicubic", "lanczos"] + ["upscale_models/"+x for x in folder_paths.get_filename_list("upscale_models")]    
    PROPORTION_METHODS = ["disabled", "1.5x", "2x", "3x", "4x", "based on width", "based on height", "disabled & crop center"]
    
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required": {
                              "image": (sorted(files), {"image_upload": True}),
                              "upscale_method": (s.UPSCALE_METHODS,),
                              "width": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                              "height": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                              "keep_proportions": (s.PROPORTION_METHODS,),},
                    "hidden": { "my_unique_id": "UNIQUE_ID",}
                    }
    CATEGORY = "Efficiency Nodes/Image"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING",)
    RETURN_NAMES = ("IMAGE", "MASK", "PROMPT_TEXT",)
    FUNCTION = "load_image"

    def load_image(self, image, upscale_method, width, height, keep_proportions, my_unique_id):        
        output_image, output_mask = super().load_image(image)
        image_width, image_height = ED_Util.get_image_size(output_image)
        text = self.get_prompt(image)

        if "not upscale" not in upscale_method:
            if "upscale_models" in upscale_method:
                upscaler = ED_Util.load_upscale_model(upscale_method.split("/", 1)[-1])
                output_image = ImageUpscaleWithModel().upscale(upscaler, output_image)[0]
                upscale_method = "lanczos"

            width, height = self.calculate_dimensions(width, height, keep_proportions, image_width, image_height)
            crop = "center" if keep_proportions == "disabled & crop center" else "disabled"

            self.send_feedback(my_unique_id, width, height)

            output_image = nodes.ImageScale().upscale(output_image, upscale_method, width, height, crop)[0] 
            if output_mask is not None:
                output_mask = self.upscale_mask(output_mask, upscale_method, width, height, crop)

        return output_image, output_mask, text

    @staticmethod
    def calculate_dimensions(width, height, keep_proportions, original_width, original_height):
        scale_factors = {"1.5x": 1.5, "2x": 2, "3x": 3, "4x": 4}

        if keep_proportions in {"based on width", "based on height"}:
            width = original_width if width == 0 else width
            height = original_height if height == 0 else height
            ratio = (width / original_width) if keep_proportions == "based on width" else (height / original_height)
            return round(original_width * ratio), round(original_height * ratio)

        elif keep_proportions in scale_factors:
            factor = scale_factors[keep_proportions]
            return int(original_width * factor), int(original_height * factor)

        return width, height

    @staticmethod
    def send_feedback(unique_id, width, height):
        feedback = PromptServer.instance.send_sync
        feedback("ed-node-feedback", {"node_id": unique_id, "widget_name": "width", "type": "text", "data": width})
        feedback("ed-node-feedback", {"node_id": unique_id, "widget_name": "height", "type": "text", "data": height})

    @staticmethod
    def upscale_mask(mask, method, width, height, crop):
        method = "bicubic" if method == "lanczos" else method
        mask = mask.unsqueeze(1)
        mask = comfy.utils.common_upscale(mask, width, height, method, crop)
        return mask.squeeze(1)

    @classmethod
    def IS_CHANGED(s, image,  **kwargs):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image,  **kwargs):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True

    @staticmethod
    def get_prompt(image):
        image_path = folder_paths.get_annotated_filepath(image)
        img = Image.open(image_path)
        info = img.info

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

                obj = NODES.get(x, None)
                if obj is not None:
                    input_types = obj.INPUT_TYPES()
                    node_inputs[x] = input_types
                    return input_types
                else:
                    return None

        if not isinstance(info, dict):
            text = "There is no prompt information within the image."
        
        elif 'prompt' in info:
            prompt = json.loads(info['prompt'])
            for k, v in prompt.items():
                input_types = get_node_inputs(v['class_type'])
                if input_types is not None and 'required' in input_types:
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
                if type(v[1]) is str and ',' in v[1]:
                    text += f"{k} [{v[0]}] ==> {v[1]}\n"
                elif type(v[1]) is int:
                    text += f"{k} [{v[0]}] ==> {v[1]}\n"
            #positive = prompt_dicts.get(positive_id.strip(), "")
            #negative = prompt_dicts.get(negative_id.strip(), "")

        elif 'exif' in info:
            try:
                text = info['exif'].decode('utf-16')  # 자동으로 LE/BE 판단
            except UnicodeDecodeError:
                try:
                    text = info['exif'].decode('utf-8')  # 백업 디코딩
                except UnicodeDecodeError:
                    text = "There is no prompt information within the image."
            
            # 영어 알파벳이 처음 등장하는 위치 찾기
            match = re.search(r'[a-zA-Z]', text)
            if match:
                text = text[match.start():]  # 첫 번째 영어 문자가 나온 위치부터 출력
                text = text.replace("\n","\n\n") + ("\n")
            else:
                text = "There is no prompt information within the image."

        else:
            text = "There is no prompt information within the image."
        
        return text


# Save Image ED
class SaveImage_ED(nodes.SaveImage):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { },
                    "optional": {
                        "context_opt": ("RGTHREE_CONTEXT",),
                        "image_opt": ("IMAGE",),
                        "filename_prefix": ("STRING", {"default": "%date:yyyy-MM-dd%/%date:MM-dd%"}),
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
# Control Net Script ED
# class Control_Net_Script_ED:
    # @classmethod
    # def INPUT_TYPES(cls):
        # return {"required": {"control_net": ("CONTROL_NET",),
                             # "image": ("IMAGE",),
                             # "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                             # "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                             # "end_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001})},
                # "optional": {"cnet_stack": ("CONTROL_NET_STACK",),
                                   # "script": ("SCRIPT",)},
                # }

    # RETURN_TYPES = ("SCRIPT",)
    # RETURN_NAMES = ("SCRIPT",)
    # FUNCTION = "control_net_script_ed"
    # CATEGORY = "Efficiency Nodes/Scripts"

    # def control_net_script_ed(self, control_net, image, strength, start_percent, end_percent, cnet_stack=None, script=None):
        # script = script or {}        
        # # If control_net_stack is None, initialize as an empty list        
        # cnet_stack = [] if cnet_stack is None else cnet_stack

        # # Extend the control_net_stack with the new tuple
        # cnet_stack.extend([(control_net, image, strength, start_percent, end_percent)])
        # script["control_net"] = (cnet_stack)
        # return (script,)

##############################################################################################################
# Refiner Script ED
class Refiner_Script_ED:
    SET_SEED_CFG_SAMPLER = {
        "from context": 1,
        "from node only": 2,
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                            "set_seed_cfg_sampler": (list(cls.SET_SEED_CFG_SAMPLER.keys()), {"default": "from context"}),
                            "add_noise": (["enable", "disable"], ),                           
                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "steps": ("INT", {"default": 30, "min": 1, "max": 10000}),
                            "cfg": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 100.0}),
                            "sampler_name": (comfy.samplers.KSampler.SAMPLERS, {"default": "dpmpp_sde"}),
                            "scheduler": (SCHEDULERS, {"default": "karras"}),
                            "denoise": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01}),
                            "start_at_step": ("INT", {"default": 17, "min": 0, "max": 10000}),
                            "end_at_step": ("INT", {"default": 100, "min": 0, "max": 10000}),
                            "ignore_batch_size": ("BOOLEAN", {"default": True}),
                            "do_refine_only": ("BOOLEAN", {"default": True}),
                        },
                "optional": {"refiner_model_opt": ("MODEL",),
                            "refiner_clip_opt": ("CLIP",),
                            "refiner_vae_opt": ("VAE",),
                            "lora_stack": ("LORA_STACK",),
                            },
                "hidden": {"my_unique_id": "UNIQUE_ID",},}
    RETURN_TYPES = ("SCRIPT",)
    RETURN_NAMES = ("SCRIPT",)
    FUNCTION = "refiner_script_ed"
    CATEGORY = "Efficiency Nodes/Scripts"

    def refiner_script_ed(self, set_seed_cfg_sampler, add_noise, seed, steps, cfg, sampler_name, scheduler, denoise, start_at_step, end_at_step, ignore_batch_size, do_refine_only, refiner_model_opt=None, refiner_clip_opt=None, refiner_vae_opt=None, lora_stack=None, my_unique_id=None):
        script = {}
        
        if refiner_model_opt:
            if refiner_clip_opt is None or refiner_vae_opt is None:
                raise Exception("Refiner Script ED: refiner_clip and refiner_vae are required.\n\n\n\n\n\n")

        if set_seed_cfg_sampler == "from context":
            seed = None
        
        refiner_script = (refiner_model_opt, refiner_clip_opt, refiner_vae_opt, add_noise, seed, steps, cfg, sampler_name, scheduler, denoise, start_at_step, end_at_step, ignore_batch_size, lora_stack, do_refine_only)
            #print(f"\033[38;5;173mRefiner Script ED: Refiner script loading. steps:{steps}, start step:{start_at_step}, end step:{end_at_step}\033[0m")
        script["refiner_script"] = refiner_script
        
        return (script,)

##############################################################################################################
#Reginal scripts process
class ED_Reg:
    @staticmethod
    def apply_controlnet_region(cnet_stack, positive_encoded, negative_encoded, model=None, clip=None, seed=0, clip_encoder=None):
        if cnet_stack:        
            for control_net_tuple in cnet_stack:
                if str(control_net_tuple[-1]) == "Region_Stack":
                    model, positive_encoded = ED_Reg.process_region_stack(control_net_tuple, positive_encoded, model, clip, seed, clip_encoder)

            for control_net_tuple in cnet_stack:
                if str(control_net_tuple[-1]) != "Region_Stack":
                    print(f"\r{message('Efficiency Nodes ED:')}\033[38;5;173m apply control net stack.\033[0m")
                    
                    control_net, image, strength, start_percent, end_percent = control_net_tuple
                    positive_encoded, negative_encoded = nodes.ControlNetApplyAdvanced().apply_controlnet(positive_encoded, negative_encoded, control_net, image, strength, start_percent, end_percent)
        
        return (model, positive_encoded, negative_encoded)

    @staticmethod
    def process_region_stack(control_net_tuple, base_positive, model, clip, seed, clip_encoder):
        region_script, global_prompt_weight, width, height, _ = control_net_tuple
        print(f"\r{message('Efficiency Nodes ED:')}\033[38;5;173m apply regional stack - script count : {len(region_script)}\033[0m")
        
        processd_positive, regions = ED_Reg.process_region_script(region_script, base_positive, model, clip, seed, clip_encoder)
        
        flattened_regions = ED_Reg.attention_couple_regions(regions)
        
        if 'AttentionCouple' not in NODES:
            ED_Util.try_install_custom_node('A8R8 ComfyUI Nodes', 'https://github.com/ramyma/A8R8_ComfyUI_nodes')

        model = NODES['AttentionCouple']().attention_couple(model, global_prompt_weight, 
            base_positive, height, width, flattened_regions)[0]

        return (model, processd_positive)

    @staticmethod
    def process_region_script(region_script, base_positive, model, clip, seed, clip_encoder):
        regions = []
        for region_tuple in region_script:
            mask, prompt, condition_strength, set_conditon_area, region_weight, lora_stack = region_tuple

            prompt = wildcard_ED.process(prompt, seed)
            reg_positive = BNK_EncoderWrapper.imp_encode(prompt, clip, clip_encoder)
            hooks = ED_Reg.process_script_lora_stack(lora_stack)
            base_positive = NODES['ConditioningSetPropertiesAndCombine']().set_properties(base_positive, reg_positive, condition_strength, set_conditon_area, mask, hooks, None)[0]
            regions.extend([{"cond": reg_positive, "mask": mask, "weight": region_weight}])

        return (base_positive, regions)

    @staticmethod
    def process_script_lora_stack (lora_stack):
        hooks = None
        if lora_stack:
            lora_params = []
            lora_count = 0
            lora_params.extend(lora_stack)
            print(f"\r{message('Regional Script ED:')} create LoRA hook -")

            for lora in lora_params:
                lora_name, strength_model, strength_clip = lora
                lora_count += 1
                lora_model_info = f"{os.path.splitext(os.path.basename(lora_name))[0]}({round(strength_model, 2)},{round(strength_clip, 2)})"
                print(f"  [{lora_count}] lora(mod,clip): {lora_model_info}")
                hooks = NODES['CreateHookLora']().create_hook(lora_name, strength_model, strength_clip, hooks)[0]

        return hooks

    @staticmethod
    def attention_couple_regions (regions):
        flattened_regions = reduce(
            lambda acc, region: acc + region
            if isinstance(region, list)
            else acc + [region]
            if region
            else acc,
            regions,
            [],
        )        
        return flattened_regions

##############################################################################################################
# REGIONAL NODES
##############################################################################################################
# Regional Stacker - Main
class Regional_Stacker_ED:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                            "region_script": ("REGION_SCRIPT",),
                            "global_prompt_weight": ("FLOAT",{"default": 1.0, "min": 0.01, "max": 1.0, "step": 0.1, "tooltip": "Base prompt strength.", }, ),
                            "width": ("INT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 1}),
                            "height": ("INT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 1}),
                            "empty image": (["Create empty image"],),},
                    }

    RETURN_TYPES = ("CONTROL_NET_STACK",)
    RETURN_NAMES = ("CNET_STACK",)
    FUNCTION = "regional_stacker"
    CATEGORY = "Efficiency Nodes/Stackers"

    def regional_stacker(self, region_script, global_prompt_weight, width, height, **kwargs):
        # Extend the control_net_stack with the new tuple
        cnet_stack = []
        cnet_stack.extend([(region_script, global_prompt_weight, width, height, "Region_Stack")])
        return (cnet_stack,) 

# Regional Processor - Main
class Regional_Processor_ED:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                            "model": ("MODEL",),
                            "clip": ("CLIP",),
                            "base_positive": ("CONDITIONING",),
                            "region_script": ("REGION_SCRIPT",),
                            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                            "global_prompt_weight": ("FLOAT",{"default": 1.0, "min": 0.01, "max": 1.0, "step": 0.1, "tooltip": "Base prompt strength.", }, ),
                            "width": ("INT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 1}),
                            "height": ("INT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 1}),
                            "empty image": (["Creates empty image"], ), },
                    }

    RETURN_TYPES = ("MODEL", "CONDITIONING",)
    RETURN_NAMES = ("MODEL", "POSITIVE",)
    FUNCTION = "regional_processor"
    CATEGORY = "Efficiency Nodes/Stackers"

    def regional_processor(self, model, clip, base_positive, region_script, seed, global_prompt_weight, width, height, **kwargs):
        # Extend the control_net_stack with the new tuple
        cnet_stack = []
        cnet_stack.extend([(region_script, global_prompt_weight, width, height, "Region_Stack")])            
        model, base_positive, _ = ED_Reg.apply_controlnet_region(cnet_stack, base_positive, None, model, clip, seed, None)

        return (model, base_positive)

# Regional Script -Sub
class Regional_Script_ED():
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                            "url": ("STRING", {"default": "None", "multiline": False}),
                            "use_blur_mask": ("BOOLEAN", {"default": False, "label_on": "Use Gaussian Blur Mask", "label_off": "Don't use Blur Mask"}),
                            "blur_mask_kernel_size": ("INT", {"default": 10, "min": 0, "max": 100, "step": 1}),
                            "blur_mask_sigma": ("FLOAT", {"default": 10.0, "min": 0.1, "max": 100.0, "step": 0.1}),
                            "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                            "Select to add Wildcard": (["Select the Wildcard to add to the text"],),
                            "condition_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                            "set_conditon_area": (["default", "mask bounds"],),
                            "region_weight": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 1.0, "step": 0.01},),},
                    "optional": {
                            "region_script": ("REGION_SCRIPT", ),
                            "image": ("IMAGE",),
                            "mask": ("MASK",),
                            "lora_stack": ("LORA_STACK",),},
                    }

    RETURN_TYPES = ("REGION_SCRIPT", "IMAGE",)
    RETURN_NAMES = ("REGION_SCRIPT", "MASK_IMAGE",)
    FUNCTION = "regional_script"
    CATEGORY = "Efficiency Nodes/Scripts"

    def regional_script(self, use_blur_mask, blur_mask_kernel_size, blur_mask_sigma, prompt, condition_strength, set_conditon_area, region_weight, region_script=None, image=None, mask=None, lora_stack=None, **kwargs):
        region_script = [] if region_script is None else region_script
        mask_image = None
        prompt = ED_Util.strip_comments(prompt)
        
        if mask is not None:
            if use_blur_mask:
                if 'ImpactGaussianBlurMask' not in NODES:
                    ED_Util.try_install_custom_node('ComfyUI Impact Pack', 'https://github.com/ltdrdata/ComfyUI-Impact-Pack')

                mask = NODES['ImpactGaussianBlurMask']().doit(mask, blur_mask_kernel_size, blur_mask_sigma)[0]
            
            mask_image = NODES['MaskToImage']().mask_to_image(mask)[0]
            region_script.extend([(mask, prompt, condition_strength, set_conditon_area, region_weight, lora_stack)])

        return (region_script, mask_image)

##############################################################################################################
# Int Holder ED
class Int_Holder_ED:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { },
            "optional": {
                    "int_opt": ("INT", {"forceInput": True}),
                    "output_int": ("INT", {"default": 0, "min": 0, "max": sys.maxsize, "step": 1}),
            },
            "hidden": {"my_unique_id": "UNIQUE_ID",},
        }

    FUNCTION = "store_value"
    RETURN_TYPES = ("INT", )
    RETURN_NAMES = ("INT",)
    OUTPUT_NODE = True
    CATEGORY = "Efficiency Nodes/Simple Eval"    

    def store_value(self, int_opt=None, output_int=0, my_unique_id=None):
        if int_opt:
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "output_int", "type": "text", "data": int_opt})            
            output_int = int_opt
            
        PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "", "type": "title", "data": output_int})
        return (output_int,)

##############################################################################################################
# Context To BasicPipe
class ContextToBasicPipe:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"context": ("RGTHREE_CONTEXT",),},
                }

    RETURN_TYPES = ("BASIC_PIPE", )
    RETURN_NAMES = ("BASIC_PIPE", )
    FUNCTION = "context_to_basic_pipe"

    CATEGORY = "Efficiency Nodes/Misc"

    def context_to_basic_pipe(self, context):
        _, model, clip, vae, positive, negative = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative"])
        pipe = (model, clip, vae, positive, negative)
        return (pipe, )

# Context To DetailerPipe
class ContextToDetailerPipe:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"context": ("RGTHREE_CONTEXT",),
                             "bbox_detector": ("BBOX_DETECTOR", ),
                             "wildcard": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                             "Select to add LoRA": (["Select the LoRA to add to the text"] + folder_paths.get_filename_list("loras"),),
                             "Select to add Wildcard": (["Select the Wildcard to add to the text"],),
                             },
                "optional": {
                    "sam_model_opt": ("SAM_MODEL", ),
                    "segm_detector_opt": ("SEGM_DETECTOR",),
                    "detailer_hook": ("DETAILER_HOOK",),
                    },
                }

    RETURN_TYPES = ("DETAILER_PIPE",)
    RETURN_NAMES = ("DETAILER_PIPE",)
    FUNCTION = "context_to_detailer_pipe"

    CATEGORY = "Efficiency Nodes/Misc"

    def context_to_detailer_pipe(self, *args, **kwargs):
        ctx = kwargs['context']
        bbox_detector = kwargs['bbox_detector']
        wildcard = kwargs['wildcard']
        sam_model_opt = kwargs.get('sam_model_opt', None)
        segm_detector_opt = kwargs.get('segm_detector_opt', None)
        detailer_hook = kwargs.get('detailer_hook', None)

        _, model, clip, vae, positive, negative = context_2_tuple_ed(ctx,["model", "clip", "vae", "positive", "negative"])
        pipe = model, clip, vae, positive, negative, wildcard, bbox_detector, segm_detector_opt, sam_model_opt, detailer_hook, None, None, None, None
        return (pipe,)

##############################################################################################################
# Get Booru Tag
get_booru_tag_id = 0
get_booru_tag_text_b = ""

class GetBooruTag_ED():
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "url": ("STRING", {"default": "None", "multiline": False}),                
            },
            "optional": {                
                #"text_a": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "text_a": ("STRING", {"forceInput": True}),
                "text_b": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                #"text_c": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "text_c": ("STRING", {"forceInput": True}),
                "Select to add Wildcard": (["Select the Wildcard to add to the text"], ),
                "Group tags by category": (["Group tags by category"], ),
            },
            "hidden": {"my_unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = 'get_prompt'
    CATEGORY = 'Efficiency Nodes/Prompt'

    def get_prompt(self, url, text_a="", text_b="", text_c="", my_unique_id=None, **kwargs):
        global get_booru_tag_id, get_booru_tag_text_b
        get_booru_tag_id = my_unique_id
        get_booru_tag_text_b = text_b

        #strip commet
        text_a = ED_Util.strip_comments(text_a)
        text_b = ED_Util.strip_comments(text_b)
        text_c = ED_Util.strip_comments(text_c)

        strip = " ,\n"
        out_text = ""
        if text_a != "":
            out_text = f"{text_a.lstrip(strip).rstrip(strip)},\n\n"
        if text_b != "":
            out_text += f"{text_b.lstrip(strip).rstrip(strip)},\n\n"
        if text_c != "":
            out_text += f"{text_c.lstrip(strip).rstrip(strip)}"

        out_text = f"{out_text.rstrip(strip)}"
        
        return (out_text,)

##############################################################################################################
# Simple text
class SimpleText_ED():
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {                              
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = 'get_text'
    CATEGORY = 'Efficiency Nodes/Prompt'

    def get_text(self, text):
        #strip commet
        text = ED_Util.strip_comments(text)

        strip = " ,\n"
        text = f"{text.lstrip(strip).rstrip(strip)}"
        
        return (text,)

##############################################################################################################
# TIPO Script ED

class TIPOScript_ED:
    @classmethod
    def INPUT_TYPES(s):
        if 'TIPO' in NODES:
            import kgen.models as tipo_models
            MODEL_NAME_LIST = [
                f"{model_name} | {file}".strip("_")
                for model_name, ggufs in tipo_models.tipo_model_list
                for file in ggufs
            ] + [i[0] for i in tipo_models.tipo_model_list]
        else:
            MODEL_NAME_LIST = ['KBlueLeaf/TIPO-500M-ft | TIPO-500M-ft-F16.gguf']

        return {"required": {
                        "context": ("RGTHREE_CONTEXT",),
                        #"tags": ("STRING", {"default": "", "multiline": True}),
                        "tipo_model": (MODEL_NAME_LIST, {"default": MODEL_NAME_LIST[0]}),
                        "format": ("STRING", {"default": """<|special|>, 
<|characters|>, <|copyrights|>, 
<|artist|>, 

<|general|>,

<|extended|>.

<|quality|>, <|meta|>, <|rating|>""", "multiline": True, },),
                    "temperature": ("FLOAT", {"default": 0.5, "step": 0.01}),
                    "top_p": ("FLOAT", {"default": 0.95, "step": 0.01}),
                    "min_p": ("FLOAT", {"default": 0.05, "step": 0.01}),
                    "top_k": ("INT", {"default": 80}),
                    "tag_length": (["very_short", "short", "long", "very_long"], {"default": "long"},),
                    "nl_length": (["very_short", "short", "long", "very_long"], {"default": "long"},),
                    "device": (["cpu", "cuda"], {"default": "cuda"}),
                },
                "optional": {
                        "positive_opt": ("CONDITIONING",),
                        "nl_prompt": ("STRING", {"default": "", "multiline": True}),
                        "ban_tags": ("STRING", {"default": "", "multiline": True}),
                    },
                }

    RETURN_TYPES = ("RGTHREE_CONTEXT", "CONDITIONING", "STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("CONTEXT", "POSITIVE", "PROMPT", "USER_PROMPT", "UNFORMATTED_PROMPT", "UNFORMATTED_USER_PROMPT",)
    FUNCTION = "tipo_process"
    CATEGORY = 'Efficiency Nodes/Prompt'

    def tipo_process(self, context, tipo_model, tag_length, nl_length, format, temperature, top_p, min_p, top_k, device, positive_opt=None, nl_prompt = "", ban_tags = ""):
        # Unpack context
        _, clip, seed, width, height, positive_prompt, clip_encoder = context_2_tuple_ed(context, ["clip", "seed", "clip_width", "clip_height", "text_pos_g", "clip_encoder"])
        
        if 'TIPO' not in NODES:
            ED_Util.try_install_custom_node('z-tipo-extension', 'https://github.com/KohakuBlueleaf/z-tipo-extension')
        
        out_string = NODES['TIPO']().execute(tipo_model, positive_prompt, nl_prompt, width, height, seed, tag_length, nl_length, ban_tags, format, temperature, top_p, min_p, top_k, device)
        
        positive_encoded = BNK_EncoderWrapper.imp_encode(out_string[0], clip, clip_encoder)
        context = new_context_ed(context, positive=positive_encoded, text_pos_g=out_string[0])        
        
        return context, positive_encoded, out_string[0], out_string[1], out_string[2], out_string[3]

##############################################################################################################
# SAMPLER
##############################################################################################################
# KSampler (Efficient) ED
class KSampler_ED():
    SET_SEED_CFG_SAMPLER = {
        "from node to ctx": 1,
        "from context": 2,
        "from node only": 3,
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {"required":
                    {"context": ("RGTHREE_CONTEXT",),
                    "set_seed_cfg_sampler": (list(cls.SET_SEED_CFG_SAMPLER.keys()), {"default": "from context"}),
                    "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                    "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                    "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                    "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                    "scheduler": (SCHEDULERS,),
                    "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),                    
                    },
                "optional": {
                    "guide_size": ("FLOAT", {"default": 512, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    "guide_size_for": ("BOOLEAN", {"default": True, "label_on": "mask bbox", "label_off": "crop region"}),
                    "max_size": ("FLOAT", {"default": 1216, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    "feather": ("INT", {"default": 15, "min": 0, "max": 100, "step": 1}),
                    "crop_factor": ("FLOAT", {"default": 3.0, "min": 1.0, "max": 10, "step": 0.1}),
                    #"cycle": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                    "positive_opt": ("CONDITIONING",),
                    "script": ("SCRIPT",),                    
                    #"detailer_hook": ("DETAILER_HOOK",),
                    "preview_method": (["auto", "latent2rgb", "taesd", "vae_decoded_only", "none"],),
                    },
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},}

    RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE", "INT",)
    RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE", "STEPS_INT",)
    OUTPUT_NODE = True
    FUNCTION = "sample_ed"
    CATEGORY = "Efficiency Nodes/Sampling"

    def sample_ed(self, context, set_seed_cfg_sampler, seed, steps, cfg, sampler_name, scheduler, denoise,  
                  guide_size=512, guide_size_for=True, max_size=1216, feather=15, crop_factor=3,
                  positive_opt=None, script=None, preview_method="auto",
                  prompt=None, extra_pnginfo=None, my_unique_id=None):        

        # Unpack context
        _, model, clip, vae, positive, negative, latent_image, optional_image, batch_size, mask = \
            context_2_tuple_ed(context, ["model", "clip", "vae", "positive", "negative", "latent", "images", "step_refiner", "mask"])
        
        # positive에  guidance 가 있는지 확인하고 있으면 스킵이 안되게 함.
        positive, c_index = self.is_positive_changed(positive, positive_opt)

        if model is None or latent_image is None:
            raise Exception("KSampler (Efficient) ED: model and latent are required.")

        previous_preview_method = global_preview_method()
        properties, vae_decode = self.extract_mask_detailer_settings(extra_pnginfo, my_unique_id)

        # Handle seed, cfg, sampler, scheduler from context or update context
        context, seed, cfg, sampler_name, scheduler = self.handle_seed_cfg_sampler(context, set_seed_cfg_sampler, seed, cfg, sampler_name, scheduler, my_unique_id)

        print(f"\r{message('KSampler (Efficient) ED:')} current seed - {warning(str(seed))}")

        # Handle script if present
        latent_list = None
        script, refiner_script, do_refine_only = self.check_refiner_script(script)
        
        if do_refine_only:
            latent_list = ED_Util.vae_encode(vae, optional_image, properties['tiled_vae'])

        ###### Mask Detailer ######
        elif properties['mask_detailer_mode']:
            print(f"\r{message('KSampler (Efficient) ED:')}\033[38;5;173m use Mask Detailer(ImpactPack) for inpainting\033[0m")
            set_preview_method(preview_method)
            
            output_images, _, _ = MaskDetailer_ED.mask_sampling(optional_image, mask, model, clip, vae, positive, negative,
                    guide_size, guide_size_for, max_size, properties['mask_mode'],
                    seed, steps, cfg, sampler_name, scheduler, denoise,
                    feather, crop_factor, properties['drop_size'], properties['refiner_ratio'], batch_size, properties['cycle'], 
                    None, properties['inpaint_model'], properties['noise_mask_feather'])

            latent_list = ED_Util.vae_encode(vae, output_images, properties['tiled_vae']) if refiner_script else None
            store_ksampler_results("image", my_unique_id, output_images)
            result_ui = nodes.PreviewImage().save_images(output_images, prompt=prompt, extra_pnginfo=extra_pnginfo)["ui"]

        ###### KSampler (Efficient) ######
        else:
            return_dict = NODES['KSampler (Efficient)']().sample(model, seed, steps, cfg, 
                sampler_name, scheduler, positive, negative, latent_image, preview_method, vae_decode, 
                denoise=denoise, prompt=prompt, extra_pnginfo=extra_pnginfo, my_unique_id=my_unique_id,
                optional_vae=vae, script=script, add_noise=None, start_at_step=None, end_at_step=c_index,
                return_with_leftover_noise=None, sampler_type="regular")               

            _, _, _, latent_list, _, output_images = return_dict["result"]
            result_ui = return_dict["ui"]

        ###### Refiner Script ######
        if refiner_script:            
            output_images = self.apply_refiner_script(context, refiner_script, latent_list or latent_image, preview_method, properties['tiled_vae'])
            
            store_ksampler_results("image", my_unique_id, output_images)
            result_ui = nodes.PreviewImage().save_images(output_images, prompt=prompt, extra_pnginfo=extra_pnginfo)["ui"]        
        
        # RESULT
        set_preview_method(previous_preview_method)
        context = new_context_ed(context, latent=latent_list or latent_image, images=output_images)

        return {"ui": result_ui, "result": (context, output_images, steps)}

    @staticmethod
    def is_positive_changed(positive, positive_opt):
        c_index = 1000
        if positive_opt:
            positive = positive_opt
            for t in positive:
                if "guidance" in t[1]:
                    c_index += t[1]["guidance"]             
                    break        
        return positive, c_index

    @staticmethod
    def extract_mask_detailer_settings(extra_pnginfo, my_unique_id):
        properties = {
            "mask_detailer_mode": False,
            "drop_size": 5,
            "cycle": 1,
            "inpaint_model": False,
            "noise_mask_feather": 20,
            "mask_mode": True,
            "refiner_ratio": 0.2,
            "tiled_vae": False,
        }
        # if vae_decode != "true (tiled)":
            # vae_decode = "true"

        if extra_pnginfo and "workflow" in extra_pnginfo:
            workflow = extra_pnginfo["workflow"]
            for node in workflow["nodes"]:
                if node["id"] == int(my_unique_id):
                    props = node["properties"]
                    properties['mask_detailer_mode'] = props.get("MaskDetailer mode", False)
                    properties['drop_size'] = int(props.get("(MaskDetailer) drop size", 5))
                    properties['cycle'] = int(props.get("(MaskDetailer) cycle", 1))
                    properties['inpaint_model'] = props.get("(MaskDetailer) inpaint model enable", False)
                    properties['noise_mask_feather'] = int(props.get("(MaskDetailer) noise mask feather", 20))
                    properties['tiled_vae'] = props.get("Use tiled VAE decode", False)
                    vae_decode = "true (tiled)" if properties['tiled_vae'] else "true"
                    return properties , vae_decode

        return properties, vae_decode
        
    @staticmethod
    def handle_seed_cfg_sampler(context, mode, seed, cfg, sampler_name, scheduler, my_unique_id):
        if mode == "from context":
            _, c_seed, c_cfg, c_sampler, c_scheduler = context_2_tuple_ed(context, ["seed", "cfg", "sampler", "scheduler"])
            if c_seed is None:
                raise Exception("KSampler (Efficient) ED: no seed, cfg, sampler, scheduler in the context.")

            seed, cfg, sampler_name, scheduler = c_seed, c_cfg, c_sampler, c_scheduler

            for key, value in zip(["seed", "cfg", "sampler_name", "scheduler"], [seed, cfg, sampler_name, scheduler]):
                PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": key, "type": "text", "data": value})

        elif mode == "from node to ctx":
            context = new_context_ed(context, seed=seed, cfg=cfg, sampler=sampler_name, scheduler=scheduler)

        return context, seed, cfg, sampler_name, scheduler

    @staticmethod
    def check_refiner_script(script):
        refiner_script = None
        do_refine_only = False
        
        if script and "refiner_script" in script:
            refiner_script = script["refiner_script"]
            do_refine_only = refiner_script[-1]
            script = script.copy()
            del script['refiner_script']

        return script, refiner_script, do_refine_only
        
    @staticmethod
    def apply_refiner_script(context, refiner_script, latent_image, preview_method, is_tiled, return_with_leftover_noise=None):

        if refiner_script:
            refiner_model, refiner_clip, refiner_vae, refiner_add_noise, refiner_seed, refiner_steps, refiner_cfg, refiner_sampler_name, refiner_scheduler, refiner_denoise, refiner_start_at_step, refiner_end_at_step, refiner_ignore_batch_size, lora_stack, _ = refiner_script

            # Unpack context
            _, model, clip, vae, positive, negative, seed, cfg, sampler, scheduler, positive_prompt, negative_prompt, clip_encoder = \
            context_2_tuple_ed(context, ["model", "clip", "vae", "positive", "negative", "seed", "cfg", "sampler", "scheduler", "text_pos_g", "text_neg_g", "clip_encoder"])
            
            if not refiner_model:
                refiner_model = model
                refiner_clip = clip
                refiner_vae = vae
                
                if lora_stack:
                    model, clip = ED_Util.apply_load_lora(lora_stack, refiner_model, refiner_clip, "KSampler (Efficient) ED [Refiner Script]")
                
                refiner_positive = positive
                refiner_negative = negative

            else:                
                if lora_stack:
                    model, clip = ED_Util.apply_load_lora(lora_stack, refiner_model, refiner_clip, "KSampler (Efficient) ED [Refiner Script]")
                
                refiner_positive = BNK_EncoderWrapper.imp_encode(positive_prompt, refiner_clip, clip_encoder)
                refiner_negative = BNK_EncoderWrapper.imp_encode(negative_prompt, refiner_clip, clip_encoder)
            
            if not refiner_seed:
                refiner_seed = seed
                refiner_cfg =cfg
                refiner_sampler_name = sampler
                refiner_scheduler = scheduler                
            
            if refiner_ignore_batch_size:
                latent_image = nodes.LatentFromBatch().frombatch(latent_image, 0, 1)[0]
            
            print(f"\r{message('KSampler (Efficient) ED:')}\033[38;5;173m running refiner script. start step:{refiner_start_at_step}, steps:{refiner_steps}, cfg:{refiner_cfg}\033[0m")
            
            set_preview_method(preview_method)
            latent_image = nodes.KSamplerAdvanced().sample(refiner_model, refiner_add_noise, refiner_seed, refiner_steps, 
                            refiner_cfg, refiner_sampler_name, refiner_scheduler, refiner_positive, refiner_negative, latent_image, 
                            refiner_start_at_step, refiner_end_at_step, return_with_leftover_noise, refiner_denoise)[0]

            refiner_images = ED_Util.vae_decode(refiner_vae, latent_image, is_tiled)

        return refiner_images

##############################################################################################################
# KSamplerTEXT ED #for BackGround Make  
class KSamplerTEXT_ED():
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":
                    {"context": ("RGTHREE_CONTEXT",),
                    "set_seed_cfg_sampler": (list(KSampler_ED.SET_SEED_CFG_SAMPLER.keys()), {"default": "from context"}),
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

        _, model, clip, vae, optional_latent, optional_image, c_seed, c_cfg, c_sampler, c_scheduler = context_2_tuple_ed(context,["model", "clip", "vae", "latent", "images", "seed", "cfg", "sampler", "scheduler"])
        
        if model is None:
            raise Exception("KSampler TEXT ED: model is None. \n\n\n\n\n\n")                
        if optional_latent is None:
            raise Exception("KSampler TEXT ED requires 'Latent' for sampling.\n\n\n\n\n\n")        

        if set_seed_cfg_sampler == "from context":
            if c_seed is None:
                raise Exception("KSampler TEXT (Eff.) 💬ED: no seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
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
            image_width, image_height  = ED_Util.get_latent_size(optional_latent)
            print(f"KSampler TEXT ED: size get from latent (width {image_width} x height {image_height})")
        elif optional_image is not None:
            image_width, image_height  = ED_Util.get_image_size(optional_image)
            print(f"KSampler TEXT ED: size get from image (width {image_width} x height {image_height})")
        else:
            raise Exception("KSamplerTEXT ED: reference image or latent is required.\n\n\n\n\n\n")

        nodes.EmptyLatentImage().generate(image_width, image_height, batch_size=1)[0]
        
        positive_encoded = nodes.CLIPTextEncode().encode(clip, positive)[0]
        negative_encoded = nodes.CLIPTextEncode().encode(clip, negative)[0]
        
        return_dict = NODES['KSampler (Efficient)']().sample(model, seed, steps, cfg, sampler_name, scheduler, 
                positive_encoded, negative_encoded, latent_image, preview_method, vae_decode, denoise=denoise, prompt=prompt, 
                extra_pnginfo=extra_pnginfo, my_unique_id=my_unique_id,
                optional_vae=vae, script=script, add_noise=add_noise, start_at_step=start_at_step, end_at_step=end_at_step,
                return_with_leftover_noise=return_with_leftover_noise, sampler_type="regular")                        

        _, _, _, latent_list, _, output_images = return_dict["result"]
                        
        context = new_context_ed(context, latent=latent_list, images=output_images)                                
        return (context, output_images)

##############################################################################################################
# EXTENSIONS
##############################################################################################################
# Face Detailer ED
class FaceDetailer_ED():
    @classmethod
    def INPUT_TYPES(s):
        if 'UltralyticsDetectorProvider' in NODES:
            bboxs = ["bbox/"+x for x in folder_paths.get_filename_list("ultralytics_bbox")] + ["segm/"+x for x in folder_paths.get_filename_list("ultralytics_segm")]
            segms = ["None"] + ["segm/"+x for x in folder_paths.get_filename_list("ultralytics_segm")]
            sams = ["None"] + [x for x in folder_paths.get_filename_list("sams") if 'hq' not in x]      
        else:
            bboxs = ['bbox/face_yolov8m.pt']
            segms = ['None']
            sams = ['None', 'sam_vit_b_01ec64.pth']
        return {"required": {
                    "context": ("RGTHREE_CONTEXT",),
                    "set_seed_cfg_sampler": (list(KSampler_ED.SET_SEED_CFG_SAMPLER.keys()), {"default": "from context"}),
                    "bbox_detector": (bboxs, ),
                    "segm_detector_opt": (segms, ),
                    "sam_model_opt": (sams, ), 
                    "sam_mode": (["AUTO", "Prefer GPU", "CPU"],),
             
                    "guide_size": ("FLOAT", {"default": 512, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    "guide_size_for": ("BOOLEAN", {"default": True, "label_on": "bbox", "label_off": "crop_region"}),
                    "max_size": ("FLOAT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
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
                    "drop_size": ("INT", {"min": 1, "max": nodes.MAX_RESOLUTION, "step": 1, "default": 10}),                     
                    "cycle": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                    },
                "optional": {
                    "image_opt": ("IMAGE",),
                    "wildcard": ("STRING", {"forceInput": True}),
                    "detailer_hook": ("DETAILER_HOOK",),
                    #"wildcard": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                    "inpaint_model": ("BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}),
                    "noise_mask_feather": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                    "scheduler_func_opt": ("SCHEDULER_FUNC",),
                },     
                "hidden": {
                    "my_unique_id": "UNIQUE_ID",
                    "extra_pnginfo": "EXTRA_PNGINFO",}
            }

    RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE", "IMAGE", "IMAGE", "MASK", "IMAGE",)
    RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE", "CROPPED_REFINED", "CROPPED_ALPHA", "MASK", "CNET_IMAGES",)
    OUTPUT_IS_LIST = (False, False, True, True, False, True,)    
    FUNCTION = "doit_ed"
    CATEGORY = "Efficiency Nodes/Image"
    DESCRIPTION = "This node enhances details by automatically detecting specific objects in the input image using detection models (bbox, segm, sam) and regenerating the image by enlarging the detected area based on the guide size.\nAlthough this node is specialized to simplify the commonly used facial detail enhancement workflow, it can also be used for various automatic inpainting purposes depending on the detection model."

    def doit_ed(self, context, set_seed_cfg_sampler, bbox_detector, segm_detector_opt, sam_model_opt, sam_mode, 
            guide_size, guide_size_for, 
            max_size, seed, steps, cfg, sampler_name, scheduler, denoise, feather, noise_mask, force_inpaint,
            bbox_threshold, bbox_dilation, bbox_crop_factor,
            sam_detection_hint, sam_dilation, sam_threshold, sam_bbox_expansion, sam_mask_hint_threshold,
            sam_mask_hint_use_negative, drop_size, wildcard="", image_opt=None, cycle=1,
            detailer_hook=None, inpaint_model=False, noise_mask_feather=0, 
            scheduler_func_opt=None, my_unique_id=None, extra_pnginfo=None):

        _, model, clip, vae, positive, negative, image, c_seed, c_steps, c_cfg, c_sampler, c_scheduler = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative",  "images", "seed", "steps", "cfg", "sampler", "scheduler"])

        # GET PROPERTIES #  
        properties = self.get_properties(extra_pnginfo, my_unique_id)

        if image_opt is not None:       
            image = image_opt
            print(f"FaceDetailer ED: Using image_opt instead of context image.")

        if set_seed_cfg_sampler == "from context":
            if c_seed is None:
                raise Exception("FaceDetailer ED: no seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
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

        bbox_detector = ED_Util.ultra_detector_model(bbox_detector, "bbox")
        segm_detector_opt = ED_Util.ultra_detector_model(segm_detector_opt, "segm")
        sam_model_opt = ED_Util.load_sam_model(sam_model_opt, sam_mode)                
        
        # GITS
        scheduler = "GITS[coeff=1.2]" if scheduler == "GITS" else scheduler
        
        if 'FaceDetailer' not in NODES:
            ED_Util.try_install_custom_node('ComfyUI Impact Pack', 'https://github.com/ltdrdata/ComfyUI-Impact-Pack')

        result_img, result_cropped_enhanced, result_cropped_enhanced_alpha, result_mask, _, result_cnet_images = \
            NODES['FaceDetailer']().doit(image, model, clip, vae, guide_size, guide_size_for, max_size, 
            seed, steps, cfg, sampler_name, scheduler, positive, negative, denoise, feather, noise_mask, force_inpaint,
            bbox_threshold, bbox_dilation, bbox_crop_factor, sam_detection_hint, sam_dilation, 
            sam_threshold, sam_bbox_expansion, sam_mask_hint_threshold,
            sam_mask_hint_use_negative, drop_size, bbox_detector, wildcard, cycle=cycle,
            sam_model_opt=sam_model_opt, segm_detector_opt=segm_detector_opt, detailer_hook=detailer_hook, 
            inpaint_model=inpaint_model, noise_mask_feather=noise_mask_feather,
            scheduler_func_opt=scheduler_func_opt, tiled_encode=properties['tiled_vae_decode'], tiled_decode=properties['tiled_vae_decode'])

        context = new_context_ed(context, images=result_img) #RE 
        return (context, result_img, result_cropped_enhanced, result_cropped_enhanced_alpha, result_mask, result_cnet_images,)

    @staticmethod
    def get_properties(extra_pnginfo, my_unique_id):
        properties = {
            "tiled_vae_decode": False,
        }
        
        if extra_pnginfo and "workflow" in extra_pnginfo:
            workflow = extra_pnginfo["workflow"]
            for node in workflow["nodes"]:
                if node["id"] == int(my_unique_id):
                    properties['tiled_vae_decode'] = node["properties"]["Use tiled VAE decode"]

        return properties


##############################################################################################################
# Mask Detailer ED
class MaskDetailer_ED():
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "context": ("RGTHREE_CONTEXT",),
                    "set_seed_cfg_sampler": (list(KSampler_ED.SET_SEED_CFG_SAMPLER.keys()), {"default": "from context"}),

                    "guide_size": ("FLOAT", {"default": 512, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    "guide_size_for": ("BOOLEAN", {"default": True, "label_on": "mask bbox", "label_off": "crop region"}),
                    "max_size": ("FLOAT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    "mask_mode": ("BOOLEAN", {"default": True, "label_on": "masked only", "label_off": "whole"}),

                    "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                    "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                    "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                    "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                    "scheduler": (SCHEDULERS,),
                    "denoise": ("FLOAT", {"default": 0.5, "min": 0.0001, "max": 1.0, "step": 0.01}),

                    "feather": ("INT", {"default": 5, "min": 0, "max": 100, "step": 1}),
                    "crop_factor": ("FLOAT", {"default": 3.0, "min": 1.0, "max": 10, "step": 0.1}),
                    "drop_size": ("INT", {"min": 1, "max": nodes.MAX_RESOLUTION, "step": 1, "default": 10}),
                    "refiner_ratio": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                    "batch_size": ("INT", {"default": 1, "min": 1, "max": 100}),

                    "cycle": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                },
                "optional": {
                    "detailer_hook": ("DETAILER_HOOK",),
                    "inpaint_model": ("BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}),
                    "noise_mask_feather": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                    "bbox_fill": ("BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}),
                    "contour_fill": ("BOOLEAN", {"default": True, "label_on": "enabled", "label_off": "disabled"}),
                    "scheduler_func_opt": ("SCHEDULER_FUNC",),
                },
                "hidden": {"my_unique_id": "UNIQUE_ID",},
            }

    RETURN_TYPES = ("RGTHREE_CONTEXT", "IMAGE", "IMAGE", "IMAGE", )
    RETURN_NAMES = ("CONTEXT", "OUTPUT_IMAGE", "CROPPED_REFINED", "CROPPED_ALPHA", )
    OUTPUT_IS_LIST = (False, False, True, True,)
    FUNCTION = "doit_ed"

    CATEGORY = "Efficiency Nodes/Image"

    @staticmethod
    def mask_sampling(image, mask, model, clip, vae, positive, negative, guide_size, guide_size_for, max_size, mask_mode,
            seed, steps, cfg, sampler_name, scheduler, denoise,
            feather, crop_factor, drop_size, refiner_ratio, batch_size, cycle, 
            detailer_hook, inpaint_model, noise_mask_feather,
            bbox_fill=False, contour_fill=True, scheduler_func_opt=None):
        
        # GITS
        scheduler = "GITS[coeff=1.2]" if scheduler == "GITS" else scheduler
        
        basic_pipe = (model, clip, vae, positive, negative)
        
        if 'MaskDetailerPipe' not in NODES:
            ED_Util.try_install_custom_node('ComfyUI Impact Pack', 'https://github.com/ltdrdata/ComfyUI-Impact-Pack')

        enhanced_img_batch, cropped_enhanced_list, cropped_enhanced_alpha_list, _, _ = \
            NODES['MaskDetailerPipe']().doit(image, mask, basic_pipe, 
            guide_size, guide_size_for, max_size, mask_mode, seed, steps, cfg, sampler_name, 
            scheduler, denoise, feather, crop_factor, drop_size, refiner_ratio, 
            batch_size, cycle, None, detailer_hook, inpaint_model, noise_mask_feather,
            bbox_fill, contour_fill, scheduler_func_opt)
        return (enhanced_img_batch, cropped_enhanced_list, cropped_enhanced_alpha_list)                
        
    def doit_ed(self, context, set_seed_cfg_sampler, guide_size, guide_size_for, max_size, mask_mode,
            seed, steps, cfg, sampler_name, scheduler, denoise,
            feather, crop_factor, drop_size, refiner_ratio, batch_size, cycle=1,
            detailer_hook=None, inpaint_model=False, noise_mask_feather=0,
            bbox_fill=False, contour_fill=True, scheduler_func_opt=None, my_unique_id=None):

        _, model, clip, vae, positive, negative, image, c_batch, c_seed, c_steps, c_cfg, c_sampler, c_scheduler, mask = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative",  "images", "step_refiner", "seed", "steps", "cfg", "sampler", "scheduler", "mask"])

        # if image_opt is not None:
            # image = image_opt
            # print(f"MaskDetailer ED: Using image_opt instead of context image.")
        # if mask_opt is not None:
            # mask = mask_opt
            # print(f"MaskDetailer ED: Using mask_opt instead of context mask.")

        if set_seed_cfg_sampler == "from context":
            if c_seed is None:
                raise Exception("MaskDetailer ED: no seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
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
                # batch_size = c_batch
                # PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "batch_size", "type": "text", "data": batch_size})
        elif set_seed_cfg_sampler =="from node to ctx":
            context = new_context_ed(context, seed=seed, cfg=cfg, sampler=sampler_name, scheduler=scheduler)      
        
        enhanced_img_batch, cropped_enhanced_list, cropped_enhanced_alpha_list = \
            MaskDetailer_ED.mask_sampling(image, mask, model, clip, vae, positive, negative,
            guide_size, guide_size_for, max_size, mask_mode,
            seed, steps, cfg, sampler_name, scheduler, denoise,
            feather, crop_factor, drop_size, refiner_ratio, batch_size, cycle,
            detailer_hook, inpaint_model, noise_mask_feather,
            bbox_fill, contour_fill, scheduler_func_opt)

        context = new_context_ed(context, images=enhanced_img_batch) #RE 
        return (context, enhanced_img_batch, cropped_enhanced_list, cropped_enhanced_alpha_list,)

##############################################################################################################
# Detailer (SEGS) ED
class DetailerForEach_ED():
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "context": ("RGTHREE_CONTEXT",),
                    "segs": ("SEGS", ),
                    "set_seed_cfg_sampler": (list(KSampler_ED.SET_SEED_CFG_SAMPLER.keys()), {"default": "from context"}),

                    "guide_size": ("FLOAT", {"default": 512, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
                    "guide_size_for": ("BOOLEAN", {"default": True, "label_on": "mask bbox", "label_off": "crop region"}),
                    "max_size": ("FLOAT", {"default": 1024, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
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
                    "scheduler_func_opt": ("SCHEDULER_FUNC",),
                },
                "hidden": {
                    "my_unique_id": "UNIQUE_ID",
                    "extra_pnginfo": "EXTRA_PNGINFO",}
            }

    RETURN_TYPES = ("RGTHREE_CONTEXT", "SEGS", "IMAGE", "IMAGE", "IMAGE", "IMAGE", )
    RETURN_NAMES = ("CONTEXT", "SEGS", "OUTPUT_IMAGE", "CROPPED_REFINED", "CROPPED_REFINED_ALPHA", "CNET_IMAGES",)
    OUTPUT_IS_LIST = (False, False, False, True, True, True)
    
    FUNCTION = "doit_ed"

    CATEGORY = "Efficiency Nodes/Image"
    DESCRIPTION = "It enhances details by inpainting each region within the detected area bundle (SEGS) after enlarging them based on the guide size."    
        
    def doit_ed(self, context, set_seed_cfg_sampler, segs, guide_size, guide_size_for, max_size, 
            seed, steps, cfg, sampler_name, scheduler,
            denoise, feather, noise_mask, force_inpaint, wildcard, cycle=1,
            image_opt=None, detailer_hook=None, refiner_basic_pipe_opt=None,
            inpaint_model=False, noise_mask_feather=0, 
            scheduler_func_opt=None, my_unique_id=None, extra_pnginfo=None):
        
        _, model, clip, vae, positive, negative, image, c_batch, c_seed, c_steps, c_cfg, c_sampler, c_scheduler, mask = context_2_tuple_ed(context,["model", "clip", "vae", "positive", "negative",  "images", "step_refiner", "seed", "steps", "cfg", "sampler", "scheduler", "mask"])

        # GET PROPERTIES #  
        properties = self.get_properties(extra_pnginfo, my_unique_id)

        if image_opt is not None:
            image = image_opt
            print(f"Detailer (SEGS) ED: Using image_opt instead of context image.")
        
        if len(image) > 1:
            raise Exception('[Impact Pack] ERROR: Detailer (SEGS) ED does not allow image batches.\nPlease refer to https://github.com/ltdrdata/ComfyUI-extension-tutorials/blob/Main/ComfyUI-Impact-Pack/tutorial/batching-detailer.md for more information.')

        if set_seed_cfg_sampler == "from context":
            if c_seed is None:
                raise Exception("Detailer (SEGS) ED: no seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
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

        # GITS
        scheduler = "GITS[coeff=1.2]" if scheduler == "GITS" else scheduler

        if 'DetailerForEachDebug' not in NODES:
            ED_Util.try_install_custom_node('ComfyUI Impact Pack', 'https://github.com/ltdrdata/ComfyUI-Impact-Pack')

        enhanced_img, _, cropped_enhanced, cropped_enhanced_alpha, cnet_pil_list = \
            NODES['DetailerForEachDebug']().doit(image, segs, model, clip, vae, guide_size, 
            guide_size_for, max_size, seed, steps, cfg, sampler_name, scheduler, positive, negative, denoise,
            feather, noise_mask, force_inpaint, wildcard, detailer_hook=detailer_hook,
            cycle=cycle, inpaint_model=inpaint_model, noise_mask_feather=noise_mask_feather,
            scheduler_func_opt=scheduler_func_opt, tiled_encode=properties['tiled_vae_decode'], tiled_decode=properties['tiled_vae_decode'])

        context = new_context_ed(context, images=enhanced_img) #RE 
        return (context, segs, enhanced_img, cropped_enhanced, cropped_enhanced_alpha, cnet_pil_list,)
        
    @staticmethod
    def get_properties(extra_pnginfo, my_unique_id):
        properties = {
            "tiled_vae_decode": False,
        }
        
        if extra_pnginfo and "workflow" in extra_pnginfo:
            workflow = extra_pnginfo["workflow"]
            for node in workflow["nodes"]:
                if node["id"] == int(my_unique_id):
                    properties['tiled_vae_decode'] = node["properties"]["Use tiled VAE decode"]

        return properties
        

##############################################################################################################
# Ultimate SD Upscale ED
class UltimateSDUpscaleED():
    SET_TILE_SIZE_FROM = {
        "Image size": 1,
        "Canvas size": 2,
        "Node setting": 3,
    }
    # The modes available for Ultimate SD Upscale
    MODES = {
        "Linear": 1,
        "Chess": 2,
        "None": 3,
    }
    # The seam fix modes
    SEAM_FIX_MODES = {
        "None": 1,
        "Band Pass": 2,
        "Half Tile": 3,
        "Half Tile + Intersections": 4,
    }
    @classmethod
    def INPUT_TYPES(s):
        return {"required": 
                {
                "context": ("RGTHREE_CONTEXT",),
                "set_seed_cfg_sampler": (list(KSampler_ED.SET_SEED_CFG_SAMPLER.keys()), {"default": "from context"}),
                "upscale_model": (folder_paths.get_filename_list("upscale_models"), ),
                "upscale_by": ("FLOAT", {"default": 2, "min": 0.05, "max": 4, "step": 0.05}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "step": 1}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (SCHEDULERS,),                        
                "denoise": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                # Upscale Params
                "mode_type": (list(s.MODES.keys()),),
                #"mode_type": UltimateSDUpscale().INPUT_TYPES()["required"]["mode_type"],
                "set_tile_size_from": (list(s.SET_TILE_SIZE_FROM.keys()), {"default": "Image size"}),
                "tile_width": ("INT", {"default": 512, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
                "tile_height": ("INT", {"default": 512, "min": 64, "max": nodes.MAX_RESOLUTION, "step": 8}),
                "mask_blur": ("INT", {"default": 8, "min": 0, "max": 64, "step": 1}),
                "tile_padding": ("INT", {"default": 32, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                # Seam fix params
                "seam_fix_mode": (list(s.SEAM_FIX_MODES.keys()),),
                #"seam_fix_mode": UltimateSDUpscale().INPUT_TYPES()["required"]["seam_fix_mode"],
                "seam_fix_denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "seam_fix_width": ("INT", {"default": 64, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
                "seam_fix_mask_blur": ("INT", {"default": 8, "min": 0, "max": 64, "step": 1}),
                "seam_fix_padding": ("INT", {"default": 16, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 8}),
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
                raise Exception("UltimateSDUpscale ED: no seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
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
            tile_width, tile_height = ED_Util.get_image_size(image)
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "tile_width", "type": "text", "data": tile_width})
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "tile_height", "type": "text", "data": tile_height})
        elif set_tile_size_from == "Canvas size":
            tile_width, tile_height = ED_Util.get_image_size(image)
            tile_height = tile_height * upscale_by
            tile_width = tile_width * upscale_by
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "tile_width", "type": "text", "data": tile_width})
            PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "tile_height", "type": "text", "data": tile_height})
        
        upscaler = ED_Util.load_upscale_model(upscale_model)

        if 'UltimateSDUpscale' not in NODES:
            ED_Util.try_install_custom_node('UltimateSDUpscale', 'https://github.com/ssitu/ComfyUI_UltimateSDUpscale')

        tensor = NODES['UltimateSDUpscale']().upscale(image, model, 
                positive, negative, vae, upscale_by, seed,
                steps, cfg, sampler_name, scheduler, denoise, upscaler,
                mode_type, tile_width, tile_height, mask_blur, tile_padding,
                seam_fix_mode, seam_fix_denoise, seam_fix_mask_blur,
                seam_fix_width, seam_fix_padding, force_uniform_tiles, tiled_decode)[0]
        
        context = new_context_ed(context, images=tensor) #RE        
        return (context, tensor, image,)

#######################################################################################################
# SUPIR UPSCALER ED
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

    def upscale(self, upscale_model, image, upscale_by, rescale_method):
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
            upscaler = ED_Util.load_upscale_model(upscale_model)
            upscaled_image = self.upscale(upscaler, image, upscale_by, rescale_method)
        else:
            upscaled_image = image

        if 'SUPIR_model_loader_v2' not in NODES:
            ED_Util.try_install_custom_node('ComfyUI-SUPIR', 'https://github.com/kijai/ComfyUI-SUPIR')

        sup_model, sup_vae = NODES['SUPIR_model_loader_v2']().process(supir_model, diffusion_dtype,
            fp8_unet, model, clip, vae, high_vram=False)
        return (context, sup_model, sup_vae, upscaled_image)

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
                "set_seed_cfg_sampler": (list(KSampler_ED.SET_SEED_CFG_SAMPLER.keys()), {"default": "from context"}),
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
                raise Exception("UltimateSDUpscale ED: no seed, cfg, sampler, scheduler in the context.\n\n\n\n\n\n")
            else:
                seed = c_seed
                PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "seed", "type": "text", "data": seed})
                # if c_steps is not None:
                    # steps = c_steps
                    # PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "steps", "type": "text", "data": steps})
                cfg = c_cfg
                PromptServer.instance.send_sync("ed-node-feedback", {"node_id": my_unique_id, "widget_name": "cfg", "type": "text", "data": cfg})
        elif set_seed_cfg_sampler =="from node to ctx":
            context = new_context_ed(context, seed=seed, cfg=cfg)
    
        if 'SUPIR_first_stage' not in NODES:
            ED_Util.try_install_custom_node('ComfyUI-SUPIR', 'https://github.com/kijai/ComfyUI-SUPIR')

        # SUPIR_first_stage
        SUPIR_vae2, denoised_image, denoised_latent = NODES['SUPIR_first_stage']().process(SUPIR_vae, image_opt, encoder_dtype, use_tiled_vae, vae_tile_size, vae_tile_size)
    
        # SUPIR_conditioner
        positive_encoded, negative_encoded = NODES['SUPIR_conditioner']().condition(SUPIR_model, denoised_latent, positive_prompt, negative_prompt, captions="")
    
        # SUPIR_encode
        SUPIR_latent = NODES['SUPIR_encode']().encode(SUPIR_vae2, denoised_image, encoder_dtype, use_tiled_vae, vae_tile_size)[0]
    
        # SUPIR_sample
        SUPIR_latent = NODES['SUPIR_sample']().sample(SUPIR_model, SUPIR_latent, steps, seed, 
            cfg, EDM_s_churn, s_noise, positive_encoded, negative_encoded, cfg, control_scale_start, control_scale_end, 
            restore_cfg, keep_model_loaded, DPMPP_eta, sampler, sampler_tile_size=1024, sampler_tile_stride=512)[0]
        
        # SUPIR_decode
        output_image = NODES['SUPIR_decode']().decode(SUPIR_vae, SUPIR_latent, use_tiled_vae, vae_tile_size)[0]
        context = new_context_ed(context, images=output_image)
        
        return (context, output_image, source_image)


##############################################################################################################
# NODE MAPPING
##############################################################################################################

NODE_CLASS_MAPPINGS = {
    #ED
    "Efficient Loader 💬ED": EfficientLoader_ED,
    "KSampler (Efficient) 💬ED": KSampler_ED,
    "KSampler Text 💬ED": KSamplerTEXT_ED,    
    "Load Image 💬ED": LoadImage_ED,
    "Save Image 🔔ED": SaveImage_ED,
    #"Control Net Script 💬ED": Control_Net_Script_ED,
    "Refiner Script 💬ED": Refiner_Script_ED,
    "Embedding Stacker 💬ED": Embedding_Stacker_ED,
    "Wildcard Encode 💬ED": WildcardEncode_ED,
    "LoRA Stacker 💬ED": LoRA_Stacker_ED,
    "Int Holder 💬ED": Int_Holder_ED,    
    "Regional Stacker 💬ED": Regional_Stacker_ED,
    "Regional Processor 💬ED": Regional_Processor_ED,
    "Regional Script 💬ED": Regional_Script_ED,
    "Context To BasicPipe": ContextToBasicPipe,
    "Context To DetailerPipe": ContextToDetailerPipe,
    "Get Booru Tag 💬ED": GetBooruTag_ED,
    "Simple Text 💬ED": SimpleText_ED,
    "TIPO Script 💬ED": TIPOScript_ED,
    
    "FaceDetailer 💬ED": FaceDetailer_ED,
    "MaskDetailer 💬ED": MaskDetailer_ED,
    "Detailer (SEGS) 💬ED": DetailerForEach_ED,
    "Ultimate SD Upscale 💬ED": UltimateSDUpscaleED,
    
    "SUPIR Model Loader 💬ED": SUPIR_Model_Loader_ED,
    "SUPIR Sampler 💬ED": SUPIR_Sampler_ED,
}



