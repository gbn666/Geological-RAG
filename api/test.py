import requests

# 1. 登录取 Token
LOGIN_URL = "http://172.20.83.93:5000/api/auth/login"
LOGIN_DATA = {
    "email": "1017760136@qq.com",
    "password": "123"
}
login_resp = requests.post(LOGIN_URL, json=LOGIN_DATA)
login_resp.raise_for_status()
token = login_resp.json()["access_token"]
print("Token:", token)

# 2. 创建 Session
SESSION_URL = "http://172.20.83.93:5000/api/session/new"
headers = {"Authorization": f"Bearer {token}"}
session_resp = requests.post(SESSION_URL, headers=headers)
session_resp.raise_for_status()
session_id = session_resp.json()["session_id"]
print("Session ID:", session_id)

# 3. 测试带 image_url 的 chat 调用
CHAT_URL = f"http://172.20.83.93:5000/api/session/{session_id}/chat"

# 这里填上你上传后实际能访问到的路径（相对于 UPLOAD_URL_PATH）
# 例如你的图片落盘在 F:/pycharm/RAG/api/uploads/a2fb1678307e46efa30a4edf34404b48.jpg
# 且 UPLOAD_URL_PATH 设置为 "/api/uploads"
payload = {
    "question": "这是什么矿石吗？",
    "image_url": "/api/uploads/a2fb1678307e46efa30a4edf34404b48.jpg"
}

chat_resp = requests.post(
    CHAT_URL,
    headers={**headers, "Content-Type": "application/json"},
    json=payload
)

print("Chat Status:", chat_resp.status_code)
print("Response JSON:", chat_resp.json())
