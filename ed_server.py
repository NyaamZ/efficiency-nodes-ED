import os
import json
from aiohttp import web

from server import PromptServer
import folder_paths
import shutil

routes = PromptServer.instance.routes

def get_param(request, param, default=None):
    """Gets a param from a request."""
    return request.rel_url.query[param] if param in request.rel_url.query else default


@routes.get('/ed_nodes/api/{type}/info/clear')
async def api_get_delete_model_info(request):
    model_type = request.match_info['type']
    files_param = get_param(request, 'files')

    if files_param is not None:
        files_param = files_param.split(',')

    api_response = {'model_type': model_type, 'files_param': files_param}

    # 파일 삭제 반복
    if files_param:
        for file_param in files_param:
            await delete_model_info(file_param, model_type)

    return web.json_response(api_response)

async def delete_model_info(file: str, model_type):
    file_path = get_folder_path(file, model_type)
    if file_path is None:
        return
    
    dir_name = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]  # 확장자 제거
    sha256_file = os.path.join(dir_name, f"{base_name}.sha256")
    txt_file = os.path.join(dir_name, f"{base_name}.txt")
    delete_filepath(sha256_file)
    delete_filepath(txt_file)
    
def delete_filepath(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"\033[36mUnnecessary file removed: {filepath}\033[0m")

def get_folder_path(file: str, model_type):
    file_path = folder_paths.get_full_path(model_type, file)
    if file_path and not file_exists(file_path):
        file_path = os.path.abspath(file_path)
    if not file_exists(file_path):
        file_path = None
    return file_path

def file_exists(path):
  if path is not None:
    return os.path.isfile(path)
  return False

@routes.get('/ed_nodes/api/{type}/info/openfolder')
async def api_get_open_model_info(request):
    model_type = request.match_info['type']
    files_param = get_param(request, 'files')

    if files_param is not None:
        files_param = files_param.split(',')

    api_response = {'model_type': model_type, 'files_param': files_param}

    # 파일 삭제 반복
    if files_param:        
        open_folder(files_param[0], model_type)

    return web.json_response(api_response)

def open_folder(file: str, model_type):
    file_path = get_folder_path(file, model_type)
    if file_path is None:
        return
    
    dir_name = os.path.dirname(file_path)
    os.startfile(dir_name)


################## from pysssss

@PromptServer.instance.routes.get("/ed_nodes/view/{name}")
async def view(request):
    name = request.match_info["name"]
    pos = name.index("/")
    type = name[0:pos]
    name = name[pos+1:]

    image_path = folder_paths.get_full_path(
        type, name)
    if not image_path:
        return web.Response(status=404)

    filename = os.path.basename(image_path)
    return web.FileResponse(image_path, headers={"Content-Disposition": f"filename=\"{filename}\""})

@PromptServer.instance.routes.get("/ed_nodes/images/{type}")
async def get_images(request):
    type = request.match_info["type"]
    names = folder_paths.get_filename_list(type)

    images = {}
    for item_name in names:
        file_name = os.path.splitext(item_name)[0]
        file_path = folder_paths.get_full_path(type, item_name)

        if file_path is None:
            continue

        file_path_no_ext = os.path.splitext(file_path)[0]

        for ext in ["png", "jpg", "jpeg", "preview.png", "preview.jpeg"]:
            if os.path.isfile(file_path_no_ext + "." + ext):
                images[item_name] = f"{type}/{file_name}.{ext}"
                break

    return web.json_response(images)
    
@PromptServer.instance.routes.post("/ed_nodes/save/{name}")
async def save_preview(request):
    name = request.match_info["name"]
    pos = name.index("/")
    type = name[0:pos]
    name = name[pos+1:]

    body = await request.json()

    dir = folder_paths.get_directory_by_type(body.get("type", "output"))
    subfolder = body.get("subfolder", "")
    full_output_folder = os.path.join(dir, os.path.normpath(subfolder))

    filepath = os.path.join(full_output_folder, body.get("filename", ""))

    if os.path.commonpath((dir, os.path.abspath(filepath))) != dir:
        return web.Response(status=400)

    image_path = folder_paths.get_full_path(type, name)
    image_path = os.path.splitext(
        image_path)[0] + os.path.splitext(filepath)[1]

    shutil.copyfile(filepath, image_path)

    return web.json_response({
        "image":  type + "/" + os.path.basename(image_path)
    })
    
@PromptServer.instance.routes.get("/ed_nodes/notedata/{name}")
async def load_notedata(request):
    name = request.match_info["name"]
    pos = name.index("/")
    type = name[0:pos]
    name = name[pos+1:]

    file_path = None
    if type == "embeddings" or type == "loras":
        name = name.lower()
        files = folder_paths.get_filename_list(type)
        for f in files:
            lower_f = f.lower()
            if lower_f == name:
                file_path = folder_paths.get_full_path(type, f)
            else:
                n = os.path.splitext(f)[0].lower()
                if n == name:
                    file_path = folder_paths.get_full_path(type, f)

            if file_path is not None:
                break
    else:
        file_path = folder_paths.get_full_path(
            type, name)
    if not file_path:
        return web.Response(status=404)
    
    note = {}
    file_no_ext = os.path.splitext(file_path)[0]

    info_file = file_no_ext + ".txt"
    if os.path.isfile(info_file):
        with open(info_file, "r") as f:
            note["pysssss.notes"] = f.read()

    return web.json_response(note)
    
@PromptServer.instance.routes.get("/ed_nodes/ed_settings")
async def get_ed_settings(request):
    dir = os.path.abspath(os.path.join(__file__, "../user"))
    file = os.path.join(dir, "ed_settings.json")
    if os.path.isfile(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return web.json_response(data)
    return web.json_response({"error": "file not found"}, status=404)
