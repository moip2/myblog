import os
import markdown
import yaml
from datetime import datetime

# 配置路径
POSTS_DIR = 'posts'
TEMPLATES_DIR = 'templates'
OUTPUT_DIR = '.' # 生成的 HTML 放在根目录

def build():
    # 确保文件夹存在
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)

    # 1. 加载模板文件
    try:
        with open(os.path.join(TEMPLATES_DIR, 'index.html'), 'r', encoding='utf-8') as f:
            index_tpl = f.read()
        with open(os.path.join(TEMPLATES_DIR, 'post.html'), 'r', encoding='utf-8') as f:
            post_tpl = f.read()
    except FileNotFoundError:
        print("错误：请确保 templates 文件夹中有 index.html 和 post.html")
        return

    posts_metadata = []

    # 2. 遍历并处理所有 Markdown 文章
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            with open(os.path.join(POSTS_DIR, filename), 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # 解析 Markdown 顶部的 YAML 信息 (标题、日期等)
            try:
                parts = raw_content.split('---', 2)
                if len(parts) < 3: continue
                
                meta = yaml.safe_load(parts[1])
                body_md = parts[2]
                # 将 Markdown 转换为 HTML
                body_html = markdown.markdown(body_md, extensions=['extra', 'codehilite', 'tables'])
                
                # 填充文章详情页模板
                title = meta.get('title', '无题')
                date_str = meta.get('date', '2026-04-18')
                
                page_html = post_tpl.replace('{{title}}', title)
                page_html = page_html.replace('{{date}}', str(date_str))
                page_html = page_html.replace('{{content}}', body_html)
                
                # 保存生成的 HTML 文件
                output_name = filename.replace('.md', '.html')
                with open(os.path.join(OUTPUT_DIR, output_name), 'w', encoding='utf-8') as f:
                    f.write(page_html)
                
                # 收集信息用于首页列表
                posts_metadata.append({
                    'title': title,
                    'date': date_str,
                    'excerpt': meta.get('excerpt', ''),
                    'url': output_name,
                    'dt': datetime.strptime(str(date_str), '%Y-%m-%d') if isinstance(date_str, str) else date_str
                })
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")

    # 3. 按日期排序并生成首页
    posts_metadata.sort(key=lambda x: x['dt'], reverse=True)
    
    post_list_html = ""
    for post in posts_metadata:
        post_list_html += f"""
        <article>
            <div class="post-date">{post['date']}</div>
            <a href="{post['url']}" class="post-title">{post['title']}</a>
            <p class="post-excerpt">{post['excerpt']}</p>
        </article>
        """
    
    # 将列表填入首页模板
    final_index = index_tpl.replace('{{post_list}}', post_list_html)
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(final_index)

    print(f"✅ 编译完成！共生成 {len(posts_metadata)} 篇文章。")

if __name__ == '__main__':
    build()
