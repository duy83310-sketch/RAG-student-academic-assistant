import sys
import json
import pandas as pd
import numpy as np

# Reconfigure stdout for UTF-8 in Windows console
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
CHUNKS_DIR = PROJECT_ROOT / 'data' / 'chunks'

def analyze_csv_json():
    print("======================================================================")
    print("1. KIỂM TRA VÀ PHÂN TÍCH TẬP TIN crawl_v2 (RAW & PROCESSED)")
    print("======================================================================")
    
    csv_path = RAW_DIR / 'crawl_v2.csv'
    if not csv_path.exists():
        csv_path = Path('crawl_v2.csv')
    json_path = RAW_DIR / 'crawl_v2.json'
    if not json_path.exists():
        json_path = Path('crawl_v2.json')

    # Đọc CSV
    df_csv = pd.read_csv(csv_path)
    print(f"[*] crawl_v2.csv ({csv_path.name}): {df_csv.shape[0]} dòng, {df_csv.shape[1]} cột")
    
    # Đọc JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    print(f"[*] crawl_v2.json ({json_path.name}): {len(data_json)} bản ghi JSON")
    
    # So sánh ID
    csv_ids = set(df_csv['id'])
    json_ids = set(item['id'] for item in data_json)
    print(f"[*] Trùng khớp ID giữa CSV và JSON: {len(csv_ids.intersection(json_ids))}/{len(csv_ids)} bản ghi (100% khớp)")
    
    # Thống kê phân loại content_type
    print("\n--- Phân bố content_type ---")
    ct_counts = df_csv['content_type'].value_counts()
    for ct, count in ct_counts.items():
        print(f"  + {ct:<15}: {count:>3} bản ghi ({count/len(df_csv)*100:>5.1f}%)")
        
    # Thống kê category
    print("\n--- Phân bố category ---")
    cat_counts = df_csv['category'].value_counts()
    for cat, count in cat_counts.items():
        print(f"  + {cat:<25}: {count:>3} bản ghi ({count/len(df_csv)*100:>5.1f}%)")
        
    # Thống kê department
    print("\n--- Top phòng ban / đơn vị ban hành (department) ---")
    dept_counts = df_csv['department'].value_counts(dropna=False).head(8)
    for dept, count in dept_counts.items():
        dept_name = str(dept) if pd.notna(dept) else "[Không có / Chung]"
        print(f"  + {dept_name:<40}: {count:>3} bản ghi")
        
    # Thống kê độ dài văn bản
    df_csv['content_len'] = df_csv['content'].fillna('').apply(len)
    df_csv['word_count'] = df_csv['content'].fillna('').apply(lambda x: len(x.split()))
    print("\n--- Thống kê độ dài trường 'content' (ký tự & từ) ---")
    print(f"  + Trung bình ký tự : {df_csv['content_len'].mean():.1f} ký tự")
    print(f"  + Trung bình từ    : {df_csv['word_count'].mean():.1f} từ")
    print(f"  + Ngắn nhất        : {df_csv['content_len'].min()} ký tự ({df_csv.loc[df_csv['content_len'].idxmin(), 'title']})")
    print(f"  + Dài nhất         : {df_csv['content_len'].max()} ký tự ({df_csv.loc[df_csv['content_len'].idxmax(), 'title']})")
    print(f"  + Trung vị (Median): {df_csv['content_len'].median():.1f} ký tự")

    # Kiểm tra trường rỗng (Missing values)
    print("\n--- Kiểm tra giá trị rỗng (Missing / Null values) trong CSV ---")
    null_counts = df_csv.isnull().sum()
    for col, n_null in null_counts.items():
        if n_null > 0:
            print(f"  + Cột '{col:<18}': thiếu {n_null:>3}/{len(df_csv)} bản ghi ({n_null/len(df_csv)*100:>5.1f}%)")
            
    # Phân tích cấu trúc lồng nhau trong JSON (links, tags)
    n_has_links = sum(1 for item in data_json if item.get('links'))
    total_links = sum(len(item.get('links', [])) for item in data_json)
    n_has_tags = sum(1 for item in data_json if item.get('tags'))
    total_tags = sum(len(item.get('tags', [])) for item in data_json)
    print(f"\n--- Phân tích dữ liệu siêu liên kết (links) và nhãn (tags) trong JSON ---")
    print(f"  + Số bản ghi có links: {n_has_links}/{len(data_json)} (Tổng {total_links} links trích xuất)")
    print(f"  + Số bản ghi có tags : {n_has_tags}/{len(data_json)} (Tổng {total_tags} tags)")

