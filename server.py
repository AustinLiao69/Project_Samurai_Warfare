import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse

DOCS_DIR = "00.Project documents"
PORT = 5000

STYLE = """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Noto Serif TC', 'Georgia', serif; background: #1a1209; color: #e8d5a3; min-height: 100vh; }
  .layout { display: flex; min-height: 100vh; }
  .sidebar { width: 280px; background: #120d06; border-right: 1px solid #3d2e1a; padding: 20px 0; position: fixed; top: 0; left: 0; height: 100vh; overflow-y: auto; }
  .sidebar h1 { font-size: 14px; color: #b8860b; padding: 0 20px 16px; border-bottom: 1px solid #3d2e1a; letter-spacing: 2px; text-transform: uppercase; }
  .sidebar ul { list-style: none; padding: 12px 0; }
  .sidebar li a { display: block; padding: 8px 20px; font-size: 13px; color: #c8a96e; text-decoration: none; border-left: 3px solid transparent; transition: all 0.2s; }
  .sidebar li a:hover, .sidebar li a.active { color: #f0c060; background: #1e1508; border-left-color: #b8860b; }
  .sidebar .section-label { padding: 12px 20px 4px; font-size: 11px; color: #7a6040; text-transform: uppercase; letter-spacing: 1px; }
  .main { margin-left: 280px; padding: 40px; max-width: 900px; }
  .main h1 { font-size: 28px; color: #f0c060; margin-bottom: 8px; border-bottom: 2px solid #b8860b; padding-bottom: 12px; }
  .main h2 { font-size: 20px; color: #d4a84b; margin: 28px 0 12px; }
  .main h3 { font-size: 16px; color: #c8943a; margin: 20px 0 8px; }
  .main p { line-height: 1.8; margin-bottom: 12px; color: #d8c090; }
  .main ul, .main ol { padding-left: 24px; margin-bottom: 12px; }
  .main li { line-height: 1.8; color: #d0b880; margin-bottom: 4px; }
  .main table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
  .main th { background: #2a1f0e; color: #f0c060; padding: 10px 14px; text-align: left; border: 1px solid #4a3820; }
  .main td { padding: 8px 14px; border: 1px solid #3a2a14; color: #c8b080; }
  .main tr:nth-child(even) td { background: #1a1209; }
  .main code { background: #1e1508; border: 1px solid #3d2e1a; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 13px; color: #80c080; }
  .main pre { background: #0e0b06; border: 1px solid #3d2e1a; padding: 16px; border-radius: 6px; overflow-x: auto; margin: 12px 0; }
  .main pre code { background: none; border: none; color: #90d090; padding: 0; }
  .main blockquote { border-left: 4px solid #b8860b; padding: 8px 16px; background: #1e1508; margin: 16px 0; color: #c8a860; font-style: italic; }
  .main hr { border: none; border-top: 1px solid #3d2e1a; margin: 24px 0; }
  .hero { text-align: center; padding: 60px 20px; }
  .hero h1 { font-size: 36px; color: #f0c060; margin-bottom: 16px; border: none; }
  .hero p { font-size: 18px; color: #c8a870; max-width: 500px; margin: 0 auto 32px; }
  .doc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 32px; }
  .doc-card { background: #1a1209; border: 1px solid #3d2e1a; border-radius: 8px; padding: 20px; cursor: pointer; transition: all 0.2s; text-decoration: none; display: block; }
  .doc-card:hover { border-color: #b8860b; background: #1e1508; }
  .doc-card .title { color: #f0c060; font-size: 14px; font-weight: bold; margin-bottom: 6px; }
  .doc-card .desc { color: #9a8060; font-size: 12px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-left: 8px; }
  .badge-pm { background: #4a2a00; color: #f0a030; }
  .badge-design { background: #002a4a; color: #30a0f0; }
</style>
"""

def get_doc_list():
    docs = []
    if os.path.exists(DOCS_DIR):
        for f in sorted(os.listdir(DOCS_DIR)):
            if f.endswith('.md') or f.endswith('.csv'):
                docs.append(f)
    return docs

