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
    if (window.cache_object.reciveImageByWebsocket_img) {
      window.cache_object.reciveImageByWebsocket_img.remove();
    }
    const img = new Image();
    img.src = image;
    window.cache_object.reciveImageByWebsocket_img = img;
    
    // 创建一个包装容器
    const wrapper = document.createElement('div');
    wrapper.style.position = 'absolute';
    wrapper.style.bottom = '100px';
    wrapper.style.right = '60px';
    wrapper.style.zIndex = '1000';
    
    // 设置图片样式
    img.onload = function () {
      img.style.width = '250px';
      img.style.height = 'auto';
      img.style.objectFit = "contain";
      img.classList.add("reciveImageByWebsocket");
    }
    
    // 创建切换按钮
    const toggleButton = document.createElement('button');
    toggleButton.innerHTML = '−';  // 使用减号表示最小化
    toggleButton.style.position = 'fixed';
    toggleButton.style.bottom = '100px';
    toggleButton.style.right = '80px';
    toggleButton.style.background = 'rgba(0,0,0,0.5)';
    toggleButton.style.border = 'none';
    toggleButton.style.color = 'white';
    toggleButton.style.borderRadius = '50%';
    toggleButton.style.width = '20px';
    toggleButton.style.height = '20px';
    toggleButton.style.cursor = 'pointer';
    
    
    // 添加切换功能
    let isExpanded = true;
    toggleButton.onclick = () => {
      isExpanded = !isExpanded;
      if (isExpanded) {
        img.style.display = 'block';
        toggleButton.innerHTML = '−';  // 展开状态显示减号
        wrapper.style.width = 'auto';
        wrapper.style.height = 'auto';
      } else {
        img.style.display = 'none';
        toggleButton.innerHTML = '+';  // 折叠状态显示加号
        wrapper.style.width = '30px';
        wrapper.style.height = '30px';
      }
    };
    
    // 组装DOM结构
    wrapper.appendChild(img);
    wrapper.appendChild(toggleButton);
    document.body.appendChild(wrapper);
    window.cache_object.reciveImageByWebsocket_img = wrapper;
  }
});


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

