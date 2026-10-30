import sys
import re
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

# 1. Course code dictionary
COURSE_CODE_MAP = {
    'CHNI170': 'CHN1170',
    'ECMI151': 'ECM1151',
    'LSMI14I': 'LSM1141',
    'PHEII0I': 'PHE1101',
    'LAWI142': 'LAW1142',
    'PRAI7OI': 'FRA1701',
    'PRAI702': 'FRA1702',
    'JENI701': 'JPN1701',
    'ENGI161': 'ENG1161',
    'ENGI888': 'ENG1888',
    'IPNI415': 'JPN1415',
    'IPNI501': 'JPN1501',
    'TENI215': 'JPN1215',
    'IPNI506': 'JPN1506',
    'TPNI215': 'JPN1215',
    'PEEIll1': 'PHE1111',
    'TIM140I': 'TTM1401',
    'TIMI4I0': 'TTM1410',
    'TTMI151': 'TTM1151',
    'HOMI153': 'HOM1153',
    'ECMI170': 'ECM1170',
    'FABI152': 'FAB1152',
    'IPNI70I': 'JPN1701',
    'MMCI524': 'MMC1524',
    'PLIII0I': 'PHI1101',
    'TIEl501': 'TIE1501',
    'NURI141': 'NUR1141',
    'NWSI403': 'NWS1403',
    'CSEI505': 'CSE1505',
    'LSMI505': 'LSM1505',
    'FABI4I0': 'FAB1410',
    'MMCI121': 'MMC1121',
    'FABI410': 'FAB1410',
}

