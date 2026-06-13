#!/usr/bin/env python3
"""Convert industry-chain-methodology.md to styled HTML matching toolbox dark theme."""
import markdown
import re

# Read source
with open('/home/admin/tool-tutorial/industry-chain-methodology.md') as f:
    md_content = f.read()

# Build nav sidebar from headings
headings = re.findall(r'^#{2,4}\s+(.+?)$', md_content, re.MULTILINE)
nav_items = []
for h in headings:
    # Remove anchor tags like <a name="q1"></a>
    clean = re.sub(r'<a.*?</a>', '', h).strip()
    anchor = re.sub(r'[^\w\u4e00-\u9fff]+', '-', clean).strip('-').lower()
    level = 2 if h.startswith('## ') else 3
    indent = '' if level == 2 else '  '
    nav_items.append(f'{indent}<a href="#{anchor}" onclick="navigate(\'{anchor}\')">{clean}</a>')

nav_html = '\n'.join(nav_items)

# Convert markdown to HTML
# Custom extension for better table handling
html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite', 'toc'])

# Fix anchor tags: <a name="q1"></a> → id on the heading
html_body = re.sub(r'<a name="(.*?)"></a>\s*<h([23])>', r'<h\2 id="\1">', html_body)
# Add ids to remaining headings without anchors
def add_id(m):
    text = m.group(2)
    anchor = re.sub(r'[^\w\u4e00-\u9fff]+', '-', text).strip('-').lower()
    return f'<{m.group(1)} id="{anchor}">{text}'

html_body = re.sub(r'<(h[234])>(.+?)</h\1>', add_id, html_body)

# Wrap each h2 section in a chapter div
html_body = re.sub(
    r'(<h2 id="[^"]+">.+?</h2>)',
    r'</div><div class="chapter">\n\1',
    html_body
)
html_body = '<div class="chapter active">' + html_body + '</div>'
# Remove leading empty chapter
html_body = html_body.replace('<div class="chapter"></div><div class="chapter active">', '<div class="chapter active">')

# Build full HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>产业链拆解体系 v1.0 — 曼尼投研工具箱</title>
<style>
:root {{ --bg:#0d1117; --bg2:#161b22; --bg3:#21262d; --border:#30363d; --text:#c9d1d9; --text2:#8b949e; --accent:#58a6ff; --warn:#d29922; --green:#3fb950; --red:#f85149; --purple:#8b5cf6; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB',sans-serif; background:var(--bg); color:var(--text); display:flex; min-height:100vh; }}
#sidebar {{ width:280px; min-width:280px; background:var(--bg2); border-right:1px solid var(--border); padding:24px 16px; position:sticky; top:0; height:100vh; overflow-y:auto; }}
#sidebar h1 {{ font-size:14px; color:var(--accent); margin-bottom:4px; line-height:1.4; }}
#sidebar .meta {{ font-size:11px; color:var(--text2); margin-bottom:16px; }}
#sidebar nav a {{ display:block; padding:5px 10px; border-radius:4px; font-size:12px; color:var(--text2); text-decoration:none; margin-bottom:1px; transition:all .15s; }}
#sidebar nav a:hover,#sidebar nav a.active {{ background:var(--bg3); color:var(--text); }}
#sidebar nav a.active {{ color:var(--accent); }}
#sidebar .back {{ display:block; margin-top:16px; padding:6px 10px; font-size:11px; color:var(--text2); text-decoration:none; border-top:1px solid var(--border); }}
#main {{ flex:1; padding:40px 48px; max-width:1000px; }}
#main h2 {{ font-size:22px; color:var(--accent); border-bottom:1px solid var(--border); padding-bottom:12px; margin:40px 0 20px; }}
#main h2:first-of-type {{ margin-top:0; }}
#main h3 {{ font-size:17px; color:var(--text); margin:24px 0 10px; }}
#main h4 {{ font-size:14px; color:var(--text2); margin:16px 0 8px; }}
#main p {{ font-size:14px; line-height:1.8; margin-bottom:10px; }}
#main ul,#main ol {{ margin:6px 0 14px 24px; font-size:14px; line-height:1.8; }}
#main li {{ margin-bottom:3px; }}
#main code {{ background:var(--bg3); padding:2px 6px; border-radius:3px; font-size:13px; color:var(--warn); }}
#main pre {{ background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:16px 20px; overflow-x:auto; margin:14px 0; font-size:12px; line-height:1.5; }}
#main pre code {{ background:none; padding:0; color:var(--text); }}
#main table {{ width:100%; border-collapse:collapse; margin:14px 0; font-size:13px; }}
#main th,td {{ border:1px solid var(--border); padding:7px 10px; text-align:left; vertical-align:top; }}
#main th {{ background:var(--bg3); font-weight:600; color:var(--text); }}
#main td {{ color:var(--text2); }}
#main blockquote {{ border-left:3px solid var(--accent); margin:14px 0; padding:6px 16px; background:rgba(88,166,255,0.05); border-radius:0 6px 6px 0; font-size:14px; }}
#main strong {{ color:#e6edf3; }}
#main hr {{ border:none; border-top:1px solid var(--border); margin:30px 0; }}
#main a {{ color:var(--accent); }}
.chapter {{ display:none; }}
.chapter.active {{ display:block; }}
@media(max-width:768px){{ body{{flex-direction:column}} #sidebar{{width:100%;min-width:0;height:auto;position:relative;padding:16px}} #main{{padding:20px}} }}
</style>
</head>
<body>
<div id="sidebar">
<h1>🔗 产业链拆解<br>体系 v1.0</h1>
<div class="meta">AI算力赛道 · 方法论文档 · 2026-06-13</div>
<nav id="nav">
{nav_html}
</nav>
<a href="index.html" class="back">← 返回工具箱</a>
</div>
<div id="main">
{html_body}
</div>
<script>
// Navigation
function navigate(id) {{
    document.querySelectorAll('.chapter').forEach(c => c.classList.remove('active'));
    var el = document.querySelector('#' + CSS.escape(id));
    if (el) {{
        var chapter = el.closest('.chapter');
        if (chapter) chapter.classList.add('active');
        el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}
    document.querySelectorAll('#nav a').forEach(a => a.classList.remove('active'));
    event.target.classList.add('active');
}}
// Activate first chapter
document.querySelector('.chapter').classList.add('active');
if (document.querySelector('#nav a')) document.querySelector('#nav a').classList.add('active');
</script>
</body>
</html>'''

with open('/home/admin/tool-tutorial/industry-chain-methodology.html', 'w') as f:
    f.write(html)

print(f"Written: {len(html)} chars")
print(f"Headings: {len(headings)}")
