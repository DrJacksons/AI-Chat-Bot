"""
Constants used in the data inteligence package.
"""
from pathlib import Path

# 默认存储路径
DEFAULT_STORGE_PATH = Path("stores")

# 如果用户未提供任何图表，则存储图表的默认目录
DEFAULT_CHART_DIRECTORY = DEFAULT_STORGE_PATH / "charts"

# 文件和目录的默认权限
DEFAULT_FILE_PERMISSIONS = 0o755

LOCAL_SOURCE_TYPES = ["csv", "parquet", "xlsx", "xls"]
REMOTE_SOURCE_TYPES = [
    "mysql",
    "postgres",
    "sqlserver",
    "oracle",
]
SQL_SOURCE_TYPES = ["mysql", "postgres", "sqlserver", "oracle"]
VALID_COLUMN_TYPES = ["string", "integer", "float", "datetime", "boolean"]

VALID_TRANSFORMATION_TYPES = [
    "anonymize",           # 匿名
    "convert_timezone",    # 转换时区
    "to_lowercase",        # 转换为小写
    "to_uppercase",        # 转换为大写
    "strip",               # 移除首尾空格
    "round_numbers",       # 四舍五入到指定小数位数
    "scale",               # 缩放数值到指定范围
    "format_date",         # 格式化日期
    "to_numeric",          # 转换为数值
    "to_datetime",         # 转换为日期时间
    "fill_na",             # 填充缺失值
    "replace",             # 替换值
    "extract",             # 提取子字符串
    "truncate",            # 截断字符串
    "pad",                 # 填充字符串
    "clip",                # 截断数值
    "bin",                 # 分箱数值
    "normalize",           # 归一化数值
    "standardize",         # 标准化数值
    "map_values",          # 映射值
    "rename",              # 重命名列
    "encode_categorical",  # 编码分类变量
    "validate_email",      # 验证电子邮件地址
    "validate_date_range", # 验证日期范围
    "normalize_phone",     # 标准化电话号码
    "remove_duplicates",   # 移除重复行
    "validate_foreign_key", # 验证外键关系
    "ensure_positive",      # 确保数值为正值
    "standardize_categories", # 标准化分类变量
]
