import requests

# 使用你的访问令牌
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhMzU3NzQ5MmI1NDBhMDc5YTY1ZjE4YjVmYTg3ODQ1ZSIsIm5iZiI6MTc0MjQ2NTU1NS4xMzIsInN1YiI6IjY3ZGJlYTEzOGFmNDUyZjMwZmU5ZTdiOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.8iR--zbrl40PbWaRHj4iBYpY3w95-P4qWxvch890gSo"
BASE_URL = "https://api.themoviedb.org/3"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

# 测试电影类型列表端点
url = f"{BASE_URL}/genre/movie/list?language=zh-CN"
response = requests.get(url, headers=headers)

print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")