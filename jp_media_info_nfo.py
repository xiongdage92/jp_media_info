import os
import re
import requests
from bs4 import BeautifulSoup

def get_headers():
    """
    获取请求头 / Get HTTP headers
    """
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
    }

def fetch_webpage(url):
    """
    获取网页内容 / Fetch webpage content
    """
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"获取网页失败 / Failed to fetch {url}: {e}")
        return None

def search_javtxt_link(vid_id):
    """
    在 javtxt 搜索影片链接 / Search video link on javtxt
    """
    search_base_url = 'https://l.javtxt.club/search'
    detail_base_url = 'https://d.javtxt.club'
    params = {'type': 'id', 'q': vid_id}
    
    try:
        response = requests.get(search_base_url, params=params, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        work_link = soup.select_one('.works .work')
        if work_link and work_link.get('href'):
            href = work_link.get('href')
            return f"{detail_base_url}{href}"
    except Exception as e:
        print(f"搜索 javtxt 链接失败 / Error searching javtxt for {vid_id}: {e}")
    return None

def parse_javtxt_info(html_content, vid_id):
    """
    解析 javtxt 网页信息 / Parse javtxt info
    """
    if not html_content:
        return None
        
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        info = {}
        
        # 标题 / Title
        title_zh_elem = soup.find('h2', class_='title is-4 text-zh')
        title_jp_elem = soup.find('h1', class_='title is-4 text-jp')
        title_zh = title_zh_elem.get_text(strip=True) if title_zh_elem else ""
        title_jp = title_jp_elem.get_text(strip=True) if title_jp_elem else ""
        
        info['title'] = f"{vid_id} {title_zh if title_zh else title_jp}"
        info['origin_zh_title'] = title_zh
        info['origin_jp_title'] = title_jp
        
        origin_title_elem = soup.find('title')
        info['origin_url_title'] = origin_title_elem.get_text(strip=True) if origin_title_elem else ""
        
        # 属性 / Attributes
        attributes = {}
        dd_elements = soup.find_all('dd')
        for dd in dd_elements:
            text = dd.get_text(strip=True)
            next_dt = dd.find_next('dt')
            if next_dt:
                if '📅 发行时间' in text:
                    release_date = next_dt.get_text(strip=True)
                    attributes['release_date'] = release_date
                    year_match = re.search(r'(\d{4})', release_date)
                    info['year'] = year_match.group(1) if year_match else ""
                elif '🆔 番号' in text:
                    info['origin_code'] = next_dt.get_text(strip=True)
                elif '🗂️ 番号前缀' in text:
                    info['origin_code_prefix'] = next_dt.get_text(strip=True)
                elif '🗂️ 系列' in text:
                    series_link = next_dt.find('a')
                    if series_link:
                        info['origin_series'] = series_link.get_text(strip=True)
                elif '🎥 片商' in text:
                    publisher_link = next_dt.find('a')
                    if publisher_link:
                        info['origin_publisher'] = publisher_link.get_text(strip=True)
                elif '🔖 厂牌' in text:
                    company_link = next_dt.find('a')
                    if company_link:
                        info['origin_company'] = company_link.get_text(strip=True)
        
        # 描述 / Plot
        text_zh_elem = soup.find('div', class_='text-zh')
        text_jp_elem = soup.find('p', class_='text-jp')
        info['origin_zh_desc'] = text_zh_elem.get_text(strip=True) if text_zh_elem else ""
        info['origin_jp_desc'] = text_jp_elem.get_text(strip=True) if text_jp_elem else ""
        
        if info.get('origin_zh_desc') and info.get('origin_jp_desc'):
            info['plot'] = f"{info['origin_zh_desc']}\\n{info['origin_jp_desc']}"
        else:
            info['plot'] = info.get('origin_zh_desc', '') or info.get('origin_jp_desc', '')
        info['outline'] = info['plot']
        
        # 演员 / Actors
        actors = []
        actress_links = soup.find_all('a', class_='actress')
        for i, actress_link in enumerate(actress_links):
            actors.append({
                'origin_name': actress_link.get_text(strip=True),
                'order': i
            })
        info['actors'] = actors
        
        # 标签 / Tags
        tags = []
        tag_links = soup.find_all('a', class_='tag is-white')
        for tag_link in tag_links:
            tags.append(tag_link.get_text(strip=True))
        info['origin_tags'] = tags
        
        info['releasedate'] = attributes.get('release_date', '')
        info['premiered'] = attributes.get('release_date', '')
        info['country'] = '392'
        info['filename'] = f"{vid_id}.mp4"
        info['jp_vid_number'] = vid_id
        
        return info
    except Exception as e:
        print(f"解析 javtxt 失败 / Failed to parse javtxt: {e}")
        return None

def parse_javbus_info(html_content):
    """
    解析 javbus 网页信息 / Parse javbus info
    """
    if not html_content:
        return {}
        
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        info = {}
        
        director_elem = soup.find('p', string=re.compile(r'導演:'))
        if director_elem and director_elem.find('a'):
            info['director'] = director_elem.find('a').get_text(strip=True)
            
        release_date_elem = soup.find('p', string=re.compile(r'發行日期:'))
        if release_date_elem:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', release_date_elem.get_text(strip=True))
            if date_match:
                info['javbus_release_date'] = date_match.group(1)
                
        duration_elem = soup.find('p', string=re.compile(r'長度:'))
        if duration_elem:
            duration_match = re.search(r'(\d+)', duration_elem.get_text(strip=True))
            if duration_match:
                info['duration'] = duration_match.group(1) + '分钟'
                
        big_image_elem = soup.find('a', class_='bigImage')
        if big_image_elem:
            image_href = big_image_elem.get('href', '')
            if image_href and not image_href.startswith('http'):
                info['image_url'] = f"https://www.javbus.com{image_href}"
            else:
                info['image_url'] = image_href
                
        return info
    except Exception as e:
        print(f"解析 javbus 失败 / Failed to parse javbus: {e}")
        return {}

def generate_nfo_content(info, actress_dict):
    """
    生成 NFO 内容 / Generate NFO content
    """
    nfo_content = f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<movie>
    <title>{info.get('title', '')}</title>
    <origin-zh-title>{info.get('origin_zh_title', '')}</origin-zh-title>
    <origin-jp-title>{info.get('origin_jp_title', '')}</origin-jp-title>
    <origin-url-title>{info.get('origin_url_title', '')}</origin-url-title>
    <year>{info.get('year', '')}</year>
    <plot>{info.get('plot', '')}</plot>
    <outline>{info.get('outline', '')}</outline>
    <releasedate>{info.get('releasedate', '')}</releasedate>
    <premiered>{info.get('premiered', '')}</premiered>
    <country>{info.get('country', '392')}</country>
    <origin-zh-desc>{info.get('origin_zh_desc', '')}</origin-zh-desc>
    <origin-jp-desc>{info.get('origin_jp_desc', '')}</origin-jp-desc>
    <thumb aspect="poster">{info.get('jp_vid_number', '')}-poster.jpg</thumb>
    <thumb aspect="fanart">{info.get('jp_vid_number', '')}-fanart.jpg</thumb>
    <filename>{info.get('filename', '')}</filename>
    <origin-code>{info.get('origin_code', '')}</origin-code>
    <origin-code-prefix>{info.get('origin_code_prefix', '')}</origin-code-prefix>
    <origin-series>{info.get('origin_series', '')}</origin-series>
    <origin-publisher>{info.get('origin_publisher', '')}</origin-publisher>
    <origin-company>{info.get('origin_company', '')}</origin-company>
    <origin-jp-vid-number>{info.get('jp_vid_number', '')}</origin-jp-vid-number>
'''
    
    for actor in info.get('actors', []):
        origin_name = actor['origin_name']
        actress_info = actress_dict.get(origin_name, {})
        name = actress_info.get('tmbd_name', origin_name)
        tmdbid = actress_info.get('tmdbid', '')
        
        nfo_content += f'''    <actor>
        <name>{name}</name>
        <role>{name}</role>
        <origin-name>{origin_name}</origin-name>
        <type>Actor</type>
        <order>{actor['order']}</order>
        <tmdbid>{tmdbid}</tmdbid>
    </actor>
'''
    
    for tag in info.get('origin_tags', []):
        nfo_content += f"    <origin-tags>{tag}</origin-tags>\\n"
        
    if info.get('director'):
        nfo_content += f"    <director>{info['director']}</director>\\n"
        
    nfo_content += "</movie>"
    return nfo_content

def process_nfo(vid_id, nfo_dir, actress_dict):
    """
    处理 NFO 的主流程 / Main process for NFO generation
    """
    result = {
        'nfo_status': '失败',
        'info_link': '',
        'javtxt_title': '',
        'javtxt_release_date': '',
        'javtxt_actors': '',
        'javtxt_tags': '',
        'video_info': {}
    }
    
    info_link = search_javtxt_link(vid_id)
    if not info_link:
        print(f"未找到 javtxt 链接 / No javtxt link found for {vid_id}")
        return result
        
    result['info_link'] = info_link
    html_content = fetch_webpage(info_link)
    javtxt_info = parse_javtxt_info(html_content, vid_id)
    
    if not javtxt_info:
        print(f"解析 javtxt 失败 / Failed to parse javtxt for {vid_id}")
        return result
        
    # 获取 javbus 补充信息 / Get supplementary info from javbus
    javbus_url = f"https://www.javbus.com/{vid_id}"
    javbus_html = fetch_webpage(javbus_url)
    javbus_info = parse_javbus_info(javbus_html)
    
    # 合并信息 / Merge info
    video_info = {**javtxt_info, **javbus_info}
    result['video_info'] = video_info
    
    # 生成 NFO / Generate NFO file
    try:
        nfo_content = generate_nfo_content(video_info, actress_dict)
        nfo_path = os.path.join(nfo_dir, f"{vid_id}.nfo")
        with open(nfo_path, 'w', encoding='utf-8') as f:
            f.write(nfo_content)
            
        result['nfo_status'] = '成功'
        result['javtxt_title'] = video_info.get('title', '')
        result['javtxt_release_date'] = video_info.get('releasedate', '')
        result['javtxt_actors'] = ', '.join([actor['origin_name'] for actor in video_info.get('actors', [])])
        result['javtxt_tags'] = ', '.join(video_info.get('origin_tags', []))
    except Exception as e:
        print(f"写入 NFO 文件失败 / Failed to write NFO for {vid_id}: {e}")
        
    return result
