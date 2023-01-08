# bilibili-spider

A tool for scratching videos from bilibili.  
B站视频爬虫脚本。

## Dependencies · 依赖
```bash
sudo apt install ffmpeg
pip install -r requirements.txt
```

## Usage · 使用方法
```bash
python main.py --bid BV19B4y1W76i
```

`bid` specifies the BV number of the video.  
`bid`指定视频的BV号。

The BV number of a bilibili video can be obtained from its link. For example, the BV number of the link "https://www.bilibili.com/video/BV19B4y1W76i/?spm_id_from=333.337.search-card.all.click&vd_source=cb6bdc56db66ac895c0f3d6912c94028" is "BV19B4y1W76i", which is behind "https://www.bilibili.com/video/".  
B站视频的BV号可以从视频的网页链接获取。比如，网页链接 "https://www.bilibili.com/video/BV19B4y1W76i/?spm_id_from=333.337.search-card.all.click&vd_source=cb6bdc56db66ac895c0f3d6912c94028" 中的BV号是 "BV19B4y1W76i" 。它位于 "https://www.bilibili.com/video/" 之后。