def render_md_to_html(content):
    lines = content.split('\n')
    html = []
    in_code = False
    in_table = False
    in_list = False

    for line in lines:
        if line.startswith('```'):
            if in_code:
                html.append('</code></pre>')
                in_code = False
            else:
                lang = line[3:].strip()
                html.append(f'<pre><code class="lang-{lang}">')
                in_code = True
            continue

        if in_code:
            html.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            continue

        if line.startswith('| ') or line.startswith('|--'):
            if not in_table:
                html.append('<table>')
                in_table = True
            if line.startswith('|--') or line.startswith('| --') or line.startswith('|:'):
                continue
            cells = [c.strip() for c in line.strip('|').split('|')]
            is_header = html and '<table>' in html[-2] if len(html) >= 2 else False
            tag = 'th' if (len(html) >= 2 and html[-2] == '<table>') else 'td'
            html.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
            continue
        else:
            if in_table:
                html.append('</table>')
                in_table = False

        if line.startswith('# '):
            html.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            html.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            html.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            html.append(f'<h4>{line[5:]}</h4>')
        elif line.startswith('> '):
            html.append(f'<blockquote>{line[2:]}</blockquote>')
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html.append('<ul>')
                in_list = True
            item = line[2:]
            item = item.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            item = item.replace('`', '<code>', 1).replace('`', '</code>', 1)
            html.append(f'<li>{item}</li>')
            continue
        elif line.startswith('---'):
            html.append('<hr>')
        elif line.strip() == '':
            if in_list:
                html.append('</ul>')
                in_list = False
            html.append('')
        else:
            if in_list:
                html.append('</ul>')
                in_list = False
            processed = line
            while '**' in processed:
                processed = processed.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            while '`' in processed:
                processed = processed.replace('`', '<code>', 1).replace('`', '</code>', 1)
            html.append(f'<p>{processed}</p>')

    if in_list:
        html.append('</ul>')
    if in_table:
        html.append('</table>')

    return '\n'.join(html)

def build_sidebar(active=None):
    docs = get_doc_list()
    pm_docs = [d for d in docs if d.startswith('PM')]
    design_docs = [d for d in docs if not d.startswith('PM')]

    html = '<div class="sidebar"><h1>⚔ 戰國三代記</h1><ul>'
    html += '<li><a href="/" ' + ('class="active"' if active is None else '') + '>📋 首頁總覽</a></li>'

    html += '</ul><div class="section-label">📌 PM 文件</div><ul>'
    for d in pm_docs:
        label = d.replace('.md', '').replace('.csv', '')
        active_class = 'class="active"' if d == active else ''
        html += f'<li><a href="/doc/{d}" {active_class}>{label}</a></li>'

    html += '</ul><div class="section-label">🎮 設計文件</div><ul>'
    for d in design_docs:
        label = d.replace('.md', '').replace('.csv', '')
        active_class = 'class="active"' if d == active else ''
        html += f'<li><a href="/doc/{d}" {active_class}>{label}</a></li>'

    html += '</ul></div>'
    return html

def build_index():
    docs = get_doc_list()
    pm_docs = [d for d in docs if d.startswith('PM')]
    design_docs = [d for d in docs if not d.startswith('PM')]

    cards_pm = ''.join(
        f'<a class="doc-card" href="/doc/{d}"><div class="title">{d.replace(".md","")}</div><div class="desc">PM 管理文件</div></a>'
        for d in pm_docs
    )
    cards_design = ''.join(
        f'<a class="doc-card" href="/doc/{d}"><div class="title">{d.replace(".md","").replace(".csv","")}</div><div class="desc">遊戲設計文件</div></a>'
        for d in design_docs
    )

    return f"""<!DOCTYPE html>
<html lang="zh-TW"><head><meta charset="UTF-8"><title>戰國三代記 - 文件總覽</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC&display=swap" rel="stylesheet">
{STYLE}</head><body>
<div class="layout">
{build_sidebar()}
<div class="main">
  <div class="hero">
    <h1>《戰國三代記》</h1>
    <p>Sengoku Sandai-ki — 專案文件庫</p>
  </div>
  <h2>📌 PM 管理文件</h2>
  <div class="doc-grid">{cards_pm}</div>
  <h2 style="margin-top:32px">🎮 遊戲設計文件</h2>
  <div class="doc-grid">{cards_design}</div>
</div>
</div>
</body></html>"""

def build_doc_page(filename):
    path = os.path.join(DOCS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if filename.endswith('.csv'):
        rows = [line.split(',') for line in content.strip().split('\n')]
        table = '<table>' + ''.join(
            '<tr>' + (''.join(f'<th>{c.strip()}</th>' for c in r) if i == 0 else ''.join(f'<td>{c.strip()}</td>' for c in r)) + '</tr>'
            for i, r in enumerate(rows)
        ) + '</table>'
        body = f'<h1>{filename}</h1>{table}'
    else:
        body = render_md_to_html(content)

    return f"""<!DOCTYPE html>
<html lang="zh-TW"><head><meta charset="UTF-8"><title>{filename} - 戰國三代記</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC&display=swap" rel="stylesheet">
{STYLE}</head><body>
<div class="layout">
{build_sidebar(filename)}
<div class="main">{body}</div>
</div>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == '/' or path == '':
            html = build_index()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        elif path.startswith('/doc/'):
            filename = path[5:]
            html = build_doc_page(filename)
            if html:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not found')

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Document viewer running at http://0.0.0.0:{PORT}')
    server.serve_forever()
