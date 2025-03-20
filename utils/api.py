import requests
import os
from typing import Dict, List, Optional, Any

class TMDBApi:
    """TMDB API封装类"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self, api_key: str):
        """
        初始化TMDB API客户端
        
        参数:
            api_key: TMDB API密钥
        """
        self.api_key = api_key
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        发送API请求
        
        参数:
            endpoint: API终端路径
            params: 查询参数
            
        返回:
            解析后的JSON响应
        """
        if params is None:
            params = {}
        
        params["api_key"] = self.api_key
        params["language"] = "zh-CN"  # 使用中文返回结果
        
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def search_movies(self, query: str, page: int = 1) -> Dict:
        """
        搜索电影
        
        参数:
            query: 搜索关键词
            page: 页码
            
        返回:
            搜索结果
        """
        endpoint = "/search/movie"
        params = {
            "query": query,
            "page": page
        }
        return self._make_request(endpoint, params)
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """
        获取电影详情
        
        参数:
            movie_id: 电影ID
            
        返回:
            电影详细信息
        """
        endpoint = f"/movie/{movie_id}"
        params = {
            "append_to_response": "credits,videos,images"
        }
        return self._make_request(endpoint, params)
    
    def get_recommended_movies(self, movie_id: int, page: int = 1) -> Dict:
        """
        获取相似电影推荐
        
        参数:
            movie_id: 电影ID
            page: 页码
            
        返回:
            相似电影列表
        """
        endpoint = f"/movie/{movie_id}/recommendations"
        params = {
            "page": page
        }
        return self._make_request(endpoint, params)
    
    def get_trending_movies(self, time_window: str = "week") -> Dict:
        """
        获取热门电影
        
        参数:
            time_window: 时间窗口, 'day'或'week'
            
        返回:
            热门电影列表
        """
        valid_time_windows = ["day", "week"]
        if time_window not in valid_time_windows:
            time_window = "week"
            
        endpoint = f"/trending/movie/{time_window}"
        return self._make_request(endpoint)
    
    def discover_movies(self, 
                        genres: Optional[List[int]] = None,
                        year: Optional[int] = None,
                        sort_by: str = "popularity.desc",
                        page: int = 1) -> Dict:
        """
        发现电影
        
        参数:
            genres: 类型ID列表
            year: 年份
            sort_by: 排序方式
            page: 页码
            
        返回:
            电影列表
        """
        endpoint = "/discover/movie"
        params = {
            "sort_by": sort_by,
            "page": page
        }
        
        if genres:
            params["with_genres"] = ",".join(map(str, genres))
        
        if year:
            params["primary_release_year"] = year
            
        return self._make_request(endpoint, params)
    
    def get_movie_genres(self) -> Dict:
        """
        获取电影类型列表
        
        返回:
            电影类型列表
        """
        endpoint = "/genre/movie/list"
        return self._make_request(endpoint)
    
    def get_image_url(self, path: str) -> str:
        """
        获取完整的图片URL
        
        参数:
            path: 图片路径
            
        返回:
            完整的图片URL
        """
        if not path:
            return ""
        return f"{self.IMAGE_BASE_URL}{path}"

# 使用示例
if __name__ == "__main__":
    api_key = os.environ.get("TMDB_API_KEY", "your_api_key_here")
    tmdb = TMDBApi(api_key)
    
    # 搜索电影
    movies = tmdb.search_movies("复仇者联盟")
    print(f"找到 {movies['total_results']} 个结果")
    
    # 打印第一个结果
    if movies['results']:
        first_movie = movies['results'][0]
        print(f"电影: {first_movie['title']}, 评分: {first_movie['vote_average']}")
        
        # 获取电影详情
        movie_id = first_movie['id']
        details = tmdb.get_movie_details(movie_id)
        print(f"片长: {details.get('runtime')} 分钟")
        print(f"简介: {details.get('overview')}")
        
        # 获取推荐电影
        recommendations = tmdb.get_recommended_movies(movie_id)
        if recommendations['results']:
            print("推荐电影:")
            for movie in recommendations['results'][:3]:
                print(f" - {movie['title']}")