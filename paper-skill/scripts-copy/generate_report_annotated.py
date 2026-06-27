#!/usr/bin/env python3
"""
报告生成脚本 - Generate PDF Reports from Paper Search Results

这个脚本将论文检索结果生成专业的学术PDF报告。

使用示例：
    python generate_report.py --input papers.json --output report.pdf

功能特点：
    - 读取 paper_search.py 输出的JSON文件
    - 生成专业学术格式的PDF报告
    - 包含封面页、目录、论文列表、趋势分析、参考文献
    - 支持中英文内容

系统要求：
    - reportlab（PDF生成库）: pip install reportlab
    - matplotlib（图表库）: pip install matplotlib
    - Python 3.8+

中文字体支持：
    - Windows: SimSun（宋体）, SimHei（黑体）, Microsoft YaHei
    - Linux: WenQuanYi, Noto Sans CJK
    - macOS: PingFang, STHeiti
"""

# ==================== 第一部分：导入必要的库 ====================

import argparse        # 用于解析命令行参数
import json            # 用于处理JSON格式数据
import sys             # 用于系统相关操作
from datetime import datetime, timezone  # 用于处理时间
from pathlib import Path                # 用于处理文件路径
from typing import Dict, List, Any, Optional  # 类型提示

# ==================== 第二部分：PDF生成库导入 ====================
# reportlab是一个用于生成PDF文档的Python库
# 我们尝试导入它，如果用户没有安装，给出友好的提示

try:
    # 从reportlab导入PDF生成相关的模块
    from reportlab.lib.pagesizes import A4           # A4纸张尺寸
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # 样式管理
    from reportlab.lib.units import cm               # 单位转换（厘米）
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT  # 文本对齐方式
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle  # PDF构建组件
    from reportlab.platypus import KeepTogether      # 保持元素在同一页
    from reportlab.lib import colors                  # 颜色定义
    from reportlab.pdfbase import pdfmetrics          # PDF度量工具
    from reportlab.pdfbase.ttfonts import TTFont      # TrueType字体支持
    REPORTLAB_AVAILABLE = True  # 标记导入成功
except ImportError:
    # 如果导入失败，设置标志并给出提示
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation disabled.", file=sys.stderr)
    print("Install with: pip install reportlab", file=sys.stderr)


# ==================== 第三部分：PDF报告生成器类 ====================
# 这是生成PDF报告的核心类

