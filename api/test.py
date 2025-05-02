import requests

# 1. 登录接口，获取 Token
LOGIN_URL = "http://172.20.97.54:5000/api/auth/login"
LOGIN_DATA = {
    "email": "1017760136@qq.com",
    "password": "123"
}

login_resp = requests.post(LOGIN_URL, json=LOGIN_DATA)
if login_resp.status_code != 200:
    print("Login failed:", login_resp.text)
    exit(1)

token = login_resp.json().get("access_token")
print("Token:", token)

# 2. 创建 Session
SESSION_URL = "http://172.20.97.54:5000/api/session/new"
headers = {"Authorization": f"Bearer {token}"}

session_resp = requests.post(SESSION_URL, headers=headers)
print("Session create status code:", session_resp.status_code)
print("Session create body:", session_resp.text)

# 接受 200 和 201 都算成功
if session_resp.status_code not in (200, 201):
    print("Session creation failed:", session_resp.text)
    exit(1)

session_id = session_resp.json().get("session_id")
print("Session ID:", session_id)

# 3. 向 chat 接口发送问题
CHAT_URL = f"http://172.20.97.54:5000/api/session/{session_id}/chat"
question_data = {
    "question": "这是含有石英的矿石吗？"
}
chat_resp = requests.post(
    CHAT_URL,
    headers={**headers, "Content-Type": "application/json"},
    json=question_data
)

# 4. 打印结果
print("Chat Status:", chat_resp.status_code)
try:
    print("Response:", chat_resp.json())
except Exception:
    print("Raw Response:", chat_resp.text)
