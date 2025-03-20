import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

def app():
    # 页面配置
    st.markdown("<h1 class='main-header'>📊 我的观影统计</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>了解你的观影习惯和偏好</p>", unsafe_allow_html=True)
    
    # 获取统计数据
    stats = st.session_state.recommender.get_viewing_stats()
    
    # 主要统计数字
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="border-radius:10px;padding:20px;text-align:center;background-color:#f0f8ff;">
                <h1 style="font-size:3rem;color:#0083B8;">{}</h1>
                <p>已观看电影</p>
            </div>
            """.format(stats["total_watched"]), 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style="border-radius:10px;padding:20px;text-align:center;background-color:#f0fff0;">
                <h1 style="font-size:3rem;color:#4CAF50;">{}</h1>
                <p>喜欢的电影</p>
            </div>
            """.format(stats["total_liked"]), 
            unsafe_allow_html=True
        )
    
    with col3:
        like_ratio = 0
        if stats["total_watched"] > 0:
            like_ratio = round((stats["total_liked"] / stats["total_watched"]) * 100)
            
        st.markdown(
            """
            <div style="border-radius:10px;padding:20px;text-align:center;background-color:#fff0f5;">
                <h1 style="font-size:3rem;color:#FF4B4B;">{}</h1>
                <p>好评率</p>
            </div>
            """.format(f"{like_ratio}%"), 
            unsafe_allow_html=True
        )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 如果没有观看记录
    if stats["total_watched"] == 0:
        st.info("你还没有观看记录，开始探索并添加一些电影吧！")
        return
    
    # 喜爱类型分析
    st.markdown("<h2 class='sub-header'>🎭 喜爱类型分析</h2>", unsafe_allow_html=True)
    
    if not stats["favorite_genres"]:
        st.info("还没有足够的数据分析你喜爱的电影类型")
    else:
        # 准备图表数据
        genre_data = pd.DataFrame(stats["favorite_genres"])
        
        # 使用Plotly创建条形图
        fig = px.bar(
            genre_data,
            x="name",
            y="score",
            color="score",
            color_continuous_scale="Viridis",
            labels={"name": "电影类型", "score": "喜好分数"},
            title="你最喜爱的电影类型"
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 文字分析
        top_genre = genre_data.iloc[0]["name"] if not genre_data.empty else "未知"
        st.markdown(f"🎬 你最喜欢的电影类型是 **{top_genre}**。")
        
        if len(genre_data) > 1:
            second_genre = genre_data.iloc[1]["name"]
            st.markdown(f"🌟 你也很喜欢 **{second_genre}** 类型的电影。")
            
        # 推荐文字
        st.markdown("### 💡 基于你的喜好，你可能会喜欢：")
        
        # 根据前两个最喜欢的类型组合推荐
        if len(genre_data) >= 2:
            st.markdown(f"- 结合 **{top_genre}** 和 **{second_genre}** 元素的电影")
        
        # 其他喜好类型推荐
        if len(genre_data) >= 3:
            third_genre = genre_data.iloc[2]["name"]
            st.markdown(f"- 探索更多 **{third_genre}** 类型的佳作")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 观影历史
    st.markdown("<h2 class='sub-header'>📜 最近观看记录</h2>", unsafe_allow_html=True)
    
    if not stats["watched_movies"]:
        st.info("暂无观影记录")
    else:
        # 创建表格显示最近观看的电影
        watched_df = pd.DataFrame(stats["watched_movies"])
        
        # 添加海报图片
        def get_poster_html(poster_path):
            if poster_path:
                image_url = st.session_state.tmdb_api.get_image_url(poster_path)
                return f'<img src="{image_url}" width="60">'
            return '<img src="https://via.placeholder.com/60x90?text=No+Image" width="60">'
        
        # 添加状态表情
        def get_status_emoji(status):
            if status == "liked":
                return "👍 喜欢"
            elif status == "disliked":
                return "👎 不喜欢"
            return "🤔 未评价"
            
        if not watched_df.empty:
            # 仅保留需要的列并重命名
            watched_df = watched_df[["title", "poster_path", "status", "date"]]
            watched_df["海报"] = watched_df["poster_path"].apply(get_poster_html)
            watched_df["评价"] = watched_df["status"].apply(get_status_emoji)
            watched_df["日期"] = watched_df["date"]
            watched_df["电影"] = watched_df["title"]
            
            # 只显示需要的列
            display_df = watched_df[["海报", "电影", "评价", "日期"]].copy()
            
            # 使用Streamlit显示表格
            st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 观影习惯分析
    if stats["total_watched"] >= 5:  # 只有当有足够数据时才显示
        st.markdown("<h2 class='sub-header'>📈 观影习惯分析</h2>", unsafe_allow_html=True)
        
        # 根据评分和类型生成一些分析数据（模拟数据）
        # 实际应用中可以从用户数据中分析
        
        # 创建喜欢与不喜欢比例饼图
        labels = ['喜欢', '不喜欢', '未评价']
        values = [
            stats["total_liked"], 
            stats["total_disliked"], 
            stats["total_watched"] - stats["total_liked"] - stats["total_disliked"]
        ]
        
        # 只保留非零值
        non_zero = [(l, v) for l, v in zip(labels, values) if v > 0]
        if non_zero:
            non_zero_labels, non_zero_values = zip(*non_zero)
            
            fig = go.Figure(data=[go.Pie(
                labels=non_zero_labels,
                values=non_zero_values,
                hole=.3,
                marker_colors=['#4CAF50', '#FF4B4B', '#9E9E9E']
            )])
            
            fig.update_layout(
                title_text="评价分布",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 提供一些观影建议
        st.markdown("### 🔍 观影习惯分析")
        
        if stats["total_liked"] > stats["total_disliked"]:
            st.markdown("✨ 你对大多数观看的电影都给予了积极评价，说明你的电影选择相当成功！")
        elif stats["total_disliked"] > stats["total_liked"]:
            st.markdown("🤔 你对很多电影给出了负面评价，也许可以尝试更多类型来找到你真正喜欢的。")
        
        # 添加一些随机但有用的建议
        import random
        tips = [
            "📺 建议尝试探索一些不同地区的电影，以扩展你的观影视野。",
            "🎬 考虑观看一些经典老片，它们常常包含深刻的艺术价值。",
            "🌟 多关注获奖电影可能会帮助你发现更多高质量内容。",
            "🎭 尝试观看一些独立电影，它们往往有独特的创意和表达方式。",
            "📽 考虑跟随某个你欣赏的导演的作品系列进行观看。"
        ]
        
        st.markdown(random.choice(tips))
    
    # 数据导出选项
    st.markdown("<h2 class='sub-header'>💾 数据管理</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 导出观影数据", use_container_width=True):
            # 创建导出数据
            export_data = {
                "export_date": datetime.now().strftime("%Y-%m-%d"),
                "stats": stats
            }
            
            # 转换为JSON
            json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            # 提供下载链接
            st.markdown(
                f"""
                <a href="data:application/json;charset=utf-8,{json_data}" 
                   download="my_movie_data.json">
                    点击下载观影数据
                </a>
                """, 
                unsafe_allow_html=True
            )
    
    with col2:
        if st.button("🗑️ 重置观影数据", use_container_width=True):
            # 确认对话框
            if st.session_state.get("confirm_reset") is None:
                st.session_state.confirm_reset = True
                st.warning("⚠️ 确定要删除所有观影数据吗？此操作不可逆！")
                
                confirm_col1, confirm_col2 = st.columns(2)
                with confirm_col1:
                    if st.button("✅ 确认删除", key="confirm_delete"):
                        # 重置用户数据
                        default_data = {"watched": [], "liked": [], "disliked": [], "preferences": {}}
                        st.session_state.recommender._save_user_data(default_data)
                        st.session_state.recommender.user_data = default_data
                        st.session_state.confirm_reset = None
                        st.success("数据已重置！")
                        st.experimental_rerun()
                
                with confirm_col2:
                    if st.button("❌ 取消", key="cancel_delete"):
                        st.session_state.confirm_reset = None
                        st.experimental_rerun()

if __name__ == "__main__":
    app()