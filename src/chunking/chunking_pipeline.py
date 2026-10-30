import sys
import json
import re
import pandas as pd
from typing import List, Dict, Any

sys.stdout.reconfigure(encoding='utf-8')

def recursive_text_splitter(text: str, chunk_size: int = 700, chunk_overlap: int = 120) -> List[str]:
    """
    Splits text recursively using natural boundaries:
    paragraphs (\n\n) -> lines (\n) -> sentences (. ) -> words ( ).
    """
    text = text.strip()
    if not text:
        return []
    
    if len(text) <= chunk_size:
        return [text]
    
    separators = ["\n\n", "\n", ". ", "; ", ", ", " "]
    
    def _split(txt: str, seps: List[str]) -> List[str]:
        if len(txt) <= chunk_size or not seps:
            return [txt] if txt.strip() else []
        
        sep = seps[0]
        splits = txt.split(sep)
        
        chunks = []
        current_chunk = ""
        
        for part in splits:
            part_str = part if not current_chunk else sep + part
            if len(current_chunk) + len(part_str) <= chunk_size:
                current_chunk += part_str
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # If a single part exceeds chunk_size, split recursively with next separator
                if len(part) > chunk_size:
                    sub_chunks = _split(part, seps[1:])
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part
                    
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return chunks

    raw_chunks = _split(text, separators)
    
    # Apply overlapping between chunks
    overlapped_chunks = []
    for i, c in enumerate(raw_chunks):
        if i == 0:
            overlapped_chunks.append(c)
        else:
            prev_chunk = raw_chunks[i - 1]
            # Take last overlap characters from previous chunk at word boundary
            overlap_text = prev_chunk[-chunk_overlap:] if len(prev_chunk) >= chunk_overlap else prev_chunk
            if " " in overlap_text:
                overlap_text = overlap_text[overlap_text.find(" ") + 1:]
            combined = f"{overlap_text} ... {c}" if overlap_text else c
            overlapped_chunks.append(combined.strip())
            
    return overlapped_chunks

