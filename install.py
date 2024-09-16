import os
import shutil

annotating_file_list = ["../efficiency-nodes-comfyui/js/node_options/addLinks.js",
            "../efficiency-nodes-comfyui/js/node_options/addScripts.js",
            "../efficiency-nodes-comfyui/js/node_options/addXYinputs.js",
            "../efficiency-nodes-comfyui/js/node_options/modelInfo.js",
            "../efficiency-nodes-comfyui/js/node_options/setResolution.js",
            "../efficiency-nodes-comfyui/js/node_options/swapLoaders.js",
            "../efficiency-nodes-comfyui/js/node_options/swapSamplers.js",
            "../efficiency-nodes-comfyui/js/node_options/swapScripts.js",
            "../efficiency-nodes-comfyui/js/node_options/swapXYinputs.js"]

read_css_folder = "./user_css/"
write_css_folder = "../../web/"
user_css = "user.css"
    
def annotate_file(js_file):
    contents = []
    with open(js_file, 'r', encoding='UTF8') as f:
        contents = f.readlines()
    with open(js_file, 'w', encoding='UTF8') as f:
        for c in contents:
            if c[:5] == "//** ":
                f.write(c)
            else:
                f.write("//** "+c)
    #os.chmod( js_file, stat.FILE_ATTRIBUTE_READONLY )

def restore_annotate_file(js_file):
    contents = []
    #os.chmod( js_file, stat.S_IWRITE )
    with open(js_file, 'r', encoding='UTF8') as f:
        contents = f.readlines()
    with open(js_file, 'w', encoding='UTF8') as f:
        for c in contents:
            if c[:5] == "//** ":
                f.write(c[5:])
            else:
                f.write(c)

def copy_user_css():
    if os.path.isfile(write_css_folder + user_css):
        os.rename(write_css_folder +  user_css, write_css_folder + user_css + ".old")    
    shutil.copy(read_css_folder + user_css, write_css_folder + user_css)
    
def restore_user_css():
    if os.path.isfile(write_css_folder + user_css):
        os.remove(write_css_folder + user_css)
    if os.path.isfile(write_css_folder + user_css + ".old"):
        os.rename(write_css_folder + user_css + ".old", write_css_folder + user_css)
    else:
        with open(write_css_folder + user_css, 'w', encoding='UTF8') as f:
            f.write("/* Put custom styles here */")
            
try:
    printout = "Install"
    
    for file in annotating_file_list:
        annotate_file(file)
    copy_user_css()
    print(f"Efficiency Nodes ED: Attempting to {printout} success!")
    
except Exception as e:
    print("[ERROR] efficiency nodes ED: An error occurred while annotating the file.")
    
