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

