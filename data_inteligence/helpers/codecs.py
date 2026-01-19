import os


def is_chinese_char(uchar):
    """判断一个unicode是否是汉字"""
    return '\u4e00' <= uchar <= '\u9fa5'

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    return '\u0041' <= uchar <= '\u005a' or '\u0061' <= uchar <= '\u007a'

def is_all_chinese(text):
    """判断字符串是否全部为中文字符"""
    if not text:
        return False
    
    for char in text:
        if not is_chinese_char(char):
            return False
    
    return True

def check_filename_contain_zh(filepath):
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    for c in str(file_name):
        if is_chinese_char(c):
            return True

    return False