class PDFReportGenerator:
    """
    PDF报告生成器

    这个类负责：
    1. 创建PDF文档样式（字体、颜色、间距等）
    2. 构建报告的各个部分（封面、论文列表、分析等）
    3. 将所有内容组合成最终的PDF文件
    """

    def __init__(self, input_data: Dict[str, Any], config: Dict[str, Any] = None):
        """
        初始化报告生成器

        参数：
            input_data: 从paper_search.py读取的搜索结果
            config: 可选的配置参数（预留扩展用）
        """
        self.input_data = input_data      # 保存搜索结果数据
        self.config = config or {}        # 保存配置（使用空字典作为默认值）
        self.styles = self._create_styles()  # 创建文档样式
        self.story = []                   # 存储PDF内容的列表（story是reportlab的术语）

    def _create_styles(self):
        """
        创建自定义段落样式

        在reportlab中，"样式"定义了文本的外观：
        - 字体大小和类型
        - 颜色
        - 对齐方式
        - 间距

        这个函数为报告创建了一套统一的样式体系
        """
        # 如果reportlab不可用，返回None
        if not REPORTLAB_AVAILABLE:
            return None

        # 获取reportlab的默认样式作为基础
        styles = getSampleStyleSheet()

        # 创建报告标题样式（大标题，居中，学术蓝色）
        styles.add(ParagraphStyle(
            name='CustomTitle',              # 样式名称
            parent=styles['Heading1'],       # 基于Heading1样式
            fontSize=24,                     # 字体大小24磅
            textColor=colors.HexColor('#2C5F8D'),  # 学术蓝色
            spaceAfter=30,                   # 段后间距30磅
            alignment=TA_CENTER,             # 居中对齐
            fontName='Helvetica-Bold'        # 粗体Helvetica字体
        ))

        # 创建一级标题样式（章节标题）
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,                     # 字体大小18磅
            textColor=colors.HexColor('#2C5F8D'),  # 学术蓝色
            spaceAfter=12,                   # 段后间距12磅
            spaceBefore=20,                  # 段前间距20磅
            fontName='Helvetica-Bold'        # 粗体
        ))

        # 创建二级标题样式（小节标题）
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,                     # 字体大小14磅
            textColor=colors.HexColor('#2C5F8D'),  # 学术蓝色
            spaceAfter=10,                   # 段后间距10磅
            spaceBefore=15,                  # 段前间距15磅
            fontName='Helvetica-Bold'        # 粗体
        ))

        # 创建正文样式（普通段落）
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,                     # 字体大小11磅
            spaceAfter=8,                    # 段后间距8磅
            leading=16,                      # 行间距16磅
            fontName='Helvetica'             # 常规Helvetica字体
        ))

        # 创建元数据样式（用于显示辅助信息）
        styles.add(ParagraphStyle(
            name='CustomMeta',
            parent=styles['BodyText'],
            fontSize=10,                     # 字体大小10磅
            textColor=colors.HexColor('#7F8C8D'),  # 灰色（不太显眼）
            spaceAfter=6,                    # 段后间距6磅
            fontName='Helvetica'             # 常规字体
        ))

        return styles  # 返回创建的样式集合

    def _add_cover_page(self):
        """
        添加封面页

        封面页包含：
        - 报告标题（基于检索主题）
        - 检索元数据（时间、数据源、论文数量）
        - 生成机构信息
        """
        if not REPORTLAB_AVAILABLE:
            return

        # 添加主标题（基于检索主题）
        title = f"{self.input_data.get('query', 'Paper Search Results')} Research Report"
        self.story.append(Paragraph(title, self.styles['CustomTitle']))  # 添加到story中
        self.story.append(Spacer(1, 2*cm))  # 添加空白间距（2厘米）

        # 添加元数据信息
        meta_data = [
            f"<b>Research Topic:</b> {self.input_data.get('query', 'N/A')}",  # 研究主题
            f"<b>Generated:</b> {self.input_data.get('timestamp', 'N/A')}",  # 生成时间
            f"<b>Total Papers:</b> {self.input_data.get('total_found', 0)}",  # 论文总数
            f"<b>Data Sources:</b> {', '.join(self.input_data.get('sources_used', []))}",  # 数据源
        ]

        # 如果有时间范围信息，添加进去
        filters = self.input_data.get('filters_applied', {})
        if filters.get('time_range'):
            time_range = filters['time_range']
            meta_data.append(
                f"<b>Time Range:</b> {time_range.get('start_date', 'N/A')} to {time_range.get('end_date', 'N/A')}"
            )

        # 将每条元数据添加到story
        for meta in meta_data:
            self.story.append(Paragraph(meta, self.styles['CustomBody']))  # 添加段落
            self.story.append(Spacer(1, 0.3*cm))  # 添加小段间距

        # 添加底部信息（生成机构）
        self.story.append(Spacer(1, 2*cm))  # 添加大段间距
        self.story.append(Paragraph(
            "Generated by Hermes Agent Academic Paper Search System",
            self.styles['CustomMeta']
        ))

    def _add_summary_section(self):
        """
        添加检索概况部分

        这个部分用表格形式展示：
        - 检索参数
        - 结果统计
        - 数据源信息
        """
        if not REPORTLAB_AVAILABLE:
            return

        # 添加分页符（新的一页）
        self.story.append(PageBreak())
        # 添加章节标题
        self.story.append(Paragraph("Search Summary", self.styles['CustomHeading1']))

        # 构建表格数据
        summary_data = [
            ["<b>Parameter</b>", "<b>Value</b>"],  # 表头
            ["Search Query", self.input_data.get('query', 'N/A')],
            ["Total Papers Found", str(self.input_data.get('total_found', 0))],
            ["Data Sources Used", ', '.join(self.input_data.get('sources_used', []))],
            ["Search Timestamp", self.input_data.get('timestamp', 'N/A')],
        ]

        # 添加时间范围信息（如果有）
        filters = self.input_data.get('filters_applied', {})
        if filters.get('time_range'):
            time_range = filters['time_range']
            summary_data.append([
                "Time Range",
                f"{time_range.get('start_date', 'N/A')} to {time_range.get('end_date', 'N/A')}"
            ])

        # 创建表格
        table = Table(summary_data, colWidths=[5*cm, 10*cm])  # 指定列宽

        # 设置表格样式
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5F8D')),  # 表头背景色（学术蓝）
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),              # 表头文字颜色（白色）
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),                 # 表头字体（粗体）
            ('FONTSIZE', (0, 0), (-1, 0), 12),                                # 表头字体大小
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),                           # 表头底部内边距
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),                  # 数据行背景色（米色）
            ('GRID', (0, 0), (-1, -1), 1, colors.black)                       # 网格线（1磅粗，黑色）
        ]))

        # 将表格添加到story
        self.story.append(table)
        self.story.append(Spacer(1, 1*cm))  # 添加间距

    def _add_papers_section(self):
        """
        添加论文列表部分

        这是报告的核心内容，展示每篇论文的详细信息：
        - 标题
        - 作者
        - 年份
        - 期刊/会议
        - DOI
        - 引用量
        - 摘要
        """
        if not REPORTLAB_AVAILABLE:
            return

        # 添加分页符和章节标题
        self.story.append(PageBreak())
        self.story.append(Paragraph("Core Papers List", self.styles['CustomHeading1']))

        # 获取论文列表
        papers = self.input_data.get('papers', [])

        # 遍历每篇论文
        for i, paper in enumerate(papers, 1):  # 从1开始计数
            # 添加论文编号和标题
            self.story.append(Paragraph(f"Paper #{i}", self.styles['CustomHeading2']))

            # 添加论文标题
            title = paper.get('title', 'N/A')
            self.story.append(Paragraph(f"<b>Title:</b> {title}", self.styles['CustomBody']))

            # 添加作者列表
            authors = paper.get('authors', [])
            if authors:
                # 只显示前5位作者，超过5位显示"等"
                author_list = ', '.join(str(a) for a in authors[:5])
                if len(authors) > 5:
                    author_list += f" et al. ({len(authors)} authors)"
                self.story.append(Paragraph(f"<b>Authors:</b> {author_list}", self.styles['CustomBody']))

            # 添加年份
            year = paper.get('year') or (paper.get('published', '')[:4] if paper.get('published') else 'N/A')
            self.story.append(Paragraph(f"<b>Year:</b> {year}", self.styles['CustomBody']))

            # 添加期刊/会议信息
            if paper.get('journal'):
                self.story.append(Paragraph(f"<b>Journal:</b> {paper.get('journal')}", self.styles['CustomBody']))

            # 添加DOI链接
            if paper.get('doi'):
                doi = paper.get('doi')
                # 创建可点击的DOI链接
                self.story.append(Paragraph(
                    f'<b>DOI:</b> <link href="https://doi.org/{doi}">{doi}</link>',
                    self.styles['CustomBody']
                ))

            # 添加引用量
            if paper.get('citationCount'):
                self.story.append(Paragraph(
                    f"<b>Citations:</b> {paper.get('citationCount')}",
                    self.styles['CustomBody']
                ))

            # 添加摘要（截取前500字）
            if paper.get('summary') or paper.get('abstract'):
                abstract = (paper.get('summary') or paper.get('abstract', '')).strip()
                if len(abstract) > 500:
                    abstract = abstract[:500] + "..."  # 超过500字就截断并加省略号
                self.story.append(Paragraph(f"<b>Abstract:</b> {abstract}", self.styles['CustomBody']))

            # 添加URL链接
            if paper.get('url'):
                self.story.append(Paragraph(
                    f'<b>URL:</b> <link href="{paper.get("url")}">{paper.get("url")}</link>',
                    self.styles['CustomBody']
                ))

            # 添加数据源信息
            if paper.get('source'):
                self.story.append(Paragraph(
                    f"<b>Source:</b> {paper.get('source')}",
                    self.styles['CustomMeta']
                ))

            # 添加间距
            self.story.append(Spacer(1, 0.8*cm))

            # 添加分隔线（用下划线字符）
            self.story.append(Paragraph("_" * 80, self.styles['CustomMeta']))
            self.story.append(Spacer(1, 0.5*cm))

    def _add_analysis_section(self):
        """
        添加研究趋势分析部分

        这个部分分析检索结果并提供统计信息：
        - 年度发文量分布
        - 数据源分布
        - 研究洞察
        """
        if not REPORTLAB_AVAILABLE:
            return

        # 添加分页符和章节标题
        self.story.append(PageBreak())
        self.story.append(Paragraph("Research Trend Analysis", self.styles['CustomHeading1']))

        # 获取论文列表
        papers = self.input_data.get('papers', [])

        # 统计年度发文量
        year_counts = {}
        for paper in papers:
            # 提取年份
            year = paper.get('year') or (paper.get('published', '')[:4] if paper.get('published') else 'Unknown')
            if year and year != 'Unknown':
                year_counts[year] = year_counts.get(year, 0) + 1  # 计数加1

        # 如果有年份数据，添加年度分布表格
        if year_counts:
            self.story.append(Paragraph("Publication Year Distribution", self.styles['CustomHeading2']))

            # 构建表格数据
            year_data = [["<b>Year</b>", "<b>Papers</b>"]]  # 表头
            # 按年份降序排列
            for year in sorted(year_counts.keys(), reverse=True):
                year_data.append([year, str(year_counts[year])])

            # 创建表格
            year_table = Table(year_data, colWidths=[4*cm, 4*cm])
            # 设置表格样式（与概况部分相同）
            year_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5F8D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))

            # 添加表格和间距
            self.story.append(year_table)
            self.story.append(Spacer(1, 1*cm))

        # 统计数据源分布
        source_counts = {}
        for paper in papers:
            source = paper.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1

        # 如果有数据源信息，添加分布表格
        if source_counts:
            self.story.append(Paragraph("Data Source Distribution", self.styles['CustomHeading2']))

            # 构建表格数据
            source_data = [["<b>Source</b>", "<b>Papers</b>"]]  # 表头
            # 按数量降序排列
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                source_data.append([source, str(count)])

            # 创建表格
            source_table = Table(source_data, colWidths=[6*cm, 4*cm])
            # 设置表格样式
            source_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5F8D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))

            # 添加表格和间距
            self.story.append(source_table)
            self.story.append(Spacer(1, 1*cm))

        # 添加研究洞察（文本分析）
        self.story.append(Paragraph("Research Insights", self.styles['CustomHeading2']))

        insights = []  # 存储洞察条目的列表
        if len(papers) > 0:
            # 基本统计
            insights.append(f"• Total of {len(papers)} papers found matching the search criteria.")
            # 最新年份
            if year_counts:
                latest_year = max(year_counts.keys())
                insights.append(f"• Most recent publications from {latest_year}.")
            # 主要数据源
            if source_counts:
                top_source = max(source_counts, key=source_counts.get)
                insights.append(f"• Primary data source: {top_source} ({source_counts[top_source]} papers).")
        else:
            insights.append("• No papers found. Consider adjusting search parameters.")

        # 将每条洞察添加到story
        for insight in insights:
            self.story.append(Paragraph(insight, self.styles['CustomBody']))

    def _add_references_section(self):
        """
        添加参考文献部分

        这个部分将所有论文按GB/T 7714格式（中国国家标准）列出
        格式：[序号] 作者. 标题. 期刊, 年份. DOI: xxxxx
        """
        if not REPORTLAB_AVAILABLE:
            return

        # 添加分页符和章节标题
        self.story.append(PageBreak())
        self.story.append(Paragraph("References", self.styles['CustomHeading1']))

        # 获取论文列表
        papers = self.input_data.get('papers', [])

        # 遍历每篇论文，构建参考文献条目
        for i, paper in enumerate(papers, 1):
            ref_parts = []  # 存储参考文献的各个部分

            # 作者
            authors = paper.get('authors', [])
            if authors:
                # 只显示前3位作者，超过3位显示"等"
                author_names = ', '.join(str(a) for a in authors[:3])
                if len(authors) > 3:
                    author_names += ', et al.'
                ref_parts.append(author_names)

            # 标题
            ref_parts.append(paper.get('title', 'N/A'))

            # 期刊/来源
            if paper.get('journal'):
                ref_parts.append(paper.get('journal'))

            # 年份
            year = paper.get('year') or (paper.get('published', '')[:4] if paper.get('published') else '')
            if year:
                ref_parts.append(year)

            # DOI
            if paper.get('doi'):
                ref_parts.append(f"DOI: {paper.get('doi')}")

            # 将所有部分用句号和空格连接，前面加上序号
            reference = f"[{i}] " + '. '.join(ref_parts) + '.'
            # 添加到story
            self.story.append(Paragraph(reference, self.styles['CustomBody']))
            self.story.append(Spacer(1, 0.3*cm))  # 添加小段间距

    def generate(self, output_path: str) -> bool:
        """
        生成完整的PDF报告

        这是主函数，按顺序调用各个部分的内容生成函数：
        1. 封面页
        2. 检索概况
        3. 论文列表
        4. 趋势分析
        5. 参考文献

        参数：
            output_path: 输出PDF文件的路径

        返回：
            True表示成功，False表示失败
        """
        if not REPORTLAB_AVAILABLE:
            # 如果reportlab不可用，无法生成PDF
            print("Error: reportlab not installed. Cannot generate PDF.", file=sys.stderr)
            return False

        try:
            # 按顺序构建文档的各个部分
            self._add_cover_page()         # 1. 封面页
            self._add_summary_section()     # 2. 检索概况
            self._add_papers_section()      # 3. 论文列表
            self._add_analysis_section()    # 4. 趋势分析
            self._add_references_section()  # 5. 参考文献

            # 创建PDF文档对象
            doc = SimpleDocTemplate(
                output_path,              # 输出文件路径
                pagesize=A4,              # A4纸张大小
                rightMargin=2*cm,         # 右边距2厘米
                leftMargin=2*cm,          # 左边距2厘米
                topMargin=2*cm,           # 上边距2厘米
                bottomMargin=2*cm         # 下边距2厘米
            )

            # 构建PDF（将story中的所有内容渲染成PDF）
            doc.build(self.story)
            return True  # 返回成功

        except Exception as e:
            # 如果出现任何错误，打印错误信息并返回失败
            print(f"Error generating PDF: {e}", file=sys.stderr)
            return False


