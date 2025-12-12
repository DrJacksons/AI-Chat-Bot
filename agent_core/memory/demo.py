from mem0 import MemoryClient

client = MemoryClient(api_key="sk-asdfahga")

# memory添加
messages = [
    {"role": "user", "content": "我是素食者，对坚果过敏。"},
    {"role": "assistant", "content": "明白了！我会记住你的饮食偏好。"}
]
client.add(messages, user_id="user_123")

# memory查询
results = client.search("What are my dietary restrictions?", filters={"user_id": "user_123"})
print(results)


# 输出
"""
{
  "results": [
    {
      "id": "14e1b28a-2014-40ad-ac42-69c9ef42193d",
      "memory": "Allergic to nuts",
      "user_id": "user123",
      "categories": ["health"],
      "created_at": "2025-10-22T04:40:22.864647-07:00",
      "score": 0.30
    }
  ]
}
"""



# ======================demo========================
import os

from mem0 import Memory

memory = Memory(api_key=os.environ["MEM0_API_KEY"])

# Sticky note: conversation memory
memory.add(
    ["I'm Alex and I prefer boutique hotels."],
    user_id="alex",
    session_id="trip-planning-2025",
)  # session memory主要适用于多Agent场景，每个Agent有自己的session_id

# Later in the session, pull long-term + session context
results = memory.search(
    "Any hotel preferences?",
    user_id="alex",
    session_id="trip-planning-2025",
)