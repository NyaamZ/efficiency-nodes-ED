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
widgethider_js = "../efficiency-nodes-comfyui/js/widgethider.js"

read_css_folder = "./user_css/"
write_css_folder = "../../../python_embeded/Lib/site-packages/comfyui_frontend_package/static/"

def is_file_exist(filepath):
    if not os.path.isfile(filepath):
        print(f"파일이 존재하지 않습니다: {filepath}")
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
        print(f"파일이 수정되었습니다: {js_file}")
    

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
        print(f"파일이 수정되었습니다: {js_file}")

def annotate_wildcard(py_file):
    if not is_file_exist(py_file):
        return
    
    contents = []
    modified = False
    if os.path.isfile(py_file):
        with open(py_file, 'r', encoding='UTF8') as f:
            contents = f.readlines()
        with open(py_file, 'w', encoding='UTF8') as f:
            for c in contents:
                if 'print(f"CLIP: {str.join('  in c and not "## from ED ##" in c:
                    f.write("## from ED ##" + c)
                    modified = True
                else:
                    f.write(c)
                    
    if modified:
        print(f"파일이 수정되었습니다: {js_file}")


def widgethider_js_modify(js_file):
    if not is_file_exist(js_file):
        return
    
    with open(js_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    target_line = 'for (const w of node.widgets || []) {'
    modified_line = 'for  (const w of node.widgets || []) {\n'
    insert_line_template = 'if (!nodeWidgetHandlers[node.comfyClass]) return;\n'

    modified = False
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped == target_line:
            indent = line[:line.index('for')]
            new_lines.append(indent + insert_line_template)
            new_lines.append(indent + modified_line)
            modified = True
        else:
            new_lines.append(line)

    if modified:
        with open(js_file, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        print(f"\n파일이 수정되었습니다: {js_file}")

def copy_user_css():
    if os.path.isdir(write_css_folder):
        if os.path.isfile(write_css_folder + "user.css"):
            os.remove(write_css_folder + "user.css")
        shutil.copy(read_css_folder + "user.css", write_css_folder + "user.css")
    else:
        print(f"\nDirectory does not exist - {write_css_folder}")
    
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
    printout = "uninstall"
    print ("\n")
    for file in annotating_js_files:
        restore_annotate_file(file)
    restore_user_css()
    print(f"\n\nEfficiency Nodes ED: Attempting to {printout} success!")
    
except Exception as e:
    print("[ERROR] efficiency nodes ED: An error occurred while annotating the file.")
    
