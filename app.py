import streamlit as st
import os
import time
from utils.api import TMDBApi
from utils.recommend import MovieRecommender

# 导入各页面模块
# 注意：在实际部署中，这些模块应该放在pages目录下
# 这里为了简化演示，假设它们都在同一个文件中
# 实际使用时应该导入各个页面的app函数

# 如果是使用页面模块导入:
# from pages.home import app as home_app
# from pages.search import app as search_app
# from pages.profile import app as profile_app

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
    .sidebar .sidebar-content {
        background-color: #f5f5f5;
    }
    div.block-container {
        padding-top: 2rem;
    }
    .nav-link {
        text-decoration: none;
        color: inherit;
        cursor: pointer;
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        border-radius: 5px;
        display: flex;
        align-items: center;
    }
    .nav-link:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }
    .nav-link.active {
        background-color: rgba(255, 75, 75, 0.1);
        color: #FF4B4B;
        font-weight: bold;
    }
    .nav-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
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

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# 导入页面模块后引入的app函数
from pages.home import app as home_app
from pages.search import app as search_app
from pages.profile import app as profile_app

# 导航栏
def show_navigation():
    """显示侧边栏导航"""
    st.sidebar.image("assets/images/logo.png", use_column_width=True)
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    
    # 导航菜单
    nav_options = {
        "home": {
            "icon": "🏠",
            "title": "首页推荐",
            "desc": "发现适合你心情的电影"
        },
        "search": {
            "icon": "🔍",
            "title": "搜索电影",
            "desc": "查找特定电影或浏览分类"
        },
        "profile": {
            "icon": "📊",
            "title": "观影统计",
            "desc": "查看你的观影历史和喜好分析"
        }
    }
    
    for page_id, page_info in nav_options.items():
        active_class = "active" if st.session_state.current_page == page_id else ""
        
        if st.sidebar.markdown(
            f"""
            <div class="nav-link {active_class}" id="{page_id}">
                <span class="nav-icon">{page_info['icon']}</span>
                <div>
                    <div>{page_info['title']}</div>
                    <div style="font-size:0.8rem;opacity:0.8;">{page_info['desc']}</div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        ):
            st.session_state.current_page = page_id
            st.experimental_rerun()
    
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    
    # 附加信息
    st.sidebar.markdown("### 关于")
    st.sidebar.markdown(
        """
        AI观影助手是一款智能电影推荐应用，基于你的心情和喜好，
        帮助你发现最适合当下观看的电影。
        
        **数据来源:** [TMDB API](https://www.themoviedb.org/)
        
        **版本:** 1.0.0
        """
    )
    
    # API密钥设置
    if st.sidebar.expander("API设置"):
        with st.form("api_settings"):
            new_api_key = st.text_input(
                "TMDB API密钥", 
                value=st.session_state.tmdb_api.api_key,
                type="password"
            )
            
            if st.form_submit_button("保存"):
                st.session_state.tmdb_api.api_key = new_api_key
                st.success("API密钥已更新！")
                time.sleep(1)
                st.experimental_rerun()

# JavaScript代码用于导航交互
nav_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const pageId = this.id;
            // 使用Streamlit的回调机制切换页面
            // 这需要配合Python代码工作
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: pageId
            }, '*');
        });
    });
});
</script>
"""

st.markdown(nav_script, unsafe_allow_html=True)

# 主函数
def main():
    """主程序入口"""
    # 显示侧边栏导航
    show_navigation()
    
    # 根据当前页面显示相应内容
    if st.session_state.movie_details:
        # 如果有电影详情，优先显示详情页面
        show_movie_detail_page(st.session_state.movie_details)
    elif st.session_state.current_page == "home":
        home_app()
    elif st.session_state.current_page == "search":
        search_app()
    elif st.session_state.current_page == "profile":
        profile_app()

def show_movie_detail_page(movie):
    """显示电影详情页"""
    # 返回按钮
    if st.button("← 返回"):
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
        
        # 原标题（如果与标题不同）
        if movie.get('original_title') and movie['original_title'] != movie['title']:
            st.markdown(f"**原标题**: {movie['original_title']}")
        
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
        
        # 演职人员
        if movie.get('credits', {}).get('cast'):
            cast = movie['credits']['cast'][:5]  # 只显示前5个
            cast_names = [member['name'] for member in cast]
            st.markdown(f"**主演**: {', '.join(cast_names)}")
        
        if movie.get('credits', {}).get('crew'):
            directors = [member['name'] for member in movie['credits']['crew'] if member['job'] == 'Director']
            if directors:
                st.markdown(f"**导演**: {', '.join(directors)}")
        
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

def mark_as_watched(movie_id, liked=None):
    """将电影标记为已观看"""
    st.session_state.recommender.add_watched_movie(movie_id, liked)
    
    # 如果在详情页，关闭它
    if st.session_state.movie_details and st.session_state.movie_details.get('id') == movie_id:
        st.session_state.movie_details = None

def display_movie_grid(movies, cols=3):
    """以网格形式显示电影列表"""
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
    """显示单部电影卡片"""
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
        
    st.markdown("</div>", unsafe_allow_html=True)

def show_movie_details(movie_id):
    """获取并显示电影详情"""
    try:
        details = st.session_state.tmdb_api.get_movie_details(movie_id)
        st.session_state.movie_details = details
        st.experimental_rerun()
    except Exception as e:
        st.error(f"获取电影详情时出错: {e}")

if __name__ == "__main__":
    main()