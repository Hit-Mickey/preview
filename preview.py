import os, http.server, socketserver, urllib.parse, datetime, base64

# --- 新增：从环境变量读取用户名和密码并生成认证密钥 ---
AUTH_USER = os.environ.get('AUTH_USER')
AUTH_PASS = os.environ.get('AUTH_PASS')
AUTH_KEY = None
if AUTH_USER and AUTH_PASS:
    AUTH_KEY = "Basic " + base64.b64encode(f"{AUTH_USER}:{AUTH_PASS}".encode('utf-8')).decode('utf-8')

# 1. 载入配置
MAPPINGS = []
MAPPING_DICT = {}
if os.path.exists('paths.conf'):
    with open('paths.conf', 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    alias, path = line.split(':', 1)
                    alias = alias.strip()
                    clean_path = path.strip().lstrip('/').rstrip('/')
                    phys_path = os.path.join('/host', clean_path)
                    MAPPINGS.append({'alias': alias, 'path': phys_path})
                    MAPPING_DICT[alias] = phys_path
                except: continue

# 2. UI 模板：全自适应 + 智能面包屑着色 + 16px 列表
HTML_TPL = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{ 
            --bg: #ffffff; --text: #2c3e50; --sub: #7f8c8d; 
            --hover: #f8f9fa; --border: #edf2f7; --accent: #00b4d8; 
        }}
        @media (prefers-color-scheme: dark) {{ 
            :root {{ --bg: #1a202c; --text: #e2e8f0; --sub: #a0aec0; --hover: #2d3748; --border: #2d3748; --accent: #38bdf8; }} 
        }}
        
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; min-height: 100vh; }}
        .container {{ width: 100%; max-width: 1000px; margin: 0 auto; padding: 40px 24px; box-sizing: border-box; }}
        
        .header {{ margin-bottom: 25px; text-align: center; }}
        .header h1 {{ font-size: clamp(26px, 6vw, 34px); font-weight: 700; margin: 0; color: var(--text); letter-spacing: -0.5px; }}
        
        .nav-bar {{ font-size: 17px; text-align: left; padding-left: 16px; margin-bottom: 15px; overflow-x: auto; white-space: nowrap; font-weight: 400; }}
        .nav-bar a {{ color: var(--sub); text-decoration: none; transition: color 0.2s; }}
        .nav-bar a:hover {{ color: var(--accent); text-decoration: underline; }}
        .nav-bar .curr {{ color: var(--accent); font-weight: 600; }}
        .sep {{ margin: 0 8px; color: var(--border); }}
        
        .list-header {{ display: flex; align-items: center; padding: 12px 16px; font-size: 16px; color: var(--sub); font-weight: 600; background: var(--hover); border-radius: 10px 10px 0 0; border-bottom: 1px solid var(--border); }}
        .col-name {{ flex: 1; display: flex; align-items: center; }}
        .col-size {{ width: 120px; text-align: right; }}
        .col-time {{ width: 180px; text-align: right; }}
        
        .sort-btn {{ color: inherit; text-decoration: none; display: flex; align-items: center; justify-content: flex-end; gap: 8px; cursor: pointer; border: none; background: none; font: inherit; padding: 0; width: 100%; }}
        .sort-btn.left {{ justify-content: flex-start; }}
        .sort-btn:hover {{ color: var(--accent); }}
        .active-sort {{ color: var(--accent) !important; }}
        .arrow {{ font-size: 22px; font-weight: 900; line-height: 1; display: inline-block; width: 18px; }}

        .item {{ display: flex; align-items: center; padding: 14px 16px; text-decoration: none; color: inherit; transition: background 0.2s; border-bottom: 1px solid var(--border); }}
        .item:hover {{ background: var(--hover); }}
        .icon {{ margin-right: 18px; min-width: 24px; display: flex; align-items: center; fill: var(--sub); }}
        .name-text {{ flex: 1; font-size: 16px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .meta {{ font-size: 14px; color: var(--sub); font-variant-numeric: tabular-nums; }}

        @media (max-width: 650px) {{
            .col-size {{ display: none; }} 
            .col-time {{ width: 120px; }}
            .nav-bar {{ font-size: 16px; padding-left: 12px; }}
            .list-header, .name-text {{ font-size: 14px; }}
            .arrow {{ font-size: 18px; }}
            .container {{ padding: 20px 15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>{title}</h1></div>
        <div class="nav-bar">{nav}</div>
        <div class="list-header">
            <div class="col-name"><button onclick="applySort('name')" class="sort-btn left" id="btn-name">文件名<span class="arrow" id="arrow-name"></span></button></div>
            <div class="col-size"><button onclick="applySort('size')" class="sort-btn" id="btn-size">大小<span class="arrow" id="arrow-size"></span></button></div>
            <div class="col-time"><button onclick="applySort('time')" class="sort-btn" id="btn-time">修改时间<span class="arrow" id="arrow-time"></span></button></div>
        </div>
        <div id="file-list">{content}</div>
    </div>

    <script>
        // 1. 默认值严格设为 name/asc
        let currentSort = document.cookie.replace(/(?:(?:^|.*;\s*)sort\s*\=\s*([^;]*).*$)|^.*$/, "$1") || "name";
        let currentOrder = document.cookie.replace(/(?:(?:^|.*;\s*)order\s*\=\s*([^;]*).*$)|^.*$/, "$1") || "asc";

        function applySort(type, isFirstLoad = false) {{
            if (!isFirstLoad) {{
                if (currentSort === type) {{
                    currentOrder = currentOrder === "asc" ? "desc" : "asc";
                }} else {{
                    currentSort = type;
                    currentOrder = "asc";
                }}
            }}
            const list = document.getElementById('file-list');
            const items = Array.from(list.getElementsByClassName('item'));
            
            items.sort((a, b) => {{
                const isDirA = a.dataset.isdir === "true";
                const isDirB = b.dataset.isdir === "true";
                if (isDirA !== isDirB) return isDirA ? -1 : 1;
                
                let valA = a.dataset[currentSort];
                let valB = b.dataset[currentSort];
                
                if (currentSort === 'size' || currentSort === 'time') {{
                    valA = parseFloat(valA); valB = parseFloat(valB);
                }} else {{
                    valA = valA.toLowerCase(); valB = valB.toLowerCase();
                }}

                if (valA < valB) return currentOrder === "asc" ? -1 : 1;
                if (valA > valB) return currentOrder === "asc" ? 1 : -1;
                return 0;
            }});

            items.forEach(item => list.appendChild(item));
            
            // 更新 UI 激活状态
            document.querySelectorAll('.sort-btn').forEach(btn => btn.classList.remove('active-sort'));
            document.querySelectorAll('.arrow').forEach(arr => arr.innerText = '');
            
            const activeBtn = document.getElementById('btn-' + currentSort);
            if(activeBtn) activeBtn.classList.add('active-sort');
            const activeArrow = document.getElementById('arrow-' + currentSort);
            if(activeArrow) activeArrow.innerText = currentOrder === 'asc' ? ' ↑' : ' ↓';

            document.cookie = "sort=" + currentSort + ";path=/;max-age=31536000";
            document.cookie = "order=" + currentOrder + ";path=/;max-age=31536000";
        }}
        
        window.onload = () => applySort(currentSort, true);
    </script>
</body>
</html>
"""

SVG_FOLDER = '<svg viewBox="0 0 24 24" width="22"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>'
SVG_FILE = '<svg viewBox="0 0 24 24" width="22"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>'

class DefaultSortHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # --- 新增：如果配置了账号密码，校验 Authorization 头 ---
        if AUTH_KEY and self.headers.get('Authorization') != AUTH_KEY:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Login Required"')
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"401 Unauthorized")
            return
        # -----------------------------------------------------

        u = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(u.path).strip('/')
        parts = path.split('/', 1)
        alias = parts[0]
        rel = parts[1] if len(parts) > 1 else ""

        if not alias:
            self._render_root()
        elif alias in MAPPING_DICT:
            base = MAPPING_DICT[alias]
            target = os.path.normpath(os.path.join(base, rel))
            if not target.startswith(os.path.normpath(base)) or not os.path.exists(target):
                self.send_error(404)
                return
            if os.path.isdir(target):
                self._render_dir(alias, rel, target)
            else:
                self._serve_file(target)
        else:
            self.send_error(404)

    def _render_root(self):
        items = []
        for m in MAPPINGS:
            is_d = os.path.isdir(m['path'])
            s = os.stat(m['path'])
            items.append({'name': m['alias'], 'url': f"/{m['alias']}/", 'is_dir': is_d, 'mtime': s.st_mtime, 'size': s.st_size})
        nav = '<span class="curr">首页</span>'
        self._send_list(nav, items)

    def _render_dir(self, alias, rel, phys):
        items = []
        try:
            for e in os.listdir(phys):
                full = os.path.join(phys, e)
                is_d = os.path.isdir(full)
                s = os.stat(full)
                items.append({'name': e, 'url': f"/{alias}/{os.path.join(rel, e)}".replace('\\', '/') + ("/" if is_d else ""), 
                              'is_dir': is_d, 'mtime': s.st_mtime, 'size': s.st_size})
        except: pass
        
        nav_parts = [f'<a href="/">首页</a>']
        acc = f"/{alias}"
        if not rel:
            nav_parts.append(f'<span class="sep">/</span><span class="curr">{alias}</span>')
        else:
            nav_parts.append(f'<span class="sep">/</span><a href="{acc}/">{alias}</a>')
            segs = rel.strip('/').split('/')
            for i, s in enumerate(segs):
                acc += f"/{s}"
                if i == len(segs) - 1:
                    nav_parts.append(f'<span class="sep">/</span><span class="curr">{s}</span>')
                else:
                    nav_parts.append(f'<span class="sep">/</span><a href="{acc}/">{s}</a>')
        
        self._send_list("".join(nav_parts), items)

    def _send_list(self, nav, items):
        # 3. 后端执行默认排序：文件名升序 -> 文件夹置顶
        items.sort(key=lambda x: x['name'].lower())
        items.sort(key=lambda x: not x['is_dir'])
        
        rows = "".join([f'<a href="{i["url"]}" class="item" data-name="{i["name"]}" data-isdir="{"true" if i["is_dir"] else "false"}" data-size="{i["size"] if not i["is_dir"] else 0}" data-time="{i["mtime"]}">\
            <div class="icon">{SVG_FOLDER if i["is_dir"] else SVG_FILE}</div><div class="name-text">{i["name"]}</div><div class="meta col-size">{self._f_size(i["size"]) if not i["is_dir"] else "-"}</div><div class="meta col-time">{datetime.datetime.fromtimestamp(i["mtime"]).strftime("%Y-%m-%d %H:%M")}</div></a>' for i in items])
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_TPL.format(title="Mickey's Preview", nav=nav, content=rows, 
            active_name="", icon_name="", active_size="", icon_size="", active_time="", icon_time="").encode())

    def _f_size(self, b):
        for u in ['B','K','M','G']:
            if b < 1024: return f"{b:.1f}{u}"
            b /= 1024
        return f"{b:.1f}T"

    def _serve_file(self, path):
        m = {'.html': 'text/html', '.htm': 'text/html', '.pdf': 'application/pdf', '.txt': 'text/plain', '.png': 'image/png', '.jpg': 'image/jpeg'}
        try:
            with open(path, 'rb') as f:
                self.send_response(200)
                self.send_header("Content-type", m.get(os.path.splitext(path)[1].lower(), "application/octet-stream"))
                self.send_header("Content-Length", str(os.path.getsize(path)))
                self.end_headers()
                self.wfile.write(f.read())
        except: self.send_error(404)

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", 6033), DefaultSortHandler) as httpd:
    httpd.serve_forever()