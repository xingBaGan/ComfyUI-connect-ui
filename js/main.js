import { app } from "../../scripts/app.js";
import { api } from "../../../scripts/api.js";

// 注册自定义消息处理器
app.registerExtension({
  name: "ComfyUI.Demo.WebsocketImage",
  async init() {
    // api.addEventListener("recive_websocket_image", (e) => {
    //   const data = JSON.parse(e.detail);
    //   const image = data.data;
    //   const type = data.type;
    //   console.log(image, type);
    // });

    // api.addEventListener("send_image_preview", (e) => {
    //   const data = JSON.parse(e.detail);
    //   const image = data.data;
    //   const type = data.type;
    //   console.log('send_image_preview', image, type);
    // });
    console.log('ComfyUI.Demo.WebsocketImage');
  }
});