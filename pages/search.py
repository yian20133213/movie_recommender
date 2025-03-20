import streamlit as st
import pandas as pd
from datetime import datetime
import time

def app():
    # 页面配置
    st.markdown("<h1 class='main-header'>🔍 电影搜索</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>找到你想看的任何电影</p>", unsafe_allow_html=True)
    
    # 初始化会话状态
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
        
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
        
    if 'search_genres' not in st.session_state:
        try:
            genres_response = st.session_state.tmdb_api.get_movie_genres()
            st.session_state.search_genres = genres_response['genres']
        except Exception as e:
            st.error(f"获取电影类型列表失败: {e}")
            st.session_state.search_genres = []
    
    # 布局：搜索选项卡和高级筛选
    tab1, tab2 = st.tabs(["📝 快速搜索", "⚙️ 高级筛选"])
    
    with tab1:
        show_basic_search()
        
    with tab2:
        show_advanced_search()
        
    # 显示搜索结果
    show_search_results()

def show_basic_search():
    """显示基本搜索界面"""
    with st.form(key="basic_search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input("输入电影名称或关键词", placeholder="例如：复仇者联盟、科幻、成龙...")
        
        with col2:
            submit_button = st.form_submit_button(label="搜索", use_container_width=True)
            
        if submit_button and query:
            perform_search(query)
            # 添加到搜索历史
            if query not in st.session_state.search_history:
                st.session_state.search_history.insert(0, query)
                # 只保留最近10条
                st.session_state.search_history = st.session_state.search_history[:10]
    
    # 显示搜索历史
    if st.session_state.search_history:
        st.markdown("### 最近搜索")
        history_cols = st.columns(len(st.session_state.search_history[:5]))
        
        for i, term in enumerate(st.session_state.search_history[:5]):
            with history_cols[i]:
                if st.button(term, key=f"history_{i}", use_container_width=True):
                    perform_search(term)

def show_advanced_search():
    """显示高级搜索界面"""
    with st.form(key="advanced_search_form"):
        # 第一行：关键词和年份
        col1, col2 = st.columns(2)
        
        with col1:
            query = st.text_input("关键词", placeholder="可选")
        
        with col2:
            current_year = datetime.now().year
            year = st.selectbox("年份", 
                                options=[None] + list(range(current_year, 1900, -1)),
                                format_func=lambda x: "全部年份" if x is None else x)
        
        # 第二行：类型和排序
        col1, col2 = st.columns(2)
        
        with col1:
            # 准备类型选择
            genre_options = []
            genre_id_map = {}
            
            for genre in st.session_state.search_genres:
                genre_options.append(genre['name'])
                genre_id_map[genre['name']] = genre['id']
                
            selected_genres = st.multiselect(
                "电影类型",
                options=genre_options
            )
            
            # 转换为类型ID列表
            genre_ids = [genre_id_map[name] for name in selected_genres] if selected_genres else None
        
        with col2:
            sort_options = {
                "popularity.desc": "人气降序",
                "popularity.asc": "人气升序",
                "vote_average.desc": "评分降序",
                "vote_average.asc": "评分升序",
                "release_date.desc": "上映日期降序",
                "release_date.asc": "上映日期升序",
                "original_title.asc": "标题字母升序"
            }
            
            sort_by = st.selectbox(
                "排序方式",
                options=list(sort_options.keys()),
                format_func=lambda x: sort_options[x],
                index=0
            )
        
        # 第三行：评分范围
        col1, col2 = st.columns(2)
        
        with col1:
            min_rating = st.slider("最低评分", min_value=0.0, max_value=10.0, value=0.0, step=0.5)
        
        with col2:
            include_adult = st.checkbox("包含成人内容", value=False)
        
        # 搜索按钮
        submit_button = st.form_submit_button(label="高级搜索", use_container_width=True)
        
        if submit_button:
            with st.spinner("搜索中..."):
                try:
                    # 构建发现参数
                    params = {
                        "sort_by": sort_by,
                        "page": 1
                    }
                    
                    if query:
                        # 如果有关键词，使用搜索API
                        results = st.session_state.tmdb_api.search_movies(query)
                    else:
                        # 否则使用发现API
                        results = st.session_state.tmdb_api.discover_movies(
                            genres=genre_ids,
                            year=year,
                            sort_by=sort_by
                        )
                    
                    # 过滤评分
                    filtered_results = []
                    for movie in results['results']:
                        if movie['vote_average'] >= min_rating:
                            if not include_adult and movie.get('adult', False):
                                continue
                            filtered_results.append(movie)
                    
                    # 更新结果
                    st.session_state.search_results = filtered_results
                    
                    if not filtered_results:
                        st.warning("没有找到符合条件的电影")
                    
                except Exception as e:
                    st.error(f"搜索时出错: {e}")

def perform_search(query):
    """执行搜索并更新结果"""
    with st.spinner("搜索中..."):
        try:
            results = st.session_state.tmdb_api.search_movies(query)
            st.session_state.search_results = results['results']
            
            if not results['results']:
                st.warning(f"没有找到与 '{query}' 相关的电影")
                
        except Exception as e:
            st.error(f"搜索时出错: {e}")

def show_search_results():
    """显示搜索结果"""
    if not st.session_state.search_results:
        # 没有结果时显示热门电影
        try:
            st.markdown("### 🔥 热门电影推荐")
            trending = st.session_state.tmdb_api.get_trending_movies()
            display_movie_grid(trending['results'][:6])
        except Exception as e:
            st.error(f"获取热门电影时出错: {e}")
        return
    
    st.markdown(f"### 找到 {len(st.session_state.search_results)} 部相关电影")
    display_movie_grid(st.session_state.search_results)

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
    if st.button("查看详情", key=f"search_details_{movie['id']}"):
        # 跳转到详情页
        st.session_state.movie_details = st.session_state.tmdb_api.get_movie_details(movie['id'])
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    app()