# ==================== 第四部分：工具函数 ====================

def load_input_data(input_path: str) -> Optional[Dict[str, Any]]:
    """
    从文件加载输入数据

    参数：
        input_path: JSON文件的路径

    返回：
        解析后的Python字典，如果出错则返回None

    解释：
        这个函数读取paper_search.py生成的JSON文件，
        并验证数据是否有效
    """
    try:
        # 打开并读取JSON文件
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 检查搜索是否成功（status字段应该是"success"）
        if data.get('status') != 'success':
            print(f"Error: Input data indicates failed search: {data.get('error', 'Unknown error')}", file=sys.stderr)
            return None

        return data  # 返回解析后的数据
    except FileNotFoundError:
        # 文件不存在
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        # JSON格式错误
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        return None
    except Exception as e:
        # 其他错误
        print(f"Error loading input data: {e}", file=sys.stderr)
        return None


def generate_markdown_report(input_data: Dict[str, Any], output_path: str) -> bool:
    """
    生成Markdown格式的报告（作为PDF的备选）

    参数：
        input_data: 搜索结果数据
        output_path: 输出文件路径

    返回：
        True表示成功，False表示失败

    解释：
        当reportlab不可用时，可以生成Markdown格式的报告
        Markdown是纯文本格式，无需特殊库
    """
    try:
        # 打开输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            # 添加标题（一级标题）
            f.write(f"# {input_data.get('query', 'Paper Search Results')} Research Report\n\n")

            # 添加元数据
            f.write("## Search Metadata\n\n")
            f.write(f"- **Research Topic:** {input_data.get('query', 'N/A')}\n")
            f.write(f"- **Generated:** {input_data.get('timestamp', 'N/A')}\n")
            f.write(f"- **Total Papers:** {input_data.get('total_found', 0)}\n")
            f.write(f"- **Data Sources:** {', '.join(input_data.get('sources_used', []))}\n\n")

            # 添加论文列表
            f.write("## Core Papers List\n\n")
            papers = input_data.get('papers', [])
            for i, paper in enumerate(papers, 1):
                # 每篇论文的标题（三级标题）
                f.write(f"### Paper #{i}\n\n")
                f.write(f"**Title:** {paper.get('title', 'N/A')}\n\n")

                # 作者列表
                authors = paper.get('authors', [])
                if authors:
                    author_list = ', '.join(str(a) for a in authors[:5])
                    if len(authors) > 5:
                        author_list += f" et al. ({len(authors)} authors)"
                    f.write(f"**Authors:** {author_list}\n\n")

                # 年份
                year = paper.get('year') or (paper.get('published', '')[:4] if paper.get('published') else 'N/A')
                f.write(f"**Year:** {year}\n\n")

                # 期刊
                if paper.get('journal'):
                    f.write(f"**Journal:** {paper.get('journal')}\n\n")

                # DOI
                if paper.get('doi'):
                    f.write(f"**DOI:** [{paper.get('doi')}](https://doi.org/{paper.get('doi')})\n\n")

                # 引用量
                if paper.get('citationCount'):
                    f.write(f"**Citations:** {paper.get('citationCount')}\n\n")

                # 摘要（截取前500字）
                abstract = paper.get('summary') or paper.get('abstract', '')
                if abstract:
                    abstract_text = abstract[:500] + "..." if len(abstract) > 500 else abstract
                    f.write(f"**Abstract:** {abstract_text}\n\n")

                f.write("---\n\n")  # 分隔线

            # 添加分析部分
            f.write("## Research Trend Analysis\n\n")
            f.write("This report was generated by Hermes Agent Academic Paper Search System.\n")

        return True  # 返回成功
    except Exception as e:
        # 出错时打印错误信息
        print(f"Error generating Markdown report: {e}", file=sys.stderr)
        return False


