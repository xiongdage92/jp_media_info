import os
import re
import requests
import shutil
from bs4 import BeautifulSoup

BASE_URL = "https://subtitlecat.com"
SEARCH_URL_TEMPLATE = "https://subtitlecat.com/index.php?search={}"

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }

def search_subtitle(vid_id):
    """
    搜索字幕页面链接 / Search subtitle page link
    """
    search_url = SEARCH_URL_TEMPLATE.format(vid_id)
    try:
        response = requests.get(search_url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.startswith('subs/') or href.startswith('/subs/'):
                if href.endswith('.html'):
                    full_url = href if href.startswith('http') else BASE_URL + (href if href.startswith('/') else '/' + href)
                    return full_url
    except Exception as e:
        print(f"搜索字幕页面失败 / Error searching subtitle for {vid_id}: {e}")
    return None

def get_download_link(detail_url):
    """
    获取字幕下载链接 / Get subtitle download link
    """
    try:
        response = requests.get(detail_url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        sub_singles = soup.find_all('div', class_='sub-single')
        for sub in sub_singles:
            text = sub.get_text()
            if "Chinese (Simplified)" in text or "zh-CN" in str(sub):
                link = sub.find('a', class_='green-link', href=True)
                if link:
                    href = link['href']
                    full_download_url = href if href.startswith('http') else BASE_URL + (href if href.startswith('/') else '/' + href)
                    return full_download_url
    except Exception as e:
        print(f"获取下载链接失败 / Error getting download link from {detail_url}: {e}")
    return None

def download_file(url, save_path):
    """
    下载文件 / Download file
    """
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"下载文件失败 / Error downloading file: {e}")
        return False

def check_id_in_filename(vid_id, filename):
    """
    检查文件名中是否包含番号 / Check if ID is in filename
    """
    try:
        if re.search(re.escape(vid_id), filename, re.IGNORECASE):
            return "是"
        return "否"
    except Exception:
        return "否"

def process_str(vid_id, origin_str_dir, str_dir):
    """
    处理字幕的主流程 / Main process for subtitles
    """
    result = {
        'str_status': '失败',
        'str_detail_page_url': '',
        'str_download_url': '',
        'str_original_filename': '',
        'str_renamed_filename': '',
        'id_in_filename_flag': '否'
    }
    
    # 1. 搜索字幕详情页 / Search detail page
    detail_url = search_subtitle(vid_id)
    if not detail_url:
        print(f"未找到字幕页面 / No subtitle page found for {vid_id}")
        return result
    result['str_detail_page_url'] = detail_url
    
    # 2. 获取下载链接 / Get download link
    download_url = get_download_link(detail_url)
    if not download_url:
        print(f"未找到简中字幕下载链接 / No zh-CN subtitle found for {vid_id}")
        return result
    result['str_download_url'] = download_url
    
    # 3. 解析文件名 / Parse filename
    original_filename = os.path.basename(download_url)
    if '?' in original_filename:
        original_filename = original_filename.split('?')[0]
    result['str_original_filename'] = original_filename
    
    renamed_filename = f"{vid_id}.srt"
    result['str_renamed_filename'] = renamed_filename
    
    result['id_in_filename_flag'] = check_id_in_filename(vid_id, original_filename)
    
    # 4. 下载并复制 / Download and copy
    origin_file_path = os.path.join(origin_str_dir, original_filename)
    renamed_file_path = os.path.join(str_dir, renamed_filename)
    
    if download_file(download_url, origin_file_path):
        try:
            shutil.copy2(origin_file_path, renamed_file_path)
            result['str_status'] = '成功'
        except Exception as e:
            print(f"复制字幕文件失败 / Failed to copy subtitle file: {e}")
            
    return result
