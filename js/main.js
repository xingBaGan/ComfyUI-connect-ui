import { app } from "../../scripts/app.js";
import { api } from "../../../scripts/api.js";

window.cache_object = {
  input_image: null,
  node_reciveImageByWebsocket: null,
  reciveImageByWebsocket_img: null,
};
api.addEventListener("recive_websocket_image", (e) => {
  const data = JSON.parse(e.detail);
  const image = data.data;
  const type = data.type;
  if (window.cache_object.node_reciveImageByWebsocket) {
    window.cache_object.input_image = image;
    console.log("---image---", image);
    if (window.cache_object.reciveImageByWebsocket_img) {
      window.cache_object.reciveImageByWebsocket_img.remove();
    }
    // 创建图片
    const img = new Image();
    img.src = image;
    window.cache_object.reciveImageByWebsocket_img = img;
    img.onload = function () {
      img.style.width = '250px';
      img.style.height = 'auto';
      img.style.objectFit = "contain";
      img.style.position = "absolute";
      img.style.top = "100px";
      img.style.left = "50px";
      img.style.zIndex = "1000";
      img.classList.add("reciveImageByWebsocket");
    }
    document.body.appendChild(img);
  }
  // 实时绘画图片
});
// 注册自定义消息处理器
app.registerExtension({
  name: "ComfyUI.connect-ui",
  async init() {
    console.log('ComfyUI.connect-ui');
  },
  async nodeCreated(node) {
    if (node.title === "reciveImageByWebsocket") {
      window.cache_object.node_reciveImageByWebsocket = node;
    }
  }
});

