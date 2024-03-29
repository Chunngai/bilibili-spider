# Bilibili Spider

A tool for scratching videos from bilibili.  
B站视频爬虫脚本。

## Dependencies · 依赖
```bash
sudo apt install ffmpeg
pip install -r requirements.txt
```

## Usage · 使用方法
### 1. Passing URL · 传入URL
```bash
python main.py --url "https://www.bilibili.com/video/BV19B4y1W76i"
```

It's also acceptable if extra parameters are attached to the URL:  
URL后面如果有额外请求参数，也可以直接传入：
```bash
python main.py --url "https://www.bilibili.com/video/BV19B4y1W76i/?vd_source=cb6bdc56db66ac895c0f3d6912c94028"
```

Note that it's suggested to quote the provided URL with single quotes or double quotes. Otherwise, some substrings of the URL may be treated as commands.  
注意，最好使用单引号或双引号将URL括起来，否则URL的某些部分可能会被解析成命令。

### 2. Passing BID · 传入BV号
```bash
python main.py --bid BV19B4y1W76i
```

`bid` specifies the BID of the video.  
`bid`指定视频的BV号。

The BID of a bilibili video can be obtained from its URL. For example, the BID of "https://www.bilibili.com/video/BV19B4y1W76i/?spm_id_from=333.337.search-card.all.click&vd_source=cb6bdc56db66ac895c0f3d6912c94028" is "BV19B4y1W76i", which is behind "https://www.bilibili.com/video/".  
B站视频的BV号可以从视频的网页链接获取。比如，网页链接 "https://www.bilibili.com/video/BV19B4y1W76i/?spm_id_from=333.337.search-card.all.click&vd_source=cb6bdc56db66ac895c0f3d6912c94028" 中的BV号是 "BV19B4y1W76i" 。它位于 "https://www.bilibili.com/video/" 之后。

### 3. Data Saving · 数据存放
Scratched content are saved in `videos/`.  
爬取的视频数据存放在`videos/`。