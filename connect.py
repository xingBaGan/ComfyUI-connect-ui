


from PIL import Image
import numpy as np
import comfy.utils
import time
import json
import base64
from io import BytesIO
from aiohttp import WSMsgType
from server import PromptServer
import asyncio
from aiohttp import web
import torch
import logging
import uuid
import aiohttp
import PIL
import os
#You can use this node to save full size images through the websocket, the
#images will be sent in exactly the same format as the image previews: as
#binary images on the websocket with a 8 byte header indicating the type
#of binary message (first 4 bytes) and the image format (next 4 bytes).

#Note that no metadata will be put in the images saved with this node.
socket = None
placeholder_image_path = None
class reciveImageByWebsocket:
    def __init__(self):
        self.locks = {}
        self.received_images = {}
        self._task_counter = 0  # 添加计数器用于生成唯一ID
        
    @classmethod
    def INPUT_TYPES(s):
        return {}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "receive_image"
    OUTPUT_NODE = True
    CATEGORY = "api/image"
    
    def IS_CHANGED():
        return time.time()
    
    def receive_image(self):
        global placeholder_image_path
        if placeholder_image_path:
            # 将PIL Image转换为ComfyUI期望的格式
            pil_image = Image.open(placeholder_image_path)
            # 转换为numpy数组
            image_np = np.array(pil_image).astype(np.float32) / 255.0
            # 转换为正确的张量格式
            tensor_image = torch.from_numpy(image_np)[None,]
            return (tensor_image,)  # 返回元组
        return (None,)

class SaveImageByWebsocket:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"images": ("IMAGE", ),}
                }

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "api/image"

    def save_images(self, images):
        # PromptServer.instance.send_sync("send_websocket_image", json.dumps({"type": "image", "data": '123' }))
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            PromptServer.instance.send_sync("send_websocket_image", json.dumps({"type": "image", "data": base64.b64encode(img.tobytes()).decode('utf-8')}))
        return {}

    @classmethod
    def IS_CHANGED(s, images):
        return time.time()


# 添加新的API路由处理器
# @PromptServer.instance.routes.post("/api/send-image-by-post")
# async def send_image_to_client(request):
#     global message_data
#     try:
#         data = await request.post()
#         image_field = data.get("image")
#         client_id = data.get("client_id")

#         if not image_field or not client_id:
#             return web.Response(status=400, text="缺少必要参数")

#         image_bytes = image_field.file.read()
        
#         # 构建websocket消息
#         message = {
#             "type": "image",
#             "data": base64.b64encode(image_bytes).decode('utf-8'),
#             "client_id": f"task_{client_id}"  # 确保ID格式匹配
#         }
#         json_message = json.dumps(message)
#         message_data = json_message
#         PromptServer.instance.send_sync("recive_websocket_image", json_message)
#         return web.Response(status=200, text="图片已发送")
        
#     except Exception as e:
#         print(f"错误: {str(e)}")
#         return web.Response(status=500, text=str(e))

# 创建一个websocket服务器
@PromptServer.instance.routes.get('/ws_live')
async def websocket_handler(request):
    global placeholder_image_path
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    sid = request.rel_url.query.get('clientId', '')
    if sid:
        # Reusing existing session, remove old
        # socket = ws
        pass
    else:
        sid = uuid.uuid4().hex

    socket = ws
    print(f"sid: {sid}")

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data["type"] == "input_image_change":
                image_data = None
                ext = "png"
                if "," in data["data"]["image"]:
                    image_info = data["data"]["image"].split(",")
                    image_data = image_info[1]
                    image_type = image_info[0]
                    ext = image_type.split("/")[1].replace(";base64", "")
                try:
                    image_bytes = base64.b64decode(image_data)
                    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
                    image_dir = os.path.join(current_dir, "images")  # 在当前目录下创建 images 目录
                    os.makedirs(image_dir, exist_ok=True)  # 确保目录存在
                    image_path = os.path.join(image_dir, f"placeholder.{ext}")  # 图片路径
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    placeholder_image_path = image_path
                except PIL.UnidentifiedImageError:
                    print("无法识别图像文件")
                message = {
                    "type": "image",
                    "data": data["data"]["image"],
                    "client_id": f"task_{sid}"  # 确保ID格式匹配
                }
                json_message = json.dumps(message)
                PromptServer.instance.send_sync("recive_websocket_image", json_message)
                return web.Response(status=200, text="图片已发送")
        if msg.type == aiohttp.WSMsgType.ERROR:
            logging.warning('ws connection closed with exception %s' % ws.exception())
    return ws

NODE_CLASS_MAPPINGS = {
    "SaveImageByWebsocket": SaveImageByWebsocket,
    "reciveImageByWebsocket": reciveImageByWebsocket,
}
