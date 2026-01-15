# 代码目录结构
-- data_inteligence
    -- data_loader    # 数据集加载
    -- dataframe      # 自定义DataFrame类，自定义相关属性
    -- query_builders # 查询构建器，包含本地数据集和远程（数据库）数据集
    -- code_core      # 代码运行核心，包含代码执行器、代码解析器、代码生成器、提示词等


# 数据集
数据集分为两类：本地数据集和远程（数据库）数据集
其中本地数据集为表格类型的文件，支持parquet、csv格式、excel格式等
数据库数据集支持主流关系型数据库：Oracle、MySQL、PostgreSQL、SQL Server等

# Data Loader加载器
本地数据集统一使用duckdb来查询，duckdb具有对大数据量表的高性能的处理效率。

# 使用步骤
## 连接数据库创建数据集
```python3
from data_inteligence import create
sql_table = create(
    path="example/mysql-dataset",
    description="Heart disease dataset from MySQL database",
    source={
        "type": "mysql",
        "connection": {
            "host": "database.example.com",
            "port": 3306,
            "user": "${DB_USER}",
            "password": "${DB_PASSWORD}",
            "database": "medical_data"
        },
        "table": "heart_data",
        "columns": [
            {"name": "Age", "type": "integer", "description": "Age of the patient in years"},
            {"name": "Sex", "type": "string", "description": "Gender of the patient (M = male, F = female)"},
            {"name": "ChestPainType", "type": "string", "description": "Type of chest pain (ATA, NAP, ASY, TA)"},
            {"name": "RestingBP", "type": "integer", "description": "Resting blood pressure in mm Hg"},
            {"name": "Cholesterol", "type": "integer", "description": "Serum cholesterol in mg/dl"},
            {"name": "FastingBS", "type": "integer", "description": "Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)"},
            {"name": "RestingECG", "type": "string", "description": "Resting electrocardiogram results (Normal, ST, LVH)"},
            {"name": "MaxHR", "type": "integer", "description": "Maximum heart rate achieved"},
            {"name": "ExerciseAngina", "type": "string", "description": "Exercise-induced angina (Y = yes, N = no)"},
            {"name": "Oldpeak", "type": "float", "description": "ST depression induced by exercise relative to rest"},
            {"name": "ST_Slope", "type": "string", "description": "Slope of the peak exercise ST segment (Up, Flat, Down)"},
            {"name": "HeartDisease", "type": "integer", "description": "Heart disease diagnosis (1 = present, 0 = absent)"}
        ]
    }
)
```

