import streamlit as st
import os
import json
from utils.api import TMDBApi
from utils.recommend import MovieRecommender
import time

# 页面配置
st.set_page_config(
    page_title="AI观影助手",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0083B8;
        margin-bottom: 1rem;
    }
    .movie-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
    }
    .movie-info {
        font-size: 0.9rem;
        color: #888;
        margin-bottom: 0.5rem;
    }
    .movie-overview {
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .mood-button {
        margin: 0.2rem;
        padding: 0.5rem;
    }
    .movie-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    .rating {
        font-size: 1.1rem;
        font-weight: bold;
        color: #FF9529;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'tmdb_api' not in st.session_state:
    # 从环境变量或Streamlit Secrets获取API密钥
    api_key = os.environ.get("TMDB_API_KEY", st.secrets.get("TMDB_API_KEY", "在此输入您的API密钥"))
    st.session_state.tmdb_api = TMDBApi(api_key)

if 'recommender' not in st.session_state:
    st.session_state.recommender = MovieRecommender(st.session_state.tmdb_api)

if 'mood' not in st.session_state:
    st.session_state.mood = None
    
if 'duration' not in st.session_state:
    st.session_state.duration = None
    
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

if 'movie_details' not in st.session_state:
    st.session_state.movie_details = None

# 辅助函数
def set_mood(mood):
    st.session_state.mood = mood
    
def set_duration(duration):
    st.session_state.duration = duration
    
def show_movie_details(movie_id):
    try:
        details = st.session_state.tmdb_api.get_movie_details(movie_id)
        st.session_state.movie_details = details
    except Exception as e:
        st.error(f"获取电影详情时出错: {e}")
        
def mark_as_watched(movie_id, liked=None):
    st.session_state.recommender.add_watched_movie(movie_id, liked)
    # 刷新推荐
    get_recommendations()
    # 如果在详情页，关闭它
    if st.session_state.movie_details and st.session_state.movie_details.get('id') == movie_id:
        st.session_state.movie_details = None
        
def get_recommendations():
    with st.spinner("正在寻找完美影片..."):
        if st.session_state.mood:
            st.session_state.recommendations = st.session_state.recommender.get_recommendations_by_mood(
                st.session_state.mood, st.session_state.duration
            )
        else:
            st.session_state.recommendations = st.session_state.recommender.get_personalized_recommendations()

# 主界面
def main():
    # 标题栏
    st.markdown("<h1 class='main-header'>🎬 AI观影助手</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>基于你的心情和喜好，推荐最适合你的电影</p>", unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.markdown("<h2 class='sub-header'>🧠 心情选择</h2>", unsafe_allow_html=True)
        st.markdown("当前的心情是什么？我们会为你找到匹配的电影！")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("😊 开心", key="happy", use_container_width=True):
                set_mood("开心")
                
            if st.button("😎 放松", key="relaxed", use_container_width=True):
                set_mood("放松")
                
            if st.button("🤔 无聊", key="bored", use_container_width=True):
                set_mood("无聊")
        
        with col2:
            if st.button("😢 伤感", key="sad", use_container_width=True):
                set_mood("伤感")
                
            if st.button("😲 兴奋", key="excited", use_container_width=True):
                set_mood("兴奋")
                
            if st.button("😨 害怕", key="scared", use_container_width=True):
                set_mood("害怕")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h2 class='sub-header'>⏱ 时长选择</h2>", unsafe_allow_html=True)
        st.markdown("你有多少时间可以观影？")
        
        duration_col1, duration_col2 = st.columns(2)
        
        with duration_col1:
            if st.button("短片 (<60分钟)", key="short", use_container_width=True):
                set_duration("短片")
                
            if st.button("长片 (2-3小时)", key="long", use_container_width=True):
                set_duration("长片")
        
        with duration_col2:
            if st.button("标准 (1-2小时)", key="standard", use_container_width=True):
                set_duration("标准")
                
            if st.button("超长 (>3小时)", key="extra_long", use_container_width=True):
                set_duration("超长")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🔍 获取推荐", key="get_recommendations", use_container_width=True):
            get_recommendations()
            
        if st.button("🔄 个性化推荐", key="personalized", use_container_width=True):
            st.session_state.mood = None
            st.session_state.duration = None
            get_recommendations()
            
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3>当前选择</h3>", unsafe_allow_html=True)
        mood_text = st.session_state.mood if st.session_state.mood else "无"
        duration_text = st.session_state.duration if st.session_state.duration else "不限"
        st.markdown(f"**心情**: {mood_text}")
        st.markdown(f"**时长**: {duration_text}")
        
    # 主内容区
    if st.session_state.movie_details:
        show_movie_detail_page()
    else:
        show_recommendation_page()

def show_recommendation_page():
    if not st.session_state.recommendations:
        st.info("👈 请从左侧选择你的心情和可用时间，然后点击'获取推荐'按钮")
        
        # 显示一些热门电影
        st.markdown("<h2 class='sub-header'>🔥 热门电影</h2>", unsafe_allow_html=True)
        try:
            trending = st.session_state.tmdb_api.get_trending_movies()
            display_movie_grid(trending['results'][:6])
        except Exception as e:
            st.error(f"获取热门电影时出错: {e}")
    else:
        if st.session_state.mood:
            st.markdown(f"<h2 class='sub-header'>基于你的'{st.session_state.mood}'心情推荐</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 class='sub-header'>为你的个性化推荐</h2>", unsafe_allow_html=True)
            
        display_movie_grid(st.session_state.recommendations)
        
def show_movie_detail_page():
    movie = st.session_state.movie_details
    
    # 返回按钮
    if st.button("← 返回推荐列表"):
        st.session_state.movie_details = None
        st.experimental_rerun()
        
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if movie.get('poster_path'):
            st.image(st.session_state.tmdb_api.get_image_url(movie['poster_path']), width=300)
        else:
            st.image("https://via.placeholder.com/300x450?text=No+Image", width=300)
    
    with col2:
        st.markdown(f"<h1>{movie['title']}</h1>", unsafe_allow_html=True)
        
        # 发行日期和时长
        release_date = movie.get('release_date', '未知')
        runtime = movie.get('runtime', 0)
        hours, minutes = divmod(runtime, 60)
        runtime_str = f"{hours}小时{minutes}分钟" if hours > 0 else f"{minutes}分钟"
        
        st.markdown(f"**发行日期**: {release_date} | **时长**: {runtime_str} | **评分**: {movie['vote_average']}/10")
        
        # 类型
        genres = [genre['name'] for genre in movie.get('genres', [])]
        st.markdown(f"**类型**: {', '.join(genres)}")
        
        # 简介
        st.markdown("### 简介")
        st.markdown(movie.get('overview', '暂无简介'))
        
        # 评价按钮
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👍 喜欢", key="like_detail"):
                mark_as_watched(movie['id'], True)
                st.success("已添加到你喜欢的电影！")
                time.sleep(1)
                st.experimental_rerun()
        with col2:
            if st.button("👎 不喜欢", key="dislike_detail"):
                mark_as_watched(movie['id'], False)
                st.success("已记录你的评价！")
                time.sleep(1)
                st.experimental_rerun()
        with col3:
            if st.button("🕒 稍后再看", key="watch_later"):
                mark_as_watched(movie['id'])
                st.success("已添加到稍后再看！")
                time.sleep(1)
                st.experimental_rerun()
    
    # 相似电影推荐
    st.markdown("### 相似电影推荐")
    try:
        similar = st.session_state.tmdb_api.get_recommended_movies(movie['id'])
        display_movie_grid(similar['results'][:6])
    except Exception as e:
        st.error(f"获取相似电影时出错: {e}")

def display_movie_grid(movies, cols=3):
    if not movies:
        st.info("没有找到符合条件的电影")
        return
        
    # 创建网格布局
    for i in range(0, len(movies), cols):
        row_movies = movies[i:i+cols]
        columns = st.columns(cols)
        
        for j, movie in enumerate(row_movies):
            with columns[j]:
                display_movie_card(movie)

def display_movie_card(movie):
    # 卡片容器
    st.markdown(f"<div class='movie-card'>", unsafe_allow_html=True)
    
    # 海报
    if movie.get('poster_path'):
        st.image(st.session_state.tmdb_api.get_image_url(movie['poster_path']), width=200)
    else:
        st.image("https://via.placeholder.com/200x300?text=No+Image", width=200)
    
    # 电影信息
    st.markdown(f"<p class='movie-title'>{movie['title']}</p>", unsafe_allow_html=True)
    
    # 评分和发行日期
    year = movie.get('release_date', '')[:4] if movie.get('release_date') else '未知'
    st.markdown(f"<p class='movie-info'>⭐ {movie['vote_average']}/10 | {year}</p>", unsafe_allow_html=True)
    
    # 简介（截断）
    overview = movie.get('overview', '暂无简介')
    if len(overview) > 100:
        overview = overview[:100] + "..."
    st.markdown(f"<p class='movie-overview'>{overview}</p>", unsafe_allow_html=True)
    
    # 按钮
    if st.button("查看详情", key=f"details_{movie['id']}"):
        show_movie_details(movie['id'])
        st.experimental_rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()