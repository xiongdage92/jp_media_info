# JP Media Info Generator

## 项目介绍 / Project Description

本项目用于自动化获取日本媒体的元数据（NFO）、相关图片（海报、背景图）以及匹配的中文字幕文件，整理为符合 Kodi / Emby / Plex 媒体库标准的目录结构，并详细记录处理日志。

This project automates the fetching of Japanese media metadata (NFO), related images (posters, fanart), and matching Chinese subtitles. It organizes them into a standard directory structure compatible with media servers like Kodi / Emby / Plex, and maintains a detailed execution log.

## 目录结构与文件说明 / Directory Structure & Files Description

- `jp_media_info.py`: 主程序，负责调度各个模块，定义输入输出路径，并汇总生成 CSV 日志文件。 / Main orchestrator script that defines paths and generates the comprehensive CSV log.
- `jp_media_info_nfo.py`: 负责爬取并解析 javtxt 和 javbus 网站信息，生成符合规范的 NFO 文件。 / Scrapes metadata from javtxt and javbus to generate NFO files.
- `jp_media_info_pics.py`: 负责从相关网站下载媒体封面大图，并裁剪生成对应的海报（poster）和背景图（fanart）。 / Downloads fanart images and crops them into poster images.
- `jp_media_info_str.py`: 负责在 subtitlecat.com 搜索并下载匹配的简中字幕文件，支持重命名。 / Searches and downloads matching simplified Chinese subtitles from subtitlecat.com, and handles renaming.
- `target_vids.csv`: 用户需要提供的目标影片番号列表。第一列必须为番号（带表头）。 / Input list of target video IDs (vids). The first column must be the video ID with a header.
- `jp_actress_select_list.csv`: 女优映射列表，用于修正女优名字，补充 TMDBID 信息等。 / Actress mapping list used to correct actress names and add TMDBID info.
- `requirements.txt`: Python 运行依赖。 / Python dependencies for running this project.

## 输出说明 / Output Structure

每次运行主程序，会在当前目录下生成名为 `output_jp_media_info_YYYYMMDD_HHMMSS` 的文件夹，内部结构如下：
Every run will create a folder named `output_jp_media_info_YYYYMMDD_HHMMSS` in the current directory, with the following structure:

- `nfo/`: 生成的 .nfo 元数据文件。 / Generated .nfo metadata files.
- `pics/`: 生成的图片文件（包含 fanart 和 poster）。 / Generated image files (fanart and poster).
- `origin_str/`: 下载得到的原始字幕文件。 / Original subtitle files downloaded.
- `str/`: 重命名并匹配影片番号的字幕文件。 / Subtitles renamed to match the video IDs.
- `scraper_log.csv`: 记录每个番号各个环节处理状态和信息的详细日志。 / Detailed execution log for each video ID across all steps.

## 安装依赖 / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

1. 确保 `target_vids.csv` 和 `jp_actress_select_list.csv` 存在且格式正确。 / Ensure both CSV input files exist and are formatted correctly.
2. 运行主程序 / Run the main script:

```bash
python jp_media_info.py
```

## 注意事项 / Notes

- 抓取网站具有一定的反爬机制，代码中内置了 1 秒的等待间隔（可根据实际情况在主程序中调整）。 / The websites have anti-scraping mechanisms. A 1-second delay is built into the script (adjustable in the main program).
- 建议开启合适的网络代理环境以确保访问相关数据源。 / It is recommended to use an appropriate network proxy environment to access the required data sources.

