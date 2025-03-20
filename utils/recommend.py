import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import json
import os
from utils.api import TMDBApi

class MovieRecommender:
    """电影推荐引擎"""
    
    # 情绪映射到电影类型
    MOOD_TO_GENRES = {
        "开心": [35, 16, 10751],  # 喜剧、动画、家庭
        "伤感": [18, 10749],  # 剧情、爱情
        "放松": [12, 14, 878],  # 冒险、奇幻、科幻
        "兴奋": [28, 53, 80],  # 动作、惊悚、犯罪
        "害怕": [27, 9648],  # 恐怖、悬疑
        "无聊": [99, 36]  # 纪录片、历史
    }
    
    # 时长映射
    DURATION_RANGES = {
        "短片": (0, 60),
        "标准": (60, 120),
        "长片": (120, 180),
        "超长": (180, 10000)
    }
    
    def __init__(self, api: TMDBApi, user_data_path: str = "data/user_data.json"):
        """
        初始化推荐引擎
        
        参数:
            api: TMDB API实例
            user_data_path: 用户数据文件路径
        """
        self.api = api
        self.user_data_path = user_data_path
        self.user_data = self._load_user_data()
        
        # 加载电影类型
        genres_response = self.api.get_movie_genres()
        self.genres_map = {genre['id']: genre['name'] for genre in genres_response['genres']}
    
    def _load_user_data(self) -> Dict:
        """
        加载用户数据
        
        返回:
            用户数据字典
        """
        if os.path.exists(self.user_data_path):
            try:
                with open(self.user_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"watched": [], "liked": [], "disliked": [], "preferences": {}}
        else:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.user_data_path), exist_ok=True)
            # 创建默认用户数据
            default_data = {"watched": [], "liked": [], "disliked": [], "preferences": {}}
            self._save_user_data(default_data)
            return default_data
    
    def _save_user_data(self, data: Dict = None) -> None:
        """
        保存用户数据
        
        参数:
            data: 用户数据，如果为None则保存self.user_data
        """
        if data is None:
            data = self.user_data
            
        with open(self.user_data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_watched_movie(self, movie_id: int, liked: bool = None) -> None:
        """
        添加已观看电影记录
        
        参数:
            movie_id: 电影ID
            liked: 是否喜欢，None表示未评价
        """
        if movie_id not in self.user_data["watched"]:
            self.user_data["watched"].append(movie_id)
            
        if liked is True and movie_id not in self.user_data["liked"]:
            self.user_data["liked"].append(movie_id)
            if movie_id in self.user_data["disliked"]:
                self.user_data["disliked"].remove(movie_id)
                
        elif liked is False and movie_id not in self.user_data["disliked"]:
            self.user_data["disliked"].append(movie_id)
            if movie_id in self.user_data["liked"]:
                self.user_data["liked"].remove(movie_id)
                
        # 更新用户偏好
        if liked is not None:
            self._update_preferences(movie_id, liked)
                
        self._save_user_data()
    
    def _update_preferences(self, movie_id: int, liked: bool) -> None:
        """
        更新用户偏好
        
        参数:
            movie_id: 电影ID
            liked: 是否喜欢
        """
        try:
            movie_details = self.api.get_movie_details(movie_id)
            
            # 获取电影类型ID列表
            genres = [genre['id'] for genre in movie_details.get('genres', [])]
            
            for genre_id in genres:
                genre_name = self.genres_map.get(genre_id, str(genre_id))
                
                if genre_name not in self.user_data["preferences"]:
                    self.user_data["preferences"][genre_name] = 0
                    
                # 增加或减少对该类型的偏好值
                if liked:
                    self.user_data["preferences"][genre_name] += 1
                else:
                    self.user_data["preferences"][genre_name] -= 1
        except Exception as e:
            print(f"更新用户偏好时出错: {e}")
    
    def get_recommendations_by_mood(self, 
                                    mood: str, 
                                    duration: Optional[str] = None,
                                    limit: int = 10) -> List[Dict]:
        """
        根据心情推荐电影
        
        参数:
            mood: 心情关键词
            duration: 时长范围
            limit: 返回电影数量限制
            
        返回:
            电影列表
        """
        # 获取对应心情的类型ID
        genre_ids = self.MOOD_TO_GENRES.get(mood, [])
        
        if not genre_ids:
            # 如果没有映射，返回热门电影
            trending = self.api.get_trending_movies()
            return self._filter_by_duration(trending['results'], duration)[:limit]
            
        # 尝试通过类型获取电影
        discover = self.api.discover_movies(genres=genre_ids)
        
        # 根据时长过滤并返回结果
        return self._filter_by_duration(discover['results'], duration)[:limit]
    
    def _filter_by_duration(self, movies: List[Dict], duration_key: Optional[str]) -> List[Dict]:
        """
        根据时长过滤电影
        
        参数:
            movies: 电影列表
            duration_key: 时长范围键名
            
        返回:
            过滤后的电影列表
        """
        if not duration_key or duration_key not in self.DURATION_RANGES:
            return movies
            
        min_duration, max_duration = self.DURATION_RANGES[duration_key]
        
        # 先获取详细信息，然后过滤
        filtered_movies = []
        for movie in movies:
            try:
                details = self.api.get_movie_details(movie['id'])
                runtime = details.get('runtime', 0)
                
                if min_duration <= runtime < max_duration:
                    # 合并详细信息到电影对象
                    movie.update({
                        'runtime': runtime,
                        'genres': details.get('genres', []),
                        'overview': details.get('overview', '')
                    })
                    filtered_movies.append(movie)
                    
                    # 如果已经收集足够的电影，提前结束
                    if len(filtered_movies) >= 20:
                        break
            except Exception as e:
                print(f"获取电影详情出错: {e}")
                
        return filtered_movies
    
    def get_personalized_recommendations(self, limit: int = 10) -> List[Dict]:
        """
        获取个性化推荐
        
        参数:
            limit: 返回电影数量限制
            
        返回:
            推荐电影列表
        """
        # 从用户喜欢的电影中获取推荐
        recommended_movies = []
        
        # 如果有喜欢的电影，根据它们推荐
        if self.user_data["liked"]:
            # 随机选择一部喜欢的电影
            import random
            liked_movie_id = random.choice(self.user_data["liked"])
            
            try:
                recommendations = self.api.get_recommended_movies(liked_movie_id)
                recommended_movies.extend(recommendations['results'])
            except Exception as e:
                print(f"获取推荐出错: {e}")
        
        # 如果推荐不足，根据用户偏好发现电影
        if len(recommended_movies) < limit and self.user_data["preferences"]:
            # 找出偏好最高的几个类型
            sorted_preferences = sorted(
                self.user_data["preferences"].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # 获取前两个最喜欢的类型
            favorite_genres = []
            for genre_name, score in sorted_preferences[:2]:
                if score > 0:  # 只考虑正面偏好
                    # 根据名称找到ID
                    for genre_id, name in self.genres_map.items():
                        if name == genre_name:
                            favorite_genres.append(genre_id)
                            break
            
            if favorite_genres:
                try:
                    discover = self.api.discover_movies(genres=favorite_genres)
                    recommended_movies.extend(discover['results'])
                except Exception as e:
                    print(f"发现电影出错: {e}")
        
        # 如果仍然不足，获取热门电影
        if len(recommended_movies) < limit:
            try:
                trending = self.api.get_trending_movies()
                recommended_movies.extend(trending['results'])
            except Exception as e:
                print(f"获取热门电影出错: {e}")
        
        # 去重
        unique_movies = []
        seen_ids = set()
        
        for movie in recommended_movies:
            if movie['id'] not in seen_ids and movie['id'] not in self.user_data["watched"]:
                seen_ids.add(movie['id'])
                unique_movies.append(movie)
        
        return unique_movies[:limit]
    
    def get_viewing_stats(self) -> Dict:
        """
        获取观影统计数据
        
        返回:
            统计信息字典
        """
        stats = {
            "total_watched": len(self.user_data["watched"]),
            "total_liked": len(self.user_data["liked"]),
            "total_disliked": len(self.user_data["disliked"]),
            "favorite_genres": [],
            "watched_movies": []
        }
        
        # 获取喜爱类型
        if self.user_data["preferences"]:
            sorted_preferences = sorted(
                self.user_data["preferences"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            stats["favorite_genres"] = [
                {"name": genre, "score": score} 
                for genre, score in sorted_preferences 
                if score > 0
            ][:5]  # 最多5个最喜欢的类型
        
        # 获取已观看电影详情
        for movie_id in self.user_data["watched"][-10:]:  # 最近10部
            try:
                movie = self.api.get_movie_details(movie_id)
                status = "liked" if movie_id in self.user_data["liked"] else (
                    "disliked" if movie_id in self.user_data["disliked"] else "neutral"
                )
                
                stats["watched_movies"].append({
                    "id": movie_id,
                    "title": movie.get("title", "未知电影"),
                    "poster_path": movie.get("poster_path", ""),
                    "status": status,
                    "date": movie.get("release_date", "")
                })
            except Exception as e:
                print(f"获取电影详情出错: {e}")
        
        return stats