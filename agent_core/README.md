# 概述
提供AI Agent的原子能力。

1、构建一个ReAct Agent
（1）定义一个ReAct Agent类，包含以下属性和方法：
    属性：
        1）name：代理的名称
        2）tools：代理可以使用的工具列表
        3）model：代理使用的模型
    方法：
        1）act：代理执行一个动作，根据输入和工具列表，返回一个动作结果
    提示词模板：
        1）act_prompt_template：代理执行动作的提示词模板，包含输入、工具列表和动作结果的占位符
        2）act_prompt：根据输入和工具列表，格式化act_prompt_template，返回一个完整的提示词

2、构建一个智能问数的Agent
（1）基于pandasai库，定义一个智能问数的Agent类，包含以下属性和方法：
    属性：
        1）name：代理的名称
        2）model：代理使用的模型
    方法：
        1）ask：代理根据输入的问题，返回一个回答
    提示词模板：
        1）ask_prompt_template：代理回答问题的提示词模板，包含问题和回答的占位符
        2）ask_prompt：根据问题，格式化ask_prompt_template，返回一个完整的提示词


Memory记忆模块
支持vectorstores向量库、也可提供简单的滑动窗口获取历史记录
封装一个Memory类，包含以下属性和方法：
    属性：
        1）name：记忆模块的名称
        2）memory：记忆模块的记忆列表
    方法：
        1）add：添加一条记忆到记忆列表
        2）get：根据索引获取记忆列表中的一条记忆
        3）clear：清空记忆列表

