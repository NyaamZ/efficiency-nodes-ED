import os
import shutil

annotating_js_files = [
            "../efficiency-nodes-comfyui/js/node_options/addLinks.js",
            "../efficiency-nodes-comfyui/js/node_options/addScripts.js",
            "../efficiency-nodes-comfyui/js/node_options/addXYinputs.js",
            "../efficiency-nodes-comfyui/js/node_options/modelInfo.js",
            "../efficiency-nodes-comfyui/js/node_options/setResolution.js",
            "../efficiency-nodes-comfyui/js/node_options/swapLoaders.js",
            "../efficiency-nodes-comfyui/js/node_options/swapSamplers.js",
            "../efficiency-nodes-comfyui/js/node_options/swapScripts.js",
            "../efficiency-nodes-comfyui/js/node_options/swapXYinputs.js",
            "../efficiency-nodes-comfyui/js/node_options/common/modelInfoDialog.js",
            ]

widgethider_js = "../efficiency-nodes-comfyui/js/widgethider.js"
new_widgethider_js = "./user_css/widgethider.js"

read_css_folder = "./user_css/"
write_css_folder = "../../../python_embeded/Lib/site-packages/comfyui_frontend_package/static/"

replace_dict = {"efficeincy_nodes_py": {
                                        "file": "../efficiency-nodes-comfyui/efficiency_nodes.py",
                                        "target": '"ksampler_output_image": (["Images","Plot"],),},',
                                        "replacement": '"ksampler_output_image": (["Images","Plot"], {"default": "Plot"}),},',},
                            "impact_wildcard_py": {
                                        "file": "../ComfyUI-Impact-Pack/modules/impact/wildcards.py",
                                        "target": "print(f\"CLIP: {str.join(' + ', pass3_str)}\")",
                                        "replacement": "# print (f\"CLIP: {str.join(' + ', pass3_str)}\")",},
                            # "impact_sampling_py_A": {
                                        # "file": "../ComfyUI-Impact-Pack/modules/impact/impact_sampling.py",
                                        # "target": "elif scheduler.startswith('GITS[coeff='):",
                                        # "replacement": "elif scheduler.startswith('GITS'):",},
                            # "impact_sampling_py_B": {
                                        # "file": "../ComfyUI-Impact-Pack/modules/impact/impact_sampling.py",
                                        # "target": "sigmas = nodes.NODE_CLASS_MAPPINGS['GITSScheduler']().get_sigmas(float(scheduler[11:-1]), steps, denoise=1.0)[0]",
                                        # "replacement": "sigmas = nodes.NODE_CLASS_MAPPINGS['GITSScheduler']().get_sigmas(1.20, steps, denoise=1.0)[0]",},
                          }


def replaceFromDict(replace_dict):
    for key in replace_dict:
        file_path = replace_dict[key]["file"]
        target_line = replace_dict[key]["target"]
        replacement_line = replace_dict[key]["replacement"]
        replaceLineFromFile (file_path, target_line, replacement_line)

def is_file_exist(filepath):
    if not os.path.isfile(filepath):
        print(f"File does not exist: {filepath}")
        return False
    return True

def annotate_file(js_file):
    if not is_file_exist(js_file):
        return
    
    contents = []
    modified = False
    if os.path.isfile(js_file):
        with open(js_file, 'r', encoding='UTF8') as f:
            contents = f.readlines()
        with open(js_file, 'w', encoding='UTF8') as f:
            for c in contents:
                if c[:5] == "//** ":
                    f.write(c)
                else:
                    f.write("//** "+c)
                    modified = True
                    
    if modified:
        print(f"File has been modified: {js_file}")
    

def restore_annotate_file(js_file):
    if not is_file_exist(js_file):
        return
    
    contents = []
    modified = False
    if os.path.isfile(js_file):
        with open(js_file, 'r', encoding='UTF8') as f:
            contents = f.readlines()
        with open(js_file, 'w', encoding='UTF8') as f:
            for c in contents:
                if c[:5] == "//** ":
                    f.write(c[5:])
                    modified = True
                else:
                    f.write(c)

    if modified:
        print(f"File has been modified: {js_file}")


def replaceLineFromFile(file_path, target_line, replacement_line):
    if not is_file_exist(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    modified = False
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped == target_line:
            indent = line[:line.index(target_line)]
            new_lines.append(indent + replacement_line+"\n")
            modified = True
        else:
            new_lines.append(line)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        print(f"File has been modified: {file_path}")

def widgethider_js_copy():
    shutil.copy2(new_widgethider_js, widgethider_js)
    print(f"File copied: {widgethider_js}")

def copy_user_css():
    if os.path.isdir(write_css_folder):
        if os.path.isfile(write_css_folder + "user.css"):
            os.remove(write_css_folder + "user.css")
        shutil.copy2(read_css_folder + "user.css", write_css_folder + "user.css")
        print(f"File copied: {write_css_folder + "user.css"}")
    else:
        print(f"Directory does not exist - {write_css_folder}")
    
def restore_user_css():
    if os.path.isdir(write_css_folder):
        if os.path.isfile(write_css_folder + "user.css"):
            os.remove(write_css_folder + "user.css")
        if os.path.isfile(write_css_folder + "user.css.old"):
            os.rename(write_css_folder + "user.css.old", write_css_folder + "user.css")
        else:
            with open(write_css_folder + "user.css", 'w', encoding='UTF8') as f:
                f.write("/* Put custom styles here */")




try:
    printout = "copy user.css and disable unnecessary js files"
    print ("\n")

    widgethider_js_copy()
    copy_user_css()
    for file in annotating_js_files:
        annotate_file(file)
    replaceFromDict(replace_dict)

    print(f"\n\nEfficiency Nodes ED: Attempting to {printout} success!\n\n")
    
except Exception as e:
    print(f"\n\n\n[ERROR] efficiency nodes ED: An error occurred while annotating the file.\n{e}")
    
