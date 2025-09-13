import os
import shutil
import sys
import json
import csv
import re
from collections import OrderedDict


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
                                        "check": "no",}
                    }


replaceLine_dict = {"efficeincy_nodes_py": {
                                        "file": "../efficiency-nodes-comfyui/efficiency_nodes.py",
                                        "target": '"ksampler_output_image": (["Images","Plot"],),},',
                                        "replacement": '"ksampler_output_image": (["Images","Plot"], {"default": "Plot"}),},',},
                            "impact_wildcard_py": {
                                        "file": "../ComfyUI-Impact-Pack/modules/impact/wildcards.py",
                                        "target": "logging.info(f\"CLIP: {str.join(' + ', pass3_str)}\")",
                                        "replacement": "# logging.info(f\"CLIP: {str.join(' + ', pass3_str)}\")",},
                            "routes_model_info_py": {
                                        "file": "../rgthree-comfy/py/server/routes_model_info.py",
                                        "target": "if model_type not in ['loras', 'checkpoints']:",
                                        "replacement": "if model_type not in ['loras', 'checkpoints', 'embeddings']:",},
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

category_map_file = "./html_resource/category_map.json"    # major/minor → label
tags_input_file = "./html_resource/tags.json"         # 변환할 태그 데이터
tags_output_file = "./js/json/tag_category.json"    # 결과 저장
map_output_file = "./map_output_file.json"
ed_userDir = "./user"
ed_settings_file = "./user/ed_settings.json"

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

def replaceIconFavicon():
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
            choice = input("\n\n\nWould you like to change ComfyUI's favicon and create a desktop shortcut with the new icon?\n\n(y를 선택하면 ComfyUI의 웹 파비콘을 여우귀 소녀로 바꾸고 바탕화면에 같은 아이콘의 바로가기를 만듭니다.)\n\n>>y/n/r(restore/복구)").strip().lower()
            if choice in ['y', 'n', 'r']:
                return choice
            else:
                print("Invalid input. Please enter 'y', 'n', or 'r'.")
    
    user_choice = get_user_choice()

    if user_choice == 'y':
        copyFileFromDict(replace_icon_dict)
        create_shortcut_with_vbs()
    elif user_choice == 'n':
        print("ok.")
    elif user_choice == 'r':
        copyFileFromDict(restore_icon_dict)

def get_ed_settingsJson():
    if not os.path.exists(ed_userDir):
        os.mkdir(ed_userDir)
    if not os.path.exists(ed_settings_file):
        return None
    try:
        with open(ed_settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading JSON: {e}")
        return None



import json
import os

def save_gelbooru_api_key():
    def is_valid_api_key(key: str) -> bool:
        if not key:
            print("Gelbooru API Key SKIP!!")
            return False
        if "api_key=" not in key or "user_id=" not in key:
            print("Wrong Gelbooru API Key!!")
            return False
        return True

    # 기존 설정 불러오기
    settings_json = get_ed_settingsJson() or {}
    stored_api_key = settings_json.get("Gelbooru_api_key")


    # 안내 메시지
    print("\n\n\n\n\n!!To extract tags from Gelbooru using Get Booru Tag ED, an API key is required.")
    print("You can copy your API key from gelbooru.com: My Account > Options > API Access Credentials (bottom)")    
    print("\n(!!Get Booru Tag ED에서 Gelbooru 태그를 추출하려면 API key가 필요합니다.")
    print("gelbooru.com > My account > Options > API Access Credentials에서 복사 가능합니다.)")
    if stored_api_key:
        print(f"\n\n\nPreviously saved Gelbooru API Key exists. Press Enter to reuse it.")
        print(f"\n(이 전에 저장된 Gelbooru API가 존재합니다. Enter를 눌러 재사용 할 수 있습니다.)")
        print(f"Saved API Key(저장된 API 키): {stored_api_key}")
    else:
        print("\n\n\nInput Gelbooru API Key (&api_key=...&user_id=... format, Press Enter to skip)")
        print("\nGelbooru API Key를 입력 (&api_key=...&user_id=... 형식, Gelbooru 로그인 필요.)")
        print("                        (Gelbooru 태그 추출 기능을 사용을 안 할 경우 Enter로 스킵)")

    # 사용자 입력
    new_api_key = input("\n\n>> ").strip() or stored_api_key

    # 특수 명령 처리
    if new_api_key == "z":
        jsonFile_convert_tags(tags_input_file, category_map_file, tags_output_file)
        quit()
    if new_api_key == "zz":
        restructure_categories(tags_input_file, category_map_file, map_output_file)
        quit()

    if not is_valid_api_key(new_api_key):
        new_api_key = ""

    # JSON 저장
    settings_json["Gelbooru_api_key"] = new_api_key
    with open(ed_settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_json, f, indent=2, ensure_ascii=False)

    print(f"\n{ed_settings_file} 파일이 변경되었습니다.")

def restructure_categories(input_file, order_file, output_file):

    # 입력 JSON 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # order JSON 읽기 (키 순서 유지)
    with open(order_file, 'r', encoding='utf-8') as f:
        order_dict = json.load(f, object_pairs_hook=OrderedDict)
    
    # major -> minor set 매핑 (데이터에서 존재하는 minor)
    temp_dict = {}
    for item in data:
        major = item.get("major_categories", "Other")
        minor = item.get("minor_categories", "Other")
        if major not in temp_dict:
            temp_dict[major] = set()
        temp_dict[major].add(minor)
    
    # 결과 구성
    result = OrderedDict()
    for major, minor_order_dict in order_dict.items():
        minors_in_data = temp_dict.get(major, set())
        minors_ordered = OrderedDict()
        
        # order_file에 정의된 minor 순서대로 값 적용
        for minor, value in minor_order_dict.items():
            if minor in minors_in_data:
                minors_ordered[minor] = value
                minors_in_data.remove(minor)
        
        # 남은 minor는 마지막에 추가, 값은 빈 문자열
        for minor in sorted(minors_in_data):
            minors_ordered[minor] = ""
        
        result[major] = minors_ordered
    
    # JSON 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def jsonFile_convert_tags(tags_input_file, category_file, tags_output_file):

    # ----- 카테고리 매핑 읽기 -----
    with open(category_file, "r", encoding="utf-8") as f:
        category_map = json.load(f)

    # ----- 태그 데이터 읽기 -----
    with open(tags_input_file, "r", encoding="utf-8") as f:
        tag_data = json.load(f)

    # ----- 변환 함수 -----
    def convert_tags(tag_data, category_map):
        result = {}

        for tag in tag_data:
            # 영어 이름 공백 → 언더스코어
            english_name = tag["english_name"].replace(" ", "_")
            major = tag.get("major_categories", "")
            minor = tag.get("minor_categories", "")

            label = None
            if major in category_map and minor in category_map[major]:
                label = category_map[major][minor]

            if label:
                result[english_name] = [label]
            else:
                # 매핑 없는 경우 major::minor 표시
                result[english_name] = ["ERROR"]

        return result

    # ----- 변환 수행 -----
    converted = convert_tags(tag_data, category_map)

    # ----- JSON 저장 (배열 한 줄, 보기 좋게) -----
    with open(tags_output_file, "w", encoding="utf-8") as f:
        json.dump(converted, f, ensure_ascii=False, indent=2, separators=(',', ': '))

    print(f"변환 완료! 결과가 '{tags_output_file}'에 저장되었습니다.")

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

if len(sys.argv) > 1 and sys.argv[1] == "run_from_batch":
    save_gelbooru_api_key()
    replaceIconFavicon()

print(f"\n\nEfficiency Nodes ED: {printout} is complete.\n\n")
    

    
