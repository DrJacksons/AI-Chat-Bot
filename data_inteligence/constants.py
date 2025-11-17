"""
Constants used in the data inteligence package.
"""
from pathlib import Path

# 默认API url
DEFAULT_API_URL = "https://api.pandabi.ai"

# 如果用户未提供任何图表，则存储图表的默认目录
DEFAULT_CHART_DIRECTORY = Path("exports") / "charts"

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
    "anonymize",
    "convert_timezone",
    "to_lowercase",
    "to_uppercase",
    "strip",
    "round_numbers",
    "scale",
    "format_date",
    "to_numeric",
    "to_datetime",
    "fill_na",
    "replace",
    "extract",
    "truncate",
    "pad",
    "clip",
    "bin",
    "normalize",
    "standardize",
    "map_values",
    "rename",
    "encode_categorical",
    "validate_email",
    "validate_date_range",
    "normalize_phone",
    "remove_duplicates",
    "validate_foreign_key",
    "ensure_positive",
    "standardize_categories",
]