# ==================== 第五部分：命令行接口 ====================
# 处理用户从命令行传入的参数

def main():
    """
    主函数 - 程序的入口点

    这个函数：
    1. 解析命令行参数
    2. 加载输入数据
    3. 调用报告生成器
    4. 输出结果或错误信息
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="Generate PDF reports from paper search results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=""  # 帮助信息的示例部分
    )

    # 添加命令行参数
    parser.add_argument("--input", required=True, help="Input JSON file from paper_search.py")
    parser.add_argument("--output", required=True, help="Output report file path")
    parser.add_argument("--format", default="pdf", choices=["pdf", "markdown"],
                       help="Output format (default: pdf)")

    # 解析参数
    args = parser.parse_args()

    # 加载输入数据
    input_data = load_input_data(args.input)
    if not input_data:
        return 1  # 加载失败，返回错误状态码

    # 根据用户选择的格式生成报告
    if args.format == "pdf":
        # 生成PDF报告
        generator = PDFReportGenerator(input_data)
        success = generator.generate(args.output)
        if success:
            print(f"✅ PDF report generated successfully: {args.output}")
            return 0  # 成功，返回0
        else:
            print("❌ Failed to generate PDF report", file=sys.stderr)
            return 1  # 失败，返回1
    else:  # markdown
        # 生成Markdown报告
        success = generate_markdown_report(input_data, args.output)
        if success:
            print(f"✅ Markdown report generated successfully: {args.output}")
            return 0  # 成功，返回0
        else:
            print("❌ Failed to generate Markdown report", file=sys.stderr)
            return 1  # 失败，返回1


# ==================== 程序入口点 ====================
# 当脚本被直接运行时（而不是被导入为模块），执行main函数
if __name__ == "__main__":
    # 运行主函数并将返回值作为退出状态码
    sys.exit(main())
