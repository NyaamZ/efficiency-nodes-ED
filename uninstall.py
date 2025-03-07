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

impact_wildcard_py = "../ComfyUI-Impact-Pack/modules/impact/wildcards.py"

read_css_folder = "./user_css/"
write_css_folder = "../../../python_embeded/Lib/site-packages/comfyui_frontend_package/static/"

def annotate_file(js_file):
    contents = []
    if os.path.isfile(js_file):
        with open(js_file, 'r', encoding='UTF8') as f:
            contents = f.readlines()
        with open(js_file, 'w', encoding='UTF8') as f:
            for c in contents:
                if c[:5] == "//** ":
                    f.write(c)
                else:
                    f.write("//** "+c)

def restore_annotate_file(js_file):
    contents = []
    if os.path.isfile(js_file):
        with open(js_file, 'r', encoding='UTF8') as f:
            contents = f.readlines()
        with open(js_file, 'w', encoding='UTF8') as f:
            for c in contents:
                if c[:5] == "//** ":
                    f.write(c[5:])
                else:
                    f.write(c)

def annotate_wildcard(py_file):
    contents = []
    if os.path.isfile(py_file):
        with open(py_file, 'r', encoding='UTF8') as f:
            contents = f.readlines()
        with open(py_file, 'w', encoding='UTF8') as f:
            for c in contents:
                if 'print(f"CLIP: {str.join('  in c and not "## from ED ##" in c:
                    f.write("## from ED ##" + c)
                else:
                    f.write(c)

def copy_user_css():
    if os.path.isfile(write_css_folder + "user.css"):
        os.remove(write_css_folder + "user.css")
    shutil.copy(read_css_folder + "user.css", write_css_folder + "user.css")
    
def restore_user_css():
    if os.path.isfile(write_css_folder + "user.css"):
        os.remove(write_css_folder + "user.css")
    if os.path.isfile(write_css_folder + "user.css.old"):
        os.rename(write_css_folder + "user.css.old", write_css_folder + "user.css")
    else:
        with open(write_css_folder + "user.css", 'w', encoding='UTF8') as f:
            f.write("/* Put custom styles here */")
            
try:
    printout = "uninstall"
    
    for file in annotating_js_files:
        restore_annotate_file(file)
    restore_user_css()
    print(f"Efficiency Nodes ED: Attempting to {printout} success!")
    
except Exception as e:
    print("[ERROR] efficiency nodes ED: An error occurred while annotating the file.")
    
