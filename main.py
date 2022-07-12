import csv
import json
import os
import re

import requests
from bs4 import BeautifulSoup


def request(url, headers, timeout):
    try:
        r = requests.get(
            url=url,
            headers=headers,
            timeout=timeout
        )
        r.raise_for_status()
        return r
    except:
        return None


def get_info(url, headers, timeout):
    html = request(
        url=url,
        headers=headers,
        timeout=timeout
    ).text
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1", class_="video-title").text.strip()
    print(f"[title]: {title}")

    date = soup.find("span", class_="pudate").text.strip()
    print(f"[date] {date}")

    intro = soup.find("span", class_="desc-info-text").text.strip()
    print(f"[intro]\n{intro}")

    tags = []
    tags_ul = soup.find("ul", class_="tag-area")
    for tag_li in tags_ul.find_all("li"):
        tags.append(tag_li.text.strip())
    tags = list(filter(
        bool,
        tags
    ))
    print(f"[tags] {tags}")

    # num_pages = soup.find("span", class_="cur-page").text.strip().split("/")[1][:-1]
    # print(f"[#pages] {num_pages}")

    window_initial_state_script = ""
    for script in soup.find_all("script"):
        try:
            if "window.__INITIAL_STATE__" in script.string and "pages" in script.string:
                window_initial_state_script = script.string[25:]
                break
        except TypeError:
            pass
    window_initial_state_script = re.compile(r"(\{.*\});\(function\(\)\{").search(window_initial_state_script).group(1)
    initial_state_dict = json.loads(s=window_initial_state_script)

    pages = initial_state_dict["videoData"]["pages"]
    pages_info = {
        page_dict['page']: page_dict['part']
        for page_dict in pages
    }
    print(pages_info)

    return {
        "title": title,
        "date": date,
        "intro": intro,
        "tags": tags,
        "pages_info": pages_info,
    }


def get_content(url, p, headers, timeout):
    p_url = f"{url}?p={p}"
    print(f"[p_url]: {p_url}")

    html = request(
        url=p_url,
        headers=headers,
        timeout=timeout
    ).text
    soup = BeautifulSoup(html, "html.parser")

    window_playinfo_script = ""
    for script in soup.find_all("script"):
        try:
            if "window.__playinfo__" in script.string and "baseUrl" in script.string:
                window_playinfo_script = script.string[20:]
                break
        except TypeError:
            pass
    playinfo_dict = json.loads(s=window_playinfo_script)

    video_url = playinfo_dict["data"]["dash"]["video"][0]["baseUrl"]
    print(f"[video_url]: {video_url}")
    audio_url = playinfo_dict["data"]["dash"]["audio"][0]["baseUrl"]
    print(f"[audio_url]: {audio_url}")

    audio_content = request(
        audio_url,
        headers=headers,
        timeout=timeout,
    ).content
    video_content = requests.get(
        video_url,
        headers=headers,
        timeout=timeout,
    ).content

    return {
        "audio_url": audio_url,
        "audio_content": audio_content,
        "video_url": video_url,
        "video_content": video_content,
    }


def main(bv_id: str):
    url = f"https://www.bilibili.com/video/{bv_id}"

    headers = {
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
    }
    timeout = 60

    info = get_info(
        url=url,
        headers=headers,
        timeout=timeout
    )

    for p in range(1, 5 + 1):
        content_p = get_content(
            url=url,
            p=p,
            headers=headers,
            timeout=timeout
        )

        audio_path = f"{info['title']}_p{p}_{info['pages_info'][p]}_audio.m4s"
        video_path = f"{info['title']}_p{p}_{info['pages_info'][p]}_video.m4s"
        with open(audio_path, "wb") as f_audio:
            f_audio.write(content_p["audio_content"])
        with open(video_path, "wb") as f_video:
            f_video.write(content_p["video_content"])

        mp4_file_name = f"{info['title']}_{p}_{info['pages_info'][p]}.mp4"
        os.system(f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -codec copy "{mp4_file_name}"', )

        os.remove(audio_path)
        os.remove(video_path)


if __name__ == '__main__':
    bv_id = "BV19B4y1W76i"
    main(bv_id=bv_id)