def format_curriculum_chunks(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Converts structured curriculum JSON into highly optimized semantic chunks
    for each academic year and subject group.
    """
    curriculum_raw = item.get('curriculum')
    if not curriculum_raw:
        return []
        
    try:
        if isinstance(curriculum_raw, str):
            curr_data = json.loads(curriculum_raw)
        else:
            curr_data = curriculum_raw
    except Exception:
        return []
        
    chunks = []
    major_title = item.get('title', 'Chuyên ngành')
    
    for group_idx, grp in enumerate(curr_data):
        year = grp.get('year', 'Toàn khóa')
        group_name = grp.get('group', 'Khối kiến thức')
        subjects = grp.get('subjects', [])
        
        subject_list_str = ", ".join(subjects)
        
        chunk_text = (
            f"Chương trình đào tạo ngành: {major_title}\n"
            f"Giai đoạn: {year}\n"
            f"Nhóm môn: {group_name}\n"
            f"Danh sách môn học ({len(subjects)} môn): {subject_list_str}."
        )
        
        chunks.append({
            'chunk_text': chunk_text,
            'sub_section': f"{year} - {group_name}",
            'subject_count': len(subjects)
        })
        
    return chunks

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
CHUNKS_DIR = PROJECT_ROOT / 'data' / 'chunks'

def build_chunking_pipeline():
    print("======================================================================")
    print("KHỞI CHẠY PIPELINE CHUNKING & GẮN METADATA CHO HỆ THỐNG RAG")
    print("======================================================================")
    
    input_file = PROCESSED_DIR / 'crawl_v2_cleaned.json'
    if not input_file.exists():
        input_file = Path('crawl_v2_cleaned.json')
        
    print(f"[*] Nạp thành công dữ liệu từ {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"[*] Nạp thành công {len(data)} tài liệu sạch từ {input_file}")
    
    all_chunks = []
    
    for doc in data:
        doc_id = doc.get('id', 'unknown')
        title = doc.get('title', '')
        category = doc.get('category', 'chung')
        content_type = doc.get('content_type', 'page')
        department = doc.get('department') or 'Trường Đại học Thăng Long'
        date_val = doc.get('date') or ''
        source_url = doc.get('source_url', '')
        tags = doc.get('tags', [])
        content = doc.get('content', '')
        
        doc_chunks_text = []
        
        # 1. Nếu là ngành đào tạo có trường curriculum cấu trúc
        if content_type == 'major' and doc.get('curriculum'):
            # Chunk mô tả chung ngành
            if content.strip():
                main_desc_chunks = recursive_text_splitter(
                    f"Giới thiệu ngành {title}:\n{content}",
                    chunk_size=700, chunk_overlap=120
                )
                for c in main_desc_chunks:
                    doc_chunks_text.append({'text': c, 'section': 'Giới thiệu ngành'})
            
            # Chunk các khối môn học trong chương trình đào tạo
            curr_chunks = format_curriculum_chunks(doc)
            for cc in curr_chunks:
                doc_chunks_text.append({'text': cc['chunk_text'], 'section': cc['sub_section']})
                
        # 2. Các văn bản thông thường (announcement, unit, page)
        else:
            if content.strip():
                # Bổ sung tiêu đề vào đầu văn bản để giữ ngữ cảnh (Contextual Enrichment)
                enriched_text = f"Tiêu đề: {title}\nĐơn vị: {department}\n{content}"
                raw_splits = recursive_text_splitter(enriched_text, chunk_size=650, chunk_overlap=120)
                for idx, split_text in enumerate(raw_splits):
                    doc_chunks_text.append({
                        'text': split_text,
                        'section': f"Đoạn {idx + 1}/{len(raw_splits)}" if len(raw_splits) > 1 else "Toàn văn"
                    })
                    
        # Đóng gói Metadata chuẩn cho từng chunk
        total_doc_chunks = len(doc_chunks_text)
        for c_idx, c_info in enumerate(doc_chunks_text):
            chunk_id = f"{doc_id}_c{c_idx+1:03d}"
            text = c_info['text']
            
            chunk_record = {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "chunk_index": c_idx + 1,
                "total_chunks_in_doc": total_doc_chunks,
                "section": c_info['section'],
                "title": title,
                "category": category,
                "content_type": content_type,
                "department": department,
                "date": date_val,
                "source_url": source_url,
                "tags": tags,
                "char_length": len(text),
                "word_count": len(text.split()),
                "text": text
            }
            all_chunks.append(chunk_record)

    print(f"\n[+] Tổng số chunk tạo thành: {len(all_chunks)} chunks từ {len(data)} tài liệu")
    
    # Thống kê phân bố độ dài
    df_chunks = pd.DataFrame(all_chunks)
    print("\n--- Thống kê độ dài Chunk (ký tự) ---")
    print(df_chunks['char_length'].describe().round(1))
    
    print("\n--- Phân bố số lượng chunk theo category ---")
    print(df_chunks['category'].value_counts())
    
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Xuất ra file JSON chuẩn
    output_json = CHUNKS_DIR / 'clean_chunks.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Đã lưu toàn bộ chunks vào file: {output_json}")
    
    # Xuất thêm bản CSV để dễ xem bảng trên Excel (dùng utf-8-sig có BOM để Excel không lỗi font)
    try:
        output_csv = CHUNKS_DIR / 'clean_chunks.csv'
        df_chunks.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"[+] Đã lưu bản tra cứu bảng vào file (UTF-8-SIG): {output_csv}")
    except PermissionError:
        print(f"[!] File clean_chunks.csv đang được mở trong Excel. Vui lòng đóng Excel để ghi đè.")
        
    # Xuất thêm bản Excel (.xlsx) chuẩn Unicode 100% không bao giờ lỗi font
    try:
        output_xlsx = CHUNKS_DIR / 'clean_chunks.xlsx'
        df_chunks.to_excel(output_xlsx, index=False)
        print(f"[+] Đã lưu bản Excel chuẩn Unicode: {output_xlsx}")
    except Exception as e:
        pass
    
    print("\n--- Mẫu 3 Chunks hoàn chỉnh với Metadata ---")
    for s in all_chunks[:3]:
        print(f"\nID: {s['chunk_id']} | Phân mục: {s['section']} | Độ dài: {s['char_length']} ký tự")
        print(f"Metadata: [Danh mục: {s['category']}, Khoa/Phòng: {s['department']}, Ngày: {s['date']}]")
        print(f"Trích dẫn văn bản: {repr(s['text'][:140])}...")

if __name__ == '__main__':
    build_chunking_pipeline()
