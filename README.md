# AI观影助手

<div align="center">
  <img src="assets/images/logo.png" alt="AI观影助手" width="200"/>
  <h3>基于心情和个人喜好的智能电影推荐系统</h3>
</div>

## 📖 项目简介

AI观影助手是一款利用人工智能技术，根据用户心情、时间和个人偏好推荐最合适电影的应用程序。无论你是想放松心情、寻找刺激，还是只有有限的观影时间，AI观影助手都能为你找到完美匹配的电影。

### ✨ 主要功能

- **基于心情推荐**：根据当前心情（开心、伤感、放松等）推荐合适的电影
- **时长筛选**：根据可用时间快速筛选适合长度的电影
- **个性化推荐**：学习用户偏好，提供越来越精准的推荐
- **高级搜索**：多条件组合搜索，快速找到想看的电影
- **观影统计**：可视化展示用户观影习惯和偏好分析
- **详细信息**：提供电影完整信息和相似电影推荐

## 🚀 快速开始

### 前提条件

- Python 3.8+
- TMDB API密钥 ([如何获取](https://developers.themoviedb.org/3/getting-started/introduction))

### 安装步骤

1. **克隆代码库**

```bash
git clone https://github.com/yourusername/movie-recommender.git
cd movie-recommender
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置API密钥**

有两种方式设置TMDB API密钥：

- 创建`.env`文件：
```
TMDB_API_KEY=your_api_key_here
```

- 或通过环境变量：
```bash
export TMDB_API_KEY=your_api_key_here  # Linux/Mac
# 或
set TMDB_API_KEY=your_api_key_here  # Windows
```

4. **运行应用**

```bash
streamlit run app.py
```

5. **打开浏览器**

自动打开或访问 http://localhost:8501

## 📱 使用指南

### 首页推荐

1. 选择当前心情（开心、伤感、放松、兴奋、害怕、无聊）
2. 选择可用观影时间（短片、标准、长片、超长）
3. 点击"获取推荐"按钮
4. 浏览推荐电影，点击"查看详情"了解更多

### 电影搜索

1. 使用快速搜索直接输入关键词
2. 或使用高级筛选，设置类型、年份、评分等条件
3. 点击搜索按钮获取结果
4. 查看搜索历史快速重复之前的搜索

### 观影统计

1. 查看观影数量和好评率
2. 分析你最喜欢的电影类型
3. 浏览最近观看记录
4. 导出或重置观影数据

## 📊 数据来源

本应用使用[TMDB API](https://www.themoviedb.org/documentation/api)获取电影数据。TMDB提供了丰富的电影信息、海报图片和评分数据。

## 🛠️ 技术栈

- **Frontend**: Streamlit
- **Backend**: Python
- **API**: TMDB REST API
- **Data Analysis**: Pandas, Plotly
- **Recommendation Engine**: 自定义算法

## 📝 项目设计

项目采用模块化设计，主要组件包括：

- **推荐引擎**：基于心情匹配和用户历史偏好进行推荐
- **API封装**：处理与TMDB的所有通信
- **多页面UI**：直观友好的用户界面
- **数据存储**：本地保存用户观影记录和偏好

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出新功能建议！请遵循以下步骤：

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢[TMDB](https://www.themoviedb.org/)提供数据API
- 感谢Streamlit团队提供了出色的Web应用框架
- 感谢所有电影爱好者的支持和反馈

---

<div align="center">
  <p>用AI发现完美电影，享受每一次观影体验！</p>
  <p>Made with ❤️ by Movie Lovers</p>
</div>