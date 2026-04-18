# Mickey's Preview 🚀

**Mickey's Preview** is a minimalist, high-performance local file preview system based on Python and Docker. Designed specifically for developers and researchers, it offers a lightweight way to aggregate scattered directories or single files from your server into a modern web interface with an **Alist/OpenList** aesthetic.

---

### ✨ Core Features

* **🎨 Minimalist UI**: A clean, modern interface with **Full Responsive Design** (perfectly adapted for mobile, tablet, and desktop).
* **⚡ Silky Smooth Sorting**: Supports **real-time frontend sorting** by filename, file size, and modification time. Zero latency with no page reloads required.
* **🧠 Sorting Memory**: Automatically remembers your sorting preferences via Cookies. Your preferred order is maintained even when entering subdirectories or refreshing the page.
* **🔗 Clean URL Experience**: The address bar remains tidy regardless of sorting or navigation—no cluttered parameters like `?sort=...`.
* **📍 Context-Aware Breadcrumbs**: Only the current directory is highlighted, providing a clear hierarchy for quick navigation.
* **🛠️ Path Mapping**: Flexibly map any host directory or single file to the preview system via `paths.conf`.
* **🐳 Ultra Lightweight**: Built on the Python Alpine image, with a total image size of approximately **50MB**.

---

### 📦 Quick Deployment (Docker Compose)

1.  **Prepare Configuration**:
    Create a folder for the project and a `paths.conf` file. Each line represents a mapping in the format `Display_Name:Absolute_Path`:
    ```bash
    mkdir preview && cd preview
    touch paths.conf
    ```
    `paths.conf` example:
    ```text
    My_Papers:/home/user/nas/papers
    Node_Tutorial:/home/user/docs/tutorial.html
    ```

2.  **Write `docker-compose.yml`**:
    
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

3.  **Start the Service**:
    ```bash
    docker compose up -d
    ```

4.  **Restart Service after changes**:
    ```bash
    docker compose dwon && docker compose up -d
    ```

---

### ⚠️ Security Note

By default, this system has read-only access to the host's root directory (`/:/host:ro`). Please ensure this service is used only within a **trusted internal network**, or configure appropriate firewall/reverse proxy policies for production environments.

---

**Author:** Hit-Mickey

**License:** MIT