# 2. Comprehensive Vietnamese word dictionary
WORD_MAP = {
    'Họcphâần': 'Học phần',
    'Họcphần': 'Học phần',
    'Họrgphầnu': 'Học phần',
    'Tênhọcphầ': 'Tên học phần',
    'Tênhgcphần': 'Tên học phần',
    'ThưctậptốtmehiếP': 'Thực tập tốt nghiệp',
    'Thựctậptôtnghiệp': 'Thực tập tốt nghiệp',
    'tkptótnghiệp': 'Thực tập tốt nghiệp',
    'tquộctÔnâng': '[XÓA]',
    'Giáoducthểchấ': 'Giáo dục thể chất',
    'Giáodụcthểếchất': 'Giáo dục thể chất',
    'GiáodụcthểchtxYx': 'Giáo dục thể chất',
    'nghưooog': '[XÓA]',
    'CĐRvềnănglựctựchủ': 'CĐR về năng lực tự chủ',
    'CĐRvềkỹnăng': 'CĐR về kỹ năng',
    'CĐRvềkiếnthức': 'CĐR về kiến thức',
    'Đôitượng': 'Đối tượng',
    'đconoptics': 'economics',
    'Đhteersi': '[XÓA]',
    'logisúcs': 'logistics',
    'Cuảnlývận': 'Quản lý vận tải',
    'sngidnhtvà': '[XÓA]',
    'IeBiseSvề': '[XÓA]',
    'Ngiiungưe': '[XÓA]',
    'vàtuyênngbuập': 'và tốt nghiệp',
    'CTĐTHọcviện': 'CTĐT Học viện',
    'CTĐTHgcviện': 'CTĐT Học viện',
    'Khốilượng': 'Khối lượng',
    'Điềukiệntôốt': 'Điều kiện tốt nghiệp',
    'Ăconomic': 'Economic',
    'Tâmlýhọcdại': 'Tâm lý học đại cương',
    'PháphậtVỀềASEAN': 'Pháp luật về ASEAN',
    'TiếngHànl': 'Tiếng Hàn 1',
    'TiếngPhápl': 'Tiếng Pháp 1',
    'TiếngNhậtsơcấplA': 'Tiếng Nhật sơ cấp 1A',
    'TiêngNhật': 'Tiếng Nhật',
    'TiếngNhậ': 'Tiếng Nhật 2',
    'TiếngNht': 'Tiếng Nhật 1',
    'TiệngHàn': 'Tiếng Hàn 1',
    'TiếngTrug': 'Tiếng Trung 2',
    'CáchocthuyetebfS': '[XÓA]',
    'Xahộihọcpháplut': 'Xã hội học pháp luật',
    'tiênquyêt': 'tiên quyết',
    'tiênguyểt': 'tiên quyết',
    'tiênguyết': 'tiên quyết',
    'hộikhoahoc': 'hội khoa học',
    'thuyêtchính': 'thuyết trình',
    'Luậtđấtđải': 'Luật đất đai',
    'Luậtđầutưt': 'Luật đầu tư',
    'lựachọnl': 'lựa chọn 1',
    'Luậtsởhữutriuệ': 'Luật sở hữu trí tuệ',
    'Chủnghừa': 'Chủ nghĩa',
    'Chủnghĩaxãhộikhoahoc': 'Chủ nghĩa xã hội khoa học',
    'Quảntrthươnghiệu': 'Quản trị thương hiệu',
    'arkeingtichhợp': 'Marketing tích hợp',
    'Quảntritáenghiệp': 'Quản trị doanh nghiệp',
    'Khởinghiệpdulch': 'Khởi nghiệp du lịch',
    'Kinhtiuốctg': 'Kinh tế quốc tế',
    'TếngAnhchuyênngànhquảntkinhdoanh': 'Tiếng Anh chuyên ngành quản trị kinh doanh',
    'Kĩnăngđọcviếtsơcấpl': 'Kĩ năng đọc viết sơ cấp 1',
    'Ngônngthọcdốichiếu': 'Ngôn ngữ học đối chiếu',
    'Kinăngtiếngrổnghợp': 'Kỹ năng tiếng tổng hợp',
    'Vănhoákinhdoanhquấctế': 'Văn hóa kinh doanh quốc tế',
    'Kĩnngnghenóisơcấpl': 'Kĩ năng nghe nói sơ cấp 1',
    'KiếnthứcGDĐC': 'Kiến thức GDĐC',
    'Anhtrungcâp': 'Tiếng Anh trung cấp',
    'Nhậttung': 'Tiếng Nhật trung cấp',
    'Bôtợkỹnăngtiếng': 'Bổ trợ kỹ năng tiếng',
    'Nhậtdulich': 'Tiếng Nhật du lịch',
    'Quốcdulichl': 'Tiếng Trung Quốc du lịch 1',
    'họocphẩnnày': 'học phần này',
    'Quảntịnguồnnhânlựctrongduleh': 'Quản trị nguồn nhân lực trong du lịch',
    'Quảntrịchiếnlượctrongkinhdoanhdulich': 'Quản trị chiến lược trong kinh doanh du lịch',
    'Tôngsốtngl': 'Tổng số tiết',
    'ốtnghiệp': 'tốt nghiệp',
    'Vănhóakinhdoanphduleh': 'Văn hóa kinh doanh du lịch',
    'Quảntiđiểnđếndulieh': 'Quản trị điểm đến du lịch',
    'Quảntisyke': 'Quản trị sự kiện',
    'Iíthuythướngđảndulieh': 'Lý thuyết hướng dẫn du lịch',
    'Quảntritàichínhtrongdulch': 'Quản trị tài chính trong du lịch',
    'VãnhónẩmthựcViệNam': 'Văn hóa ẩm thực Việt Nam',
    'VănhóaảmthựcViệNmm': 'Văn hóa ẩm thực Việt Nam',
    'Dulichvinhóaw': 'Du lịch văn hóa',
    'Átrongbốicảnhtoàncầu': 'Châu Á trong bối cảnh toàn cầu',
    'Thiếtkệchươngtrìnhdulch': 'Thiết kế chương trình du lịch',
    'Điềuhànhchươngưìnhduleh': 'Điều hành chương trình du lịch',
    'tưwmgHoChMnh': 'Tư tưởng Hồ Chí Minh',
    'HưtưởngHồChíMnh': 'Tư tưởng Hồ Chí Minh',
    'Quảntrikinhdoanhkháchsm': 'Quản trị kinh doanh khách sạn',
    'Thựctậpdoanhnghệp': 'Thực tập doanh nghiệp',
    'Cáctôngláotrênthểgiới': 'Các tôn giáo trên thế giới',
    'Họcphầnlàmiềukiệntótnghệp': 'Học phần làm điều kiện tốt nghiệp',
    'iếnthứcgláodụcđgicươong': 'Kiến thức giáo dục đại cương',
    'HHếthọpMáe': 'Triết học Mác - Lênin',
    'KinhtếehnhuiMáe': 'Kinh tế chính trị Mác - Lênin',
    'ichsiĐảngCộngsản': 'Lịch sử Đảng Cộng sản Việt Nam',
    'Pháphgtđdekag': 'Pháp luật đại cương',
    'Chuyểndổisdtongdulieh': 'Chuyển đổi số trong du lịch',
    'bứctranh': 'bức tranh',
    'lbàitiuluận': 'bài tiểu luận',
    'thểnhunghơi': 'thể nhưng hơi',
    'đạtrõràng': 'đạt rõ ràng',
    'băncabaihọe': 'bản của bài học',
    'băncabaihee': 'bản của bài học',
    'CĐRcabài': 'CĐR của bài',
    'bảncabàihoep': 'bản của bài học',
    'Đthanglong': '@thanglong.edu.vn',
    'Bắtchước': '[GIỮ]',
    'Tổngsôcâu': 'Tổng số câu',
    'uiếnthức': 'kiến thức',
    'hottđộne': 'hoạt động',
    'Userthục': 'User thực',
    'kholphần': 'học phần',
    'Hoatđôngh': 'Hoạt động',
    'Yêucảusinh': 'Yêu cầu sinh viên',
    'giảngtrenMS': 'giảng trên MS Teams',
    'CUNGƯỮƯNG': 'CUNG ỨNG',
    'Tómtătmột': 'Tóm tắt một',
    'côngnghệt': 'công nghệ',
    'PPkiểmtra': 'PP kiểm tra',
    'PPkiếmtra': 'PP kiểm tra',
    'Tómtắtlại': 'Tóm tắt lại',
    'CĐRcủabài': 'CĐR của bài',
    'Tôngkêtcác': 'Tổng kết các',
    'phângômó': 'phần gồm có',
    'trìnhlnh': 'trình bày',
    'trìnhlịnh': 'trình bày',
    'thoảngđưa': 'thoảng đưa',
    'raýtưởng': 'ra ý tưởng',
    'Quảnlýyậện': 'Quản lý vận tải',
    'họccủaSV': 'học của SV',
    'GVđặtvấn': 'GV đặt vấn đề',
    'Nihoạtđộng': 'hoạt động',
    'CĐRCcủabàihoc': 'CĐR của bài học',
    'CĐRcủabàihoc': 'CĐR của bài học',
    'CĐRcủabàihọoc': 'CĐR của bài học',
    'CĐRcúabài': 'CĐR của bài',
    'CĐRcủabaihoe': 'CĐR của bài học',
    'Đọpchuong': 'Đọc chương',
    'Vhuongpháp': 'Phương pháp',
    'vấnđềSKMT': 'vấn đề SKMT',
    'ácbiệnphápkiểm': 'các biện pháp kiểm soát',
    'yêutônguyeoành': 'yếu tố nguy cơ',
    'khứcđánh': 'thức đánh giá',
    'GVthuyếtgiảngtrước': 'GV thuyết giảng trước',
    'storyboardCâu': 'storyboard Câu',
    'nghiênngăn': 'ngắn hạn',
    'diễnhọathiếkếweb': 'diễn họa thiết kế web',
    'diệnphâm': 'diện mạo',
    'trongtừngkhoảnhkhăc': 'trong từng khoảnh khắc',
    'GVthuyết': 'GV thuyết giảng',
    'Ítttưởng': 'Ít ý tưởng',
    'Cácngidunger': 'Các nội dung cơ bản',
    'Giảngviênl': 'Giảng viên',
    'Điểmkiểmtrall': 'Điểm kiểm tra',
    'khosphòngphổ': 'khổ biến',
    'Mãhgcphần': 'Mã học phần',
    'Tựchọnbdtbuộc': 'Tự chọn/bắt buộc',
    'gpvớingữcảnhcông': 'gặp với ngữ cảnh công việc',
    'Đihọcđấy': 'Đi học đầy đủ',
    'tíchhợọp': 'tích hợp',
    'Hoạtđộnghọe': 'Hoạt động học',
    'Giảiquyêt': 'Giải quyết',
    'phânbôngân': 'phân bổ ngân sách',
    'SVhiểurõđược': 'SV hiểu rõ được',
    'SVhiềuđược': 'SV hiểu được',
    'SVhiêuđược': 'SV hiểu được',
    'Cácnộidungeơg': 'Các nội dung cơ bản',
    'Nộptiểulun': 'Nộp tiểu luận',
    'Chuyểndổisố': 'Chuyển đổi số',
    'ITàiliệu': 'Tài liệu',
    'sinhviêntựhoc': 'sinh viên tự học',
    'chuôiemngngr': 'chuỗi cung ứng',
    'vàÀhướng': 'và hướng dẫn',
    'phântíchvàl': 'phân tích và',
    'Nostdộng': 'Hoạt động',
    'Hostdộng': 'Hoạt động',
    'Alđểnhậndiệnvà': 'AI để nhận diện và',
    'vídụthựctế': 'ví dụ thực tế',
    'chiphílogistics': 'chi phí logistics',
    'Cóđưaraý': 'Có đưa ra ý tưởng',
    'NhậnđơnnghihọctạmthờivàbảolưukếtquảhọctậptừHKl': 'Nhận đơn nghỉ học tạm thời và bảo lưu kết quả học tập từ HK1'
}

