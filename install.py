import os
import shutil
import sys
import json
import csv
import re

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
        choice = input("\n\n\n>>Would you like to change ComfyUI's favicon and create a desktop shortcut with the new icon?\n     (y를 선택하면 ComfyUI의 웹 파비콘을 여우귀 소녀로 바꾸고 바탕화면에 같은 아이콘의 바로가기를 만듭니다.)\n\n>>y/n/r(restore/복구)").strip().lower()
        if choice in ['y', 'n', 'r']:
            return choice
        else:
            print("Invalid input. Please enter 'y', 'n', or 'r'.")

def save_api_code_to_json():
    gelbooruApikey_json = "./js/json/gelbooruApiKey.json"
    # 전체 API 코드 입력 받기
    api_code = input(">>").strip()
    
    if api_code == "z":        
        autocomplete_csv_to_json()
        quit()

    if "api_key=" not in api_code or "user_id=" not in api_code:
        print("Wrong api key!!")
        return

    # 리스트로 감싸기
    data = [api_code]

    # JSON 파일로 저장
    with open(gelbooruApikey_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{gelbooruApikey_json} 파일이 변경되었습니다.")



def autocomplete_csv_to_json():
    def translate_category(category):        
        ## Meta - 이미지 정보
        if "이미지 정보" in category:
            return "meta"
        
        ## Source - 출처 및 작가
        if "작품" in category:
            return "copyright"
        if "캐릭터" in category:
            return "character"
        if "아티스트" in category:
            return "artist"
            
        ## Art & Composition - 아트 및 연출:
        if "표현 기호" in category:
            return "symbolic representation"
        if "아트 및 연출" in category:
            return "camera & composition"

        ## NSFW - 성인용:
        if "성적 요소 → 성적 신체 부위" in category:
            return "sensitive"
        if "성적 행위" in category:
            return "sexual acts & poses"
        if "성적 자세" in category:
            return "sexual acts & poses"
        if "성적 패션 및 노출" in category:
            return "sexual - other"
        if "성인용품" in category:
            return "sexual - other"
        if "분비물" in category:
            return "sensitive"
        if "성적 요소 → 상태 및 감정" in category:
            return "sexual acts & poses"
        if "성적 요소 → 기타" in category:
            return "sexual - other"

        ## Character - 인물:
        if "인원수 및 관계" in category:
            return "person"
        if "신체적 특징" in category:
            return "body"
        if "신체 부위" in category:
            return "body"
        if "종족 및 특성" in category:
            return "species & traits"
        if "상태 및 감정" in category:
            return "state & emotion"

        ## Pose - 자세:
        if "자세" in category:
            return "pose"

        ## Action - 행동:
        if "행동" in category:
            return "action"

        ## Fashion - 패션:
        if "헤어" in category:
            return "hair"
        if "액세서리" in category:
            return "accessory"
        if "의상" in category:
            return "clothing"
        if "속옷 및 양말류" in category:
            return "clothing"
        if "신발" in category:
            return "clothing"        
        if "치장 및 상태" in category:
            return "appearance"

        ## Object - 사물:
        if "무기" in category:
            return "object - weapon"

        if "사물" in category:
            return "object"

        ## Background - 배경:
        if "배경" in category:
            return "background"

        ## Concepts & Themes - 개념 및 테마:
        if "동물" in category:
            return "animals"
        if "개념 및 테마" in category:
            return "concepts & themes"

        ## Other - 기타:
        return "other"
        
    # 파일 경로
    csv_file = './html_resource/autocomplete.csv'
    json_file = './js/json/tag_category.json'

    # 결과 저장 딕셔너리
    result = {}

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue  # 잘못된 줄 스킵
            tag = row[0].strip()
            # \를 \\로 교체,"를 \"로 교체
            tag = tag.replace('\\', r'\\')   
            tag = tag.replace('"', r'\"')
            description = row[3].strip()

            # 대괄호 안에 있는 카테고리 추출
            match = re.search(r'\[([^\]]+)\]', description)
            if match:
                category = match.group(1)
                category = translate_category(category)
                result[tag] = [category]

    print(f"\n\n\n>>{csv_file}를 {json_file}으로 변환합니다.\n\n")
    
    # JSON 저장
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write('{\n')
        for i, (key, value) in enumerate(result.items()):
            comma = ',' if i < len(result) - 1 else ''
            line = f'  "{key}": {json.dumps(value, ensure_ascii=False)}{comma}\n'
            f.write(line)
        f.write('}')

    print("변환 완료:", json_file)


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
    print("\n\n!!To extract tags from Gelbooru using Get Booru Tag ED, an API key is required.")
    print("You can copy your API key from gelbooru.com by going to My Account > Options > API Access Credentials at the very bottom")
    print(f"Input Gelbooru API Key(&api_key=...&user_id=... )")
    print(f"\n!!Get Booru Tag ED에서 Gelbooru 태그를 추출하기 위해서는 Gelbooru api key가 필요합니다.")
    print(f"gelbooru.com 에서 My account > options > 맨 마지막 줄 API Access Credentials에서 api key를 복사할 수 있습니다.")
    print(f"(Gelbooru 로그인 필요, Gelbooru 태그 추출을 사용하지 않는다면 엔터를 눌러 스킵하세요.)")
    print(f"Gelbooru API Key 입력(&api_key=...&user_id=... 형식)")
    save_api_code_to_json()
    
    user_choice = get_user_choice()

    if user_choice == 'y':
        copyFileFromDict(replace_icon_dict)
        create_shortcut_with_vbs()
    elif user_choice == 'n':
        print("ok.")
    elif user_choice == 'r':
        copyFileFromDict(restore_icon_dict)

print(f"\n\nEfficiency Nodes ED: {printout} is complete.\n\n")
    

    
