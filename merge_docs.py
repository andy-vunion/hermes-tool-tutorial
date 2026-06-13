#!/usr/bin/env python3
"""Merge industry-chain-methodology.html chapters into 10x-tracker-claude.html"""
import re

# Read the industry chain HTML
with open('/home/admin/tool-tutorial/industry-chain-methodology.html') as f:
    chain_html = f.read()

# Extract chapters from chain HTML (everything between <div id="main"> and </div> before <script>)
main_match = re.search(r'<div id="main">(.*?)</div>\s*<script>', chain_html, re.DOTALL)
if not main_match:
    print("ERROR: Could not extract main content from industry-chain-methodology.html")
    exit(1)

chain_chapters = main_match.group(1).strip()

# Extract nav links from chain HTML
nav_match = re.search(r'<nav id="nav">(.*?)</nav>', chain_html, re.DOTALL)
chain_nav_links = nav_match.group(1).strip() if nav_match else ''

# Read the 10x tracker HTML
with open('/home/admin/tool-tutorial/10x-tracker-claude.html') as f:
    tracker_html = f.read()

# 1. Update title and meta
tracker_html = tracker_html.replace(
    '<title>十倍股全生命周期跟踪系统 — Claude fable-5 设计报告</title>',
    '<title>十倍股全生命周期跟踪系统 — 设计文档 + 产业链拆解</title>'
)
tracker_html = tracker_html.replace(
    '<div class="meta">设计模型：Claude fable-5 · 2026-06-13 · 620行</div>',
    '<div class="meta">设计模型：Claude fable-5 · 产业链拆解 v1.0 · 2026-06-13</div>'
)

# 2. Insert new nav links before </nav>
# Build nav entries for chain chapters
chain_nav_entries = ''
for link in re.finditer(r'<a href="([^"]+)"[^>]*>(.+?)</a>', chain_nav_links):
    href = link.group(1)
    text = link.group(2)
    # Prefix chain chapters to avoid ID conflicts with existing chapters
    chain_nav_entries += f'<a href="{href}" onclick="navigate(\'{href.lstrip("#")}\')">{text}</a>\n'

# Add a separator and the chain nav links
separator = '\n<a style="color:var(--accent);font-size:11px;margin:12px 0 4px;padding:4px 10px">── 产业链拆解体系 ──</a>\n'
tracker_html = tracker_html.replace('</nav>', separator + chain_nav_entries + '</nav>')

# 3. Insert chain chapters before the closing </div></div> that wraps main content
# The insertion point is before: </div></div>\n<script>
# We need to close the last chapter div properly
insertion_marker = '</div></div>\n<script>'
if insertion_marker in tracker_html:
    tracker_html = tracker_html.replace(
        insertion_marker,
        chain_chapters + '\n' + insertion_marker
    )
else:
    # Try alternative marker
    insertion_marker2 = '</div>\n</div>\n<script>'
    if insertion_marker2 in tracker_html:
        tracker_html = tracker_html.replace(
            insertion_marker2,
            chain_chapters + '\n</div>\n</div>\n<script>'
        )
    else:
        print("WARNING: Could not find insertion marker")
        # Fallback: insert before <script>
        tracker_html = tracker_html.replace(
            '\n<script>\nfunction navigate',
            chain_chapters + '\n</div>\n</div>\n<script>\nfunction navigate'
        )

# 4. Update the "返回工具箱" link in chain chapters to point correctly
tracker_html = tracker_html.replace(
    'href="index.html"',
    'href="index.html"',
    1  # Only first occurrence (tracker's own back link)
)

# Write merged file
with open('/home/admin/tool-tutorial/10x-tracker-claude.html', 'w') as f:
    f.write(tracker_html)

print(f"Merged: {len(tracker_html)} chars")
print(f"Chain nav entries added: {chain_nav_entries.count('<a href')}")