def analyze_excel_loi():
    print("\n======================================================================")
    print("2. KIỂM TRA VÀ PHÂN TÍCH TẬP TIN loi_crawl.xlsx & loi_crawl_hoan_thien.xlsx")
    print("======================================================================")
    
    excel_path = PROCESSED_DIR / 'loi_crawl_hoan_thien.xlsx'
    if not excel_path.exists():
        excel_path = RAW_DIR / 'loi_crawl.xlsx'
    if not excel_path.exists():
        excel_path = Path('loi_crawl.xlsx')
        
    # Đọc sheet Hướng dẫn
    wb = pd.ExcelFile(excel_path)
    print(f"[*] Tập tin phân tích: {excel_path.name}")
    print(f"[*] Các sheet có trong Excel: {wb.sheet_names}")
    
    # Đọc sheet Lỗi OCR
    df_ocr = pd.read_excel(excel_path, sheet_name='Lỗi OCR')
    print(f"[*] Sheet 'Lỗi OCR': tổng cộng {len(df_ocr)} dòng báo lỗi")
    
    # Thống kê phân loại lỗi
    print("\n--- Phân loại lỗi OCR ---")
    loi_type = df_ocr['Lỗi mắc phải (ví dụ như sai mã học phần, tên, ...)'].value_counts()
    for lt, count in loi_type.items():
        print(f"  + {lt:<32}: {count:>3} lỗi ({count/len(df_ocr)*100:>5.1f}%)")
        
    # Thống kê tiến độ khắc phục
    fixed_series = df_ocr['Khắc phục (điền chữ đúng vào đây)']
    n_fixed = fixed_series.notna().sum()
    n_unfixed = fixed_series.isna().sum()
    print(f"\n--- Tiến độ làm sạch / sửa lỗi (Data Cleaning Status) ---")
    print(f"  + Đã sửa (Fixed)   : {n_fixed:>3}/{len(df_ocr)} ({n_fixed/len(df_ocr)*100:>5.1f}%)")
    print(f"  + Chưa sửa (Unfixed): {n_unfixed:>3}/{len(df_ocr)} ({n_unfixed/len(df_ocr)*100:>5.1f}%)")

def analyze_chunks():
    print("\n======================================================================")
    print("3. KIỂM TOÁN TẬP NGỮ LIỆU SẠCH (CLEAN CORPUS CHUNKS)")
    print("======================================================================")
    chunks_path = CHUNKS_DIR / 'clean_chunks.json'
    if not chunks_path.exists():
        chunks_path = Path('clean_chunks.json')
        
    if not chunks_path.exists():
        print("[!] Chưa có file clean_chunks.json")
        return
        
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
        
    print(f"[*] Tổng số Chunks đã tạo: {len(chunks)} chunks")
    df_c = pd.DataFrame(chunks)
    print(f"[*] Độ dài ký tự trung bình: {df_c['char_length'].mean():.1f} ký tự (Min: {df_c['char_length'].min()}, Max: {df_c['char_length'].max()})")
    print(f"[*] Số từ trung bình/chunk: {df_c['word_count'].mean():.1f} từ")
    print(f"[*] Phân bố theo Category:\n{df_c['category'].value_counts().to_string()}")

if __name__ == '__main__':
    analyze_csv_json()
    analyze_excel_loi()
    analyze_chunks()
