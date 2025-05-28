import os
import shutil
# import win32com.client

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


copy_dict = {"user.css": {
                                        "file": "./html_resource/user.css",
                                        "target": "../../../python_embeded/Lib/site-packages/comfyui_frontend_package/static/user.css",
                                        "check": "no",},
                    "widgethider.js": {
                                        "file": "./html_resource/widgethider.js",
                                        "target": "../efficiency-nodes-comfyui/js/widgethider.js",
                                        "check": "yes",}

                    }


replaceLine_dict = {"efficeincy_nodes_py": {
                                        "file": "../efficiency-nodes-comfyui/efficiency_nodes.py",
                                        "target": '"ksampler_output_image": (["Images","Plot"],),},',
                                        "replacement": '"ksampler_output_image": (["Images","Plot"], {"default": "Plot"}),},',},
                            "impact_wildcard_py": {
                                        "file": "../ComfyUI-Impact-Pack/modules/impact/wildcards.py",
                                        "target": "print(f\"CLIP: {str.join(' + ', pass3_str)}\")",
                                        "replacement": "# print (f\"CLIP: {str.join(' + ', pass3_str)}\")",},
                          }


replace_icon_dict = {
                    "favicon.ico": {
                                        "file": "./html_resource/ComfyUI.ico",
                                        "target": "../../../python_embeded/Lib/site-packages/comfyui_frontend_package/static/assets/favicon.ico",
                                        "check": "yes",},
                    "favicon_progress_16x16": {
                                        "file": "./html_resource/favicon_progress_16x16",
                                        "target": "../../../python_embeded/Lib/site-packages/comfyui_frontend_package/static/assets/images/favicon_progress_16x16",
                                        "check": "folder",},
                    }

restore_icon_dict = {
                    "favicon.ico": {
                                        "file": "./html_resource/restore/favicon.ico",
                                        "target": "../../../python_embeded/Lib/site-packages/comfyui_frontend_package/static/assets/favicon.ico",
                                        "check": "yes",},
                    "favicon_progress_16x16": {
                                        "file": "./html_resource/restore/favicon_progress_16x16",
                                        "target": "../../../python_embeded/Lib/site-packages/comfyui_frontend_package/static/assets/images/favicon_progress_16x16",
                                        "check": "folder",},
                    }

short_cut_icon = "./html_resource/ComfyUI.ico"


def is_file_exist(filepath):
    if not os.path.isfile(filepath):
        print(f"File '{filepath}'does not exist.")
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
        print(f"File '{js_file}' has been modified.")
    

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
        print(f"File '{js_file}' has been modified.")


def replaceLineFromDict(replaceLine_dict):
    for key in replaceLine_dict:
        file_path = replaceLine_dict[key]["file"]
        target_line = replaceLine_dict[key]["target"]
        replacement_line = replaceLine_dict[key]["replacement"]
        replaceLineFromFile (file_path, target_line, replacement_line)

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
        print(f"File '{file_path}' has been modified.")


def copyFileFromDict(copy_dict):
    for key in copy_dict:
        file_path = copy_dict[key]["file"]
        target_file = copy_dict[key]["target"]
        check = copy_dict[key]["check"]
        copyFile(file_path, target_file, check)

def copyFile(file_path, target_file, check):
    if check == "yes" and not os.path.isfile(target_file):
        print(f"File '{target_file}' does not exist")
        return
    elif check == "folder":
        overwrite_folder(file_path, target_file)
    else:
        target_dir = os.path.dirname(target_file)
        if os.path.isdir(target_dir):
            shutil.copy2(file_path, target_file)
            print(f"File '{target_file}' copied.")
        else:
            print(f"Target directory '{target_dir}' does not exist.")
    

def overwrite_folder(source_dir, target_dir):
    if not os.path.exists(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return
    
    if not os.path.exists(target_dir):
        print(f"Target directory '{target_dir}' does not exist.")
        return

    # target_dir 내부의 모든 파일 삭제 (하위 폴더 없음 가정)
    for file in os.listdir(target_dir):
        file_path = os.path.join(target_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # source_dir에서 target_dir로 파일 복사
    for root, _, files in os.walk(source_dir):
        for file in files:
            src_file = os.path.join(root, file)
            relative_path = os.path.relpath(src_file, source_dir)
            dest_file = os.path.join(target_dir, relative_path)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(src_file, dest_file)
    
    print(f"Folder '{source_dir}' copied to:\n   {target_dir}")


def create_shortcut_with_vbs():
    # Windows가 아니면 종료
    if os.name != "nt":
        print("Creating ComfyUI shortcut can only be run on Windows.")
        return
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target = os.path.abspath(os.path.join(current_dir, "../../../run_nvidia_gpu.bat"))
    icon = os.path.abspath(os.path.join(current_dir, short_cut_icon))
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop, "ComfyUI.lnk")

    if os.path.isfile(shortcut_path):
        os.remove(shortcut_path)
        print(f"Shortcut '{shortcut_path}' removed.")

    vbs_script = f'''
Set WshShell = WScript.CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{shortcut_path}")
Shortcut.TargetPath = "{target}"
Shortcut.WorkingDirectory = "{os.path.dirname(target)}"
Shortcut.IconLocation = "{icon}"
Shortcut.Save
'''

    vbs_path = os.path.join(current_dir, "create_shortcut.vbs")
    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(vbs_script.strip())

    os.system(f'cscript //nologo "{vbs_path}"')
    os.remove(vbs_path)

    print(f"Shortcut created at: {shortcut_path}")

def get_user_choice():
    while True:
        choice = input("\n\n\n>>Would you like to change ComfyUI's favicon and create a desktop shortcut with the new icon?\n     (ComfyUI의 파비콘을 바꾸고 바탕화면에 바뀐 아이콘의 바로가기를 만들겠습니까?) y/n /r(restore/복구)").strip().lower()
        if choice in ['y', 'n', 'r']:
            return choice
        else:
            print("Invalid input. Please enter 'y', 'n', or 'r'.")

###################    Main

printout = "Copy of files and disabling of unnecessary JS files"
print ("\n")

try:
    copyFileFromDict(copy_dict)
except Exception as e:
    print(f"\n\n\n[ERROR] efficiency nodes ED: An error occurred while copy files.\n{e}")
try:
    for file in annotating_js_files:
        annotate_file(file)
except Exception as e:
    print(f"\n\n\n[ERROR] efficiency nodes ED: An error occurred while annotating js files.\n{e}")
try:
    replaceLineFromDict(replaceLine_dict)
except Exception as e:
    print(f"\n\n\n[ERROR] efficiency nodes ED: An error occurred while replace python codes.\n{e}")

user_choice = get_user_choice()

if user_choice == 'y':
    copyFileFromDict(replace_icon_dict)
    create_shortcut_with_vbs()
elif user_choice == 'n':
    print("ok.")
elif user_choice == 'r':
    copyFileFromDict(restore_icon_dict)

print(f"\n\nEfficiency Nodes ED: {printout} is complete.\n\n")
    

    
