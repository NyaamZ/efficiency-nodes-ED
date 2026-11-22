import os
import json
import aiohttp
from urllib.parse import parse_qs
from aiohttp import web

from server import PromptServer
import folder_paths
import shutil

# ============================================================
# ED Booru API
# ============================================================

@PromptServer.instance.routes.post("/ed/booru_tags")
async def ed_booru_tags(request):

    try:
        print("[ED] ed_booru API endpoint called")
        data = await request.json()

        booru = data.get("booru", "").lower()
        post_id = str(data.get("id", "")).strip()
        api_key = data.get("api_key", "")

        if not post_id.isdigit():
            return web.json_response(
                {"error": "Invalid post ID"},
                status=400
            )

        timeout = aiohttp.ClientTimeout(total=20)

        headers = {
            "User-Agent": "ComfyUI-efficiency-nodes-ED/1.0"
        }

        async with aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        ) as session:

            # ------------------------------------------------
            # Danbooru / Aibooru
            # ------------------------------------------------
            if booru in ("danbooru", "aibooru"):

                if booru == "danbooru":
                    base = "https://danbooru.donmai.us"
                else:
                    base = "https://aibooru.online"

                url = f"{base}/posts/{post_id}.json"

                # Danbooru에 식별 가능한 User-Agent 전달
                headers = {
                    "User-Agent": (
                        "ComfyUI-efficiency-nodes-ED/1.0"
                    ),
                    "Accept": "application/json"
                }

                print(f"[ED Booru] Request: {url}")

                async with session.get(
                    url,
                    headers=headers
                ) as response:

                    print(
                        f"[ED Booru] {booru} "
                        f"HTTP Status: {response.status}"
                    )

                    if response.status != 200:

                        error_body = await response.text()

                        print(
                            f"[ED Booru] Response: "
                            f"{error_body[:1000]}"
                        )

                        return web.json_response(
                            {
                                "error": (
                                    f"{booru} HTTP {response.status}"
                                ),
                                "details": error_body[:1000]
                            },
                            status=502
                        )

                    result = await response.json()

            # ------------------------------------------------
            # Gelbooru
            # ------------------------------------------------
            elif booru == "gelbooru":

                url = "https://gelbooru.com/index.php"

                params = {
                    "page": "dapi",
                    "s": "post",
                    "q": "index",
                    "json": "1",
                    "id": post_id,
                }

                # 기존 ed_settings 형식 지원
                # 예: &api_key=xxxx&user_id=123
                if api_key:

                    parsed = parse_qs(
                        api_key.lstrip("&").replace("?", "")
                    )

                    if "api_key" in parsed:
                        params["api_key"] = parsed["api_key"][0]

                    if "user_id" in parsed:
                        params["user_id"] = parsed["user_id"][0]

                async with session.get(
                    url,
                    params=params
                ) as response:

                    if response.status != 200:
                        return web.json_response(
                            {"error": f"HTTP {response.status}"},
                            status=response.status
                        )

                    result = await response.json(
                        content_type=None
                    )

            # ------------------------------------------------
            # Safebooru
            # ------------------------------------------------
            elif booru == "safebooru":

                url = "https://safebooru.org/index.php"

                params = {
                    "page": "dapi",
                    "s": "post",
                    "q": "index",
                    "json": "1",
                    "id": post_id,
                }

                async with session.get(
                    url,
                    params=params
                ) as response:

                    if response.status != 200:
                        return web.json_response(
                            {"error": f"HTTP {response.status}"},
                            status=response.status
                        )

                    result = await response.json(
                        content_type=None
                    )

            # ------------------------------------------------
            # Xbooru
            # ------------------------------------------------
            elif booru == "xbooru":

                url = "https://xbooru.com/index.php"

                params = {
                    "page": "dapi",
                    "s": "post",
                    "q": "index",
                    "json": "1",
                    "id": post_id,
                }

                async with session.get(
                    url,
                    params=params
                ) as response:

                    if response.status != 200:
                        return web.json_response(
                            {"error": f"HTTP {response.status}"},
                            status=response.status
                        )

                    result = await response.json(
                        content_type=None
                    )

            # ------------------------------------------------
            # Konachan
            # ------------------------------------------------
            # elif booru == "konachan":

                # url = "https://konachan.com/post.json"

                # params = {
                    # "tags": f"id:{post_id}"
                # }

                # print(f"[ED Konachan] Request URL: {url}")
                # print(f"[ED Konachan] Params: {params}")

                # async with session.get(
                    # url,
                    # params=params
                # ) as response:

                    # print(f"[ED Konachan] HTTP Status: {response.status}")

                    # response_text = await response.text()

                    # print(f"[ED Konachan] Raw Response: {response_text[:3000]}")

                    # if response.status != 200:
                        # return web.json_response(
                            # {
                                # "error": f"HTTP {response.status}",
                                # "response": response_text[:1000]
                            # },
                            # status=502
                        # )

                    # try:
                        # import json
                        # result = json.loads(response_text)

                    # except Exception as e:
                        # print(f"[ED Konachan] JSON Parse Error: {e}")

                        # return web.json_response(
                            # {"error": f"JSON Parse Error: {e}"},
                            # status=502
                        # )

                    # print(f"[ED Konachan] Result Type: {type(result)}")

                    # if isinstance(result, list):
                        # print(f"[ED Konachan] Result Count: {len(result)}")

                        # if result:
                            # print(f"[ED Konachan] First Post: {result[0]}")
                            # print(f"[ED Konachan] Tags: {result[0].get('tags', 'NO TAGS')}")

                    # elif isinstance(result, dict):
                        # print(f"[ED Konachan] Result Keys: {list(result.keys())}")

            # ------------------------------------------------
            # Yande
            # ------------------------------------------------
            elif booru == "yande":

                url = "https://yande.re/post.json"

                params = {
                    "tags": f"id:{post_id}"
                }

                async with session.get(
                    url,
                    params=params
                ) as response:

                    if response.status != 200:
                        return web.json_response(
                            {"error": f"HTTP {response.status}"},
                            status=response.status
                        )

                    result = await response.json()

            else:

                return web.json_response(
                    {"error": f"Unsupported booru: {booru}"},
                    status=400
                )

        return web.json_response(result)

    except Exception as e:

        print(f"[ED Booru API] Error: {e}")

        return web.json_response(
            {"error": str(e)},
            status=500
        )


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
