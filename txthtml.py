import os
import requests
import subprocess
from vars import CREDIT
from pyrogram import Client, filters
from pyrogram.types import Message

# Function to extract topic, title, and URL from the text file
def extract_names_and_urls(file_content):
    lines = file_content.strip().split("\n")
    data = []
    for line in lines:
        if ":" in line:
            name, url = line.split(":", 1)
            name = name.strip()
            url = url.strip()
            if " - " in name:
                topic, title = name.split(" - ", 1)
            else:
                topic, title = "General", name
            data.append((topic.strip(), title.strip(), url))
    return data

# Function to categorize URLs topic-wise
def categorize_urls(urls):
    videos, pdfs, others = {}, {}, {}
    for topic, title, url in urls:
        if any(x in url for x in ["akamaized.net/", "1942403233.rsc.cdn77.org/", ".m3u8", ".mp4"]):
            videos.setdefault(topic, []).append((title, url))
        elif "pdf" in url:
            pdfs.setdefault(topic, []).append((title, url))
        else:
            others.setdefault(topic, []).append((title, url))
    return videos, pdfs, others

# Function to generate HTML file with Accordion + Search
def generate_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)[0]

    def build_section(data_dict, section_class):
        html = ""
        for topic, items in data_dict.items():
            html += f"""
            <button class="accordion">{topic}</button>
            <div class="panel">
                <div class="{section_class}">
            """
            for title, url in items:
                if section_class == "video-list":
                    html += f'<a href="#" onclick="playVideo(\'{url}\')">{title}</a>'
                else:
                    html += f'<a href="{url}" target="_blank">{title}</a>'
            html += "</div></div>"
        return html

    video_links = build_section(videos, "video-list")
    pdf_links = build_section(pdfs, "pdf-list")
    other_links = build_section(others, "other-list")

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{file_name_without_extension}</title>
<link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
<style>
    body {{ font-family: Arial, sans-serif; background: #f5f7fa; padding: 20px; }}
    h1 {{ text-align: center; }}
    .accordion {{ background-color: #007bff; color: white; cursor: pointer; padding: 12px; margin: 5px 0; width: 100%; border: none; text-align: left; font-size: 18px; border-radius: 8px; transition: 0.4s; }}
    .accordion:hover {{ background-color: #0056b3; }}
    .panel {{ padding: 0 15px; display: none; overflow: hidden; background: white; border: 1px solid #ccc; border-radius: 0 0 8px 8px; margin-bottom: 10px; }}
    .video-list a, .pdf-list a, .other-list a {{ display: block; padding: 8px; text-decoration: none; color: #007bff; border-bottom: 1px solid #eee; }}
    .video-list a:hover, .pdf-list a:hover, .other-list a:hover {{ background: #007bff; color: white; }}
    .search-bar {{ margin: 15px auto; max-width: 600px; text-align: center; }}
    .search-bar input {{ width: 100%; padding: 10px; border: 2px solid #007bff; border-radius: 6px; font-size: 16px; }}
    .no-results {{ text-align: center; color: red; font-weight: bold; display: none; }}
</style>
</head>
<body>
    <h1>{file_name_without_extension}</h1>
    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search videos, PDFs, or resources..." oninput="filterContent()">
    </div>
    <div id="noResults" class="no-results">No results found.</div>

    <h2>Videos</h2>
    {video_links}

    <h2>PDFs</h2>
    {pdf_links}

    <h2>Others</h2>
    {other_links}

<script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
<script>
    var acc = document.getElementsByClassName("accordion");
    for (let i = 0; i < acc.length; i++) {{
        acc[i].addEventListener("click", function() {{
            this.classList.toggle("active");
            var panel = this.nextElementSibling;
            panel.style.display = panel.style.display === "block" ? "none" : "block";
        }});
    }}

    function playVideo(url) {{
        if (url.includes('.m3u8')) {{
            window.open(url, "_blank");
        }} else {{
            window.open(url, "_blank");
        }}
    }}

    function filterContent() {{
        let searchTerm = document.getElementById("searchInput").value.toLowerCase();
        let links = document.querySelectorAll(".video-list a, .pdf-list a, .other-list a");
        let accordions = document.querySelectorAll(".accordion");
        let panels = document.querySelectorAll(".panel");
        let hasResults = false;

        for (let i = 0; i < links.length; i++) {{
            let text = links[i].textContent.toLowerCase();
            if (text.includes(searchTerm)) {{
                links[i].style.display = "block";
                let panel = links[i].closest(".panel");
                if (panel) panel.style.display = "block";
                hasResults = true;
            }} else {{
                links[i].style.display = "none";
            }}
        }}

        for (let j = 0; j < panels.length; j++) {{
            let visibleLinks = panels[j].querySelectorAll("a[style='display: block;']");
            accordions[j].style.display = visibleLinks.length > 0 ? "block" : "none";
        }}

        document.getElementById("noResults").style.display = hasResults ? "none" : "block";
    }}
</script>
</body>
</html>
"""
    return html_template

# Function to download video using FFmpeg
def download_video(url, output_path):
    command = f"ffmpeg -i {url} -c copy {output_path}"
    subprocess.run(command, shell=True, check=True)