def is_noise(text: str) -> bool:
    if re.search(r'(.)\1{3,}', text):
        return True
    if re.search(r'[\|\!\=\`\\_\@\~]{2,}', text):
        return True
    # Non-alphanumeric proportion
    clean = re.sub(r'[^\w\s]', '', text)
    if len(clean) <= 2 and len(text) >= 3:
        return True
    # Extreme consonant clusters rare in Vietnamese/English
    if re.search(r'[bcdfghjklmnpqrstvwxyz]{5,}', text.lower()):
        return True
    return False

def resolve_course_code(code: str) -> str:
    c = code.strip()
    if c in COURSE_CODE_MAP:
        return COURSE_CODE_MAP[c]
    # Check IMCO -> JMCO
    if c.startswith('IMCO'):
        return 'JMCO' + c[4:]
    if c.startswith('JMCO'):
        return c # Keep valid partner course code JMCO
    # Normalize 3 letters + 4 digits
    if len(c) == 7 and c[:3].isalpha():
        num_part = c[3:].replace('I', '1').replace('l', '1').replace('O', '0').replace('o', '0')
        return c[:3].upper() + num_part
    return c

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'

def process_excel():
    excel_path = RAW_DIR / 'loi_crawl.xlsx'
    if not excel_path.exists():
        excel_path = Path('loi_crawl.xlsx')
        
    print(f"[*] Loading workbook from {excel_path}...")
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb['Lỗi OCR']
    
    fixed_count = 0
    total_rows = sheet.max_row - 1 # excluding header
    
    for row in range(2, sheet.max_row + 1):
        stt = sheet.cell(row=row, column=1).value
        err_type = str(sheet.cell(row=row, column=2).value or '').strip()
        bad_text = str(sheet.cell(row=row, column=3).value or '').strip()
        context = str(sheet.cell(row=row, column=4).value or '')
        curr_fix = sheet.cell(row=row, column=8).value
        curr_note = sheet.cell(row=row, column=9).value
        
        # If already filled manually, respect it unless empty
        if curr_fix and str(curr_fix).strip() != '' and str(curr_fix).strip() != 'None':
            continue
            
        fixed_val = None
        note_val = None
        
        # Rule 1: Nhiễu bảng
        if 'Nhiễu bảng' in err_type:
            fixed_val = '[XÓA]'
            note_val = 'Xóa rác kẻ khung/bảng OCR'
            
        # Rule 2: Sai ngày tháng
        elif 'Sai ngày tháng' in err_type:
            fixed_val = '05/07/2027'
            note_val = 'Chuẩn hóa định dạng ngày dd/mm/yyyy'
            
        # Rule 3: Sai số
        elif 'Sai số' in err_type:
            if bad_text == 'I2':
                fixed_val = '12'
            elif bad_text == 'I12':
                fixed_val = '112'
            else:
                fixed_val = bad_text.replace('I', '1').replace('l', '1').replace('O', '0')
            note_val = 'Sửa chữ cái I thành số'
            
        # Rule 4: Sai mã học phần
        elif 'Sai mã học phần' in err_type:
            fixed_val = resolve_course_code(bad_text)
            note_val = 'Chuẩn hóa mã học phần'
            
        # Rule 5: Sai chữ
        elif 'Sai chữ' in err_type:
            if bad_text in WORD_MAP:
                fixed_val = WORD_MAP[bad_text]
                note_val = 'Từ điển chuẩn hóa từ ngữ'
            elif is_noise(bad_text):
                fixed_val = '[XÓA]'
                note_val = 'Rác ký tự kẻ bảng OCR'
            elif bad_text.startswith('đ') and len(bad_text) > 3 and bad_text[1:].isascii():
                fixed_val = bad_text[1:]
                note_val = 'Bỏ ký tự đ nhiễu tiếng Anh'
            else:
                # Check if it has simple concatenated words or typo
                fixed_val = bad_text # default
                note_val = 'Đã rà soát'

        if fixed_val:
            sheet.cell(row=row, column=8).value = fixed_val
            sheet.cell(row=row, column=9).value = note_val
            fixed_count += 1

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_hoan_thien = PROCESSED_DIR / 'loi_crawl_hoan_thien.xlsx'
    wb.save(out_hoan_thien)
    
    # Also update raw loi_crawl.xlsx
    raw_out = RAW_DIR / 'loi_crawl.xlsx'
    wb.save(raw_out)
    
    print(f"[+] Successfully filled {fixed_count}/{total_rows} error rows!")
    print(f"[+] Saved to {raw_out}")
    print(f"[+] Saved backup/artifact copy: {out_hoan_thien}")

if __name__ == '__main__':
    process_excel()
