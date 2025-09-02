import os
import requests
import subprocess
from vars import CREDIT
from pyrogram import Client, filters
from pyrogram.types import Message

# Function to extract names, topics, and URLs from the text file
def extract_names_and_urls(file_content):
    lines = file_content.strip().split("\n")
    data = []
    for line in lines:
        if ":" in line:
            left, url = line.split(":", 1)
            if "-" in left:
                topic, name = left.split("-", 1)
                data.append((topic.strip(), name.strip(), url.strip()))
            else:
                data.append(("General", left.strip(), url.strip()))
    return data

# Function to categorize URLs topic-wise
def categorize_urls(urls):
    categorized = {}

    for topic, name, url in urls:
        if topic not in categorized:
            categorized[topic] = {"videos": [], "pdfs": [], "others": []}

        new_url = url
        if "akamaized.net/" in url or "1942403233.rsc.cdn77.org/" in url:
            new_url = f"https://www.khanglobalstudies.com/player?src={url}"
            categorized[topic]["videos"].append((name, new_url))

        elif "d1d34p8vz63oiq.cloudfront.net/" in url:
            new_url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token=YOUR_TOKEN"
            categorized[topic]["videos"].append((name, new_url))

        elif "youtube.com/embed" in url:
            yt_id = url.split("/")[-1]
            new_url = f"https://www.youtube.com/watch?v={yt_id}"
            categorized[topic]["videos"].append((name, new_url))

        elif ".m3u8" in url or ".mp4" in url:
            categorized[topic]["videos"].append((name, url))
        elif ".pdf" in url:
            categorized[topic]["pdfs"].append((name, url))
        else:
            categorized[topic]["others"].append((name, url))

    return categorized

# Function to generate HTML with Accordion + Video.js player
def generate_html(file_name, categorized):
    file_name_without_extension = os.path.splitext(file_name)[0]

    accordion_content = ""
    for topic, sections in categorized.items():
        video_links = "".join(f'<a href="#" onclick="playVideo(\'{url}\')">{name}</a>'
                              for name, url in sections["videos"])
        pdf_links = "".join(f'<a href="{url}" target="_blank">{name}</a>'
                            for name, url in sections["pdfs"])
        other_links = "".join(f'<a href="{url}" target="_blank">{name}</a>'
                              for name, url in sections["others"])

        accordion_content += f"""
        <button class="accordion">{topic}</button>
        <div class="panel">
            <div class="video-list">{video_links}</div>
            <div class="pdf-list">{pdf_links}</div>
            <div class="other-list">{other_links}</div>
        </div>
        """

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_name_without_extension}</title>
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f5f7fa;
            margin: 0;
            padding: 0;
        }}
        .header {{
            background: #1c1c1c;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }}
        .subheading {{
            font-size: 16px;
            margin-top: 5px;
            color: #ccc;
        }}
        .accordion {{
            background-color: #007bff;
            color: white;
            cursor: pointer;
            padding: 15px;
            width: 100%;
            text-align: left;
            font-size: 18px;
            border: none;
            outline: none;
            transition: 0.3s;
            margin: 5px 0;
            border-radius: 5px;
        }}
        .accordion:hover {{
            background-color: #0056b3;
        }}
        .panel {{
            padding: 0 15px;
            display: none;
            background-color: white;
            overflow: hidden;
            border-radius: 5px;
        }}
        .video-list a, .pdf-list a, .other-list a {{
            display: block;
            padding: 10px;
            margin: 5px 0;
            background: #f1f1f1;
            color: #007bff;
            text-decoration: none;
            border-radius: 5px;
        }}
        .video-list a:hover, .pdf-list a:hover, .other-list a:hover {{
            background: #007bff;
            color: white;
        }}
        #video-player {{
            margin: 20px auto;
            width: 90%;
            max-width: 800px;
            display: none;
        }}
        .footer {{
            margin-top: 30px;
            padding: 15px;
            background: #1c1c1c;
            color: white;
            text-align: center;
        }}
        .search-bar {{
            margin: 20px auto;
            width: 90%;
            max-width: 600px;
            text-align: center;
        }}
        .search-bar input {{
            width: 100%;
            padding: 10px;
            border: 2px solid #007bff;
            border-radius: 5px;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="header">
        {file_name_without_extension}
        <div class="subheading">📥 Extracted By: {CREDIT}</div>
    </div>

    <div id="video-player">
        <video id="engineer-babu-player" class="video-js vjs-default-skin" controls preload="auto"></video>
    </div>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search..." oninput="filterContent()">
    </div>

    {accordion_content}

    <div class="footer">📥 Extracted By: {CREDIT}</div>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script>
        const player = videojs('engineer-babu-player');

        function playVideo(url) {{
            document.getElementById('video-player').style.display = 'block';
            if (url.includes('.m3u8')) {{
                player.src({{ src: url, type: 'application/x-mpegURL' }});
            }} else {{
                player.src({{ src: url, type: 'video/mp4' }});
            }}
            player.play();
        }}

        // Accordion toggle
        const acc = document.getElementsByClassName("accordion");
        for (let i = 0; i < acc.length; i++) {{
            acc[i].addEventListener("click", function() {{
                this.classList.toggle("active");
                let panel = this.nextElementSibling;
                panel.style.display = panel.style.display === "block" ? "none" : "block";
            }});
        }}

        // Search filter
        function filterContent() {{
            const searchTerm = document.getElementById("searchInput").value.toLowerCase();
            const acc = document.getElementsByClassName("accordion");
            let foundAny = false;

            for (let i = 0; i < acc.length; i++) {{
                let panel = acc[i].nextElementSibling;
                let links = panel.getElementsByTagName("a");
                let hasMatch = false;

                for (let link of links) {{
                    if (link.textContent.toLowerCase().includes(searchTerm)) {{
                        link.style.display = "block";
                        hasMatch = true;
                        foundAny = true;
                    }} else {{
                        link.style.display = "none";
                    }}
                }}

                panel.style.display = hasMatch ? "block" : "none";
            }}
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
