import argparse
import json
import os
import re

import requests
from bs4 import BeautifulSoup


def construct_url(bv_id: str) -> str:
    """Construct a url with the given bv id.

    :param bv_id: BV id.
    :return: Constructed url.
    """

    return f"https://www.bilibili.com/video/{bv_id}"


def clean_url(url: str) -> str:
    """Extract https://www.bilibili.com/video/BID from the url.

    :param url: Raw url.
    :return: Cleaned url.
    """

    return re.compile(r"https://www.bilibili.com/video/.+?(/|$)").search(url).group(0)


def construct_headers(url: str) -> dict:
    """Construct headers with the given url.

    :param url: Url needed to construct the headers.
    :return: Constructed headers.
    """

    return {
        'Referer': url,  # Necessary for requesting audio/video content.
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36',
    }


def request(url: str, headers: dict, timeout: int = 60) -> requests.Response:
    """Send a request.

    :param url: The url to which the request is sent.
    :param headers: Request headers.
    :param timeout: Request timeout. Default 60s.
    :return: Response from the server of the url.
    """

    try:
        # Send the request.
        r = requests.get(
            url=url,
            headers=headers,
            timeout=timeout
        )

        # Raise an exception if something goes wrong.
        r.raise_for_status()

        return r
    except:
        return requests.Response()


def get_info(url: str, headers: dict) -> dict:
    """Get video info.

    :param url: Url of the video.
    :param headers: Headers for sending requests.
    :return: Video info, including title, date, introduction, tags and page list. They are wrapped into a dict.
    """

    # Obtain the html text of the url.
    html = request(
        url=url,
        headers=headers,
    ).text

    # Parse the html.
    soup = BeautifulSoup(
        markup=html,
        features="html.parser"
    )

    # Get the video title.
    title = soup.find(
        name="h1",
        class_="video-title"
    ).text.strip()

    # Get the video date.
    date = soup.find(
        name="span",
        class_="pudate"
    ).text.strip()

    # Get the video introduction.
    intro = soup.find(
        name="span",
        class_="desc-info-text"
    ).text.strip()

    # Get the video tags.
    tags = []
    for tag_li in soup.find(
            name="ul",
            class_="tag-area"
    ).find_all(name="li"):
        tag = tag_li.text.strip()
        # It's really a tag if it is not an empty string.
        if len(tag) != 0:
            tags.append(tag)

    # Get the video pages.
    window_initial_state_script = ""  # The script contains page info.
    for script in soup.find_all(name="script"):
        try:
            if "window.__INITIAL_STATE__" in script.string and "pages" in script.string:
                window_initial_state_script = script.string
                break
        except TypeError:
            pass
    # Extract the json from the script.
    pattern = re.compile(pattern=r"(\{.*\});")
    window_initial_state_json = pattern.search(string=window_initial_state_script).group(1)
    # Convert the json to dict.
    window_initial_state_dict = json.loads(s=window_initial_state_json)
    # Extract page info.
    pages = window_initial_state_dict["videoData"]["pages"]
    pages = {
        int(page_dict['page']): page_dict['part']
        for page_dict in pages
    }

    return {
        "title": title,
        "date": date,
        "intro": intro,
        "tags": tags,
        "pages": pages,
    }


def get_content(url: str, p: int, headers: dict) -> dict:
    """Get video content (audio & video).

    :param url: Url of the video.
    :param p: Page number.
    :param headers: Headers for sending requests.
    :return: Video content (audio & video).
    """

    # Construct the page url.
    p_url = f"{url}?p={p}"
    print(f"[p_url]: {p_url}")

    # Obtain the html text of the url.
    html = request(
        url=p_url,
        headers=headers,
    ).text

    # parse the html.
    soup = BeautifulSoup(
        markup=html,
        features="html.parser"
    )

    # Get the urls of the audio & video.
    window_playinfo_script = ""  # The script contains the audio & video urls.
    for script in soup.find_all(name="script"):
        try:
            if "window.__playinfo__" in script.string and "baseUrl" in script.string:
                window_playinfo_script = script.string
                break
        except TypeError:
            pass
    # Extract the json from the script.
    pattern = re.compile(pattern=r"(\{.*\})")
    window_playinfo_json = pattern.search(string=window_playinfo_script).group(0)
    # Convert the json to dict.
    window_playinfo_dict = json.loads(s=window_playinfo_json)
    # Video url.
    video_url = window_playinfo_dict["data"]["dash"]["video"][0]["baseUrl"]
    # Audio url.
    audio_url = window_playinfo_dict["data"]["dash"]["audio"][0]["baseUrl"]
    print(f"[video_url]: {video_url}")
    print(f"[audio_url]: {audio_url}")

    # Get the content of the audio.
    audio_content = request(
        audio_url,
        headers=headers,
    ).content
    # Get the content of the video.
    video_content = requests.get(
        video_url,
        headers=headers,
    ).content

    return {
        "audio_url": audio_url,
        "audio_content": audio_content,
        "video_url": video_url,
        "video_content": video_content,
    }


def save_content(content: dict, dp_root: str, filename: str):
    """Save video content (mp4 format)

    :param content: Obtained video content (audio url, audio content, video url, video content).
    :param dp_root: Root directory for saving videos.
    :param filename: Filename of the page.
    """

    # Write the audio.
    fp_audio = os.path.join(
        dp_root,
        f"{filename}_audio.m4s"
    )
    with open(fp_audio, "wb") as f_audio:
        f_audio.write(content["audio_content"])

    # Write the video.
    fp_video = os.path.join(
        dp_root,
        f"{filename}_video.m4s"
    )
    with open(fp_video, "wb") as f_video:
        f_video.write(content["video_content"])

    # Merge the audio and video into an mp4 file.
    fp_mp4 = os.path.join(
        dp_root,
        f"{filename}.mp4"
    )
    os.system(f'ffmpeg -y -i "{fp_video}" -i "{fp_audio}" -codec copy "{fp_mp4}"', )

    # Remove the audio and video file.
    os.remove(fp_audio)
    os.remove(fp_video)


def main(bv_id: str = None, url: str = None):
    if url is None:
        url = construct_url(bv_id=bv_id)
    else:
        url = clean_url(url=url)
    headers = construct_headers(url=url)

    # Obtain title, date, intro, tags, and page info.
    info = get_info(
        url=url,
        headers=headers,
    )
    for k, v in info.items():
        print(f"[{k}]: {v}")

    # Make a directory for saving the content.
    dp_content = os.path.join("videos", f"{info['title']}")
    os.makedirs(
        name=dp_content,
        exist_ok=True
    )

    # Obtain and save video content.
    for p, p_title in info["pages"].items():
        content = get_content(
            url=url,
            p=p,
            headers=headers,
        )

        save_content(
            content=content,
            dp_root=dp_content,
            filename=f"p{p} {p_title}"
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bid", help="ID of the video.")
    parser.add_argument("--url", help="Url of the video.")
    args = parser.parse_args()

    assert args.bid is not None or args.url is not None

    main(
        bv_id=args.bid,
        url=args.url,
    )
