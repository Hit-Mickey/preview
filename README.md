# Mickey's Preview 🚀

## 中文说明|[英文说明](./README_EN.md)

**Mickey's Preview** 是一个基于 Python 和 Docker 的极简、高性能本地文件预览系统。它专为开发者和研究人员设计，通过最轻量化的方式，将服务器上的零散目录或单个文件聚合到一个具有 **Alist/OpenList** 风格的现代网页界面中。

### ✨ 核心特性

* **🎨 极简风格 UI**：极致简约的现代界面，支持**全设备自适应**（完美适配手机/平板/电脑）。
* **⚡ 德芙般丝滑的排序**：支持按文件名、文件大小、修改时间进行**前端实时排序**。零延迟响应，无需重新加载页面。
* **🧠 排序记忆功能**：利用 Cookie 自动记住你的排序偏好。进入子目录或刷新页面，依然保持你喜欢的顺序。
* **🔗 纯净 URL 体验**：无论如何排序或跳转，地址栏永远保持简洁，没有任何 `?sort=...` 等杂乱参数。
* **📍 局部着色面包屑**：导航栏仅高亮当前所在目录，父级目录清晰明了，方便快速返回。
* **🛠️ 路径穿透映射**：通过 `paths.conf` 灵活映射宿主机任何位置的文件夹或单文件。
* **🐳 极致轻量化**：基于 Python Alpine 镜像构建，整体体积仅约 **50MB**。

### 📦 快速部署 (Docker Compose)

1.  **准备配置文件**：
    在本地创建 `paths.conf`，每一行代表一个映射，格式为 `显示名称:绝对路径`：
    ```bash
    mkdir preview && cd preview
    touch paths.conf
    ```
    `paths.conf`示例：
    ```text
    我的论文:/home/user/nas/papers
    节点教程:/home/user/docs/tutorial.html
    ```

2.  **编写 `docker-compose.yml`**：

    `vim docker-compose.yml`
    ```yaml
    services:
      preview:
        image: mickey666/preview:latest
        container_name: preview
        # 如果要设置密码请取消注释
        # environment:
          # - AUTH_USER=user
          # - AUTH_PASS=1
        volumes:
          - ./paths.conf:/app/paths.conf:ro    # 映射配置文件
          - /:/host:ro                        # 只读映射宿主机根目录
        ports:
          - "6033:6033"
        restart: unless-stopped
    ```

3.  **启动服务**：
    ```bash
    docker compose up -d
    ```

4.  **更改文件后重启服务**：
    ```bash
    docker compose dwon && docker compose up -d
    ```


### ⚠️ Security Note / 安全提示

本系统默认具有宿主机根目录的只读访问权限（`/:/host:ro`）。请确保该服务仅在受信内网使用，或在生产环境配置相应的防火墙/反向代理策略。

**Author:** Hit-Mickey

**License:** MIT