import os
import csv
import time
from datetime import datetime
from jp_media_info_nfo import process_nfo
from jp_media_info_pics import process_pics
from jp_media_info_str import process_str

def read_actress_dict(csv_path):
    """
    读取女优映射表 / Read actress dictionary
    """
    actress_dict = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                origin_name = row.get('origin_name', '').strip()
                if origin_name:
                    actress_dict[origin_name] = {
                        'tmbd_name': row.get('tmbd_name', ''),
                        'tmdbid': row.get('tmdbid', '')
                    }
    except Exception as e:
        print(f"读取演员列表失败 / Failed to read actress list: {e}")
    return actress_dict

def read_target_vids(csv_path):
    """
    读取目标番号列表 / Read target video IDs
    """
    vids = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row and row[0].strip():
                    vids.append(row[0].strip())
    except Exception as e:
        print(f"读取番号列表失败 / Failed to read target vids: {e}")
    return vids

def main():
    """
    主函数 / Main orchestration function
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 相对路径定义 / Relative paths definition
    target_vids_path = os.path.join(base_dir, 'target_vids.csv')
    actress_list_path = os.path.join(base_dir, 'jp_actress_select_list.csv')
    
    # 创建输出目录 / Create output directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir_name = f"output_jp_media_info_{timestamp}"
    output_dir = os.path.join(base_dir, output_dir_name)
    
    nfo_dir = os.path.join(output_dir, 'nfo')
    pics_dir = os.path.join(output_dir, 'pics')
    str_dir = os.path.join(output_dir, 'str')
    origin_str_dir = os.path.join(output_dir, 'origin_str')
    
    os.makedirs(nfo_dir, exist_ok=True)
    os.makedirs(pics_dir, exist_ok=True)
    os.makedirs(str_dir, exist_ok=True)
    os.makedirs(origin_str_dir, exist_ok=True)
    
    log_csv_path = os.path.join(output_dir, 'scraper_log.csv')
    
    # 读取输入文件 / Read input files
    print("初始化数据 / Initializing data...")
    actress_dict = read_actress_dict(actress_list_path)
    target_vids = read_target_vids(target_vids_path)
    
    if not target_vids:
        print("未找到需要处理的番号 / No target vids found.")
        return
        
    print(f"共发现 {len(target_vids)} 个待处理番号 / Found {len(target_vids)} vids to process.")
    
    # 准备日志 / Prepare log
    log_headers = [
        'vids_id', 
        'nfo_status', 
        'info_link', 
        'javtxt_title', 
        'javtxt_release_date', 
        'javtxt_actors', 
        'javtxt_tags', 
        'pics_status', 
        'javbus_image_url', 
        'str_status', 
        'str_detail_page_url', 
        'str_download_url', 
        'str_original_filename', 
        'str_renamed_filename', 
        'id_in_filename_flag', 
        'process_datetime'
    ]
    
    with open(log_csv_path, 'w', encoding='utf-8', newline='') as log_file:
        writer = csv.DictWriter(log_file, fieldnames=log_headers)
        writer.writeheader()
        
        for vid_id in target_vids:
            print(f"\\n开始处理番号 / Processing: {vid_id}")
            process_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. 生成 NFO / Generate NFO
            print(f"  [{vid_id}] 1. 正在获取 NFO 信息 / Generating NFO...")
            nfo_result = process_nfo(vid_id, nfo_dir, actress_dict)
            
            # 2. 生成图片 / Process Pics
            print(f"  [{vid_id}] 2. 正在下载图片 / Downloading pictures...")
            video_info = nfo_result.pop('video_info', {})
            image_url = video_info.get('image_url')
            pics_result = process_pics(vid_id, pics_dir, image_url)
            
            # 3. 生成字幕 / Process Subtitles
            print(f"  [{vid_id}] 3. 正在搜索字幕 / Searching subtitles...")
            str_result = process_str(vid_id, origin_str_dir, str_dir)
            
            # 4. 记录日志 / Logging
            log_row = {
                'vids_id': vid_id,
                'process_datetime': process_datetime
            }
            log_row.update(nfo_result)
            log_row.update(pics_result)
            log_row.update(str_result)
            
            writer.writerow(log_row)
            log_file.flush() # 实时刷新日志 / Flush log in real time
            
            print(f"完成处理番号 / Finished processing: {vid_id}")
            
            # 友好请求 / Be nice to servers
            time.sleep(1)

    print(f"\\n所有任务已完成！日志保存在: {log_csv_path}")
    print(f"All tasks completed! Logs saved to: {log_csv_path}")

if __name__ == "__main__":
    main()
