#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流测试脚本
测试paper-email-service的完整功能，但不实际发送邮件
"""

import sys
import os
from pathlib import Path
import json

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加scripts目录到路径
script_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(script_dir))

def print_header(title):
    """打印标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

def print_step(step_num, description):
    """打印步骤"""
    print(f"\n{step_num}. {description}")
    print('-' * 40)

def print_success(message):
    """打印成功消息"""
    print(f"✅ {message}")

def print_error(message):
    """打印错误消息"""
    print(f"❌ {message}")

def print_info(message):
    """打印信息消息"""
    print(f"ℹ️  {message}")

def main():
    try:
        print_header("Paper Email Service 完整功能测试")

        # 导入所有模块
        print_step("1", "导入服务模块")
        from config_manager import ConfigManager
        from workflow_executor import WorkflowExecutor
        from task_scheduler import TaskScheduler
        from paper_email_service import PaperEmailService
        print_success("所有模块导入成功")

        # 测试配置管理
        print_step("2", "测试配置管理")
        config_manager = ConfigManager()

        # 加载默认配置
        default_config = config_manager.load_config('default')
        print_success(f"默认配置加载成功: {default_config.get('service', {}).get('name')}")

        # 获取预设任务
        presets = config_manager.get_preset_tasks()
        print_success(f"找到 {len(presets)} 个预设任务")

        # 获取默认参数
        defaults = config_manager.get_default_params()
        print_success(f"默认参数: 时间范围={defaults.get('time_range')}, 最大结果={defaults.get('max_results')}")

        # 测试工作流执行器
        print_step("3", "测试工作流执行器")
        workflow_executor = WorkflowExecutor(config_manager)

        # 检查技能路径
        skill_paths = workflow_executor.skill_paths
        all_skills_exist = all(path.exists() for path in skill_paths.values())
        if all_skills_exist:
            print_success("所有子技能路径正确")
            for skill_name, skill_path in skill_paths.items():
                print_info(f"  {skill_name}: ✓")
        else:
            print_error("部分子技能路径缺失")
            for skill_name, skill_path in skill_paths.items():
                status = "✓" if skill_path.exists() else "✗"
                print_info(f"  {skill_name}: {status}")

        # 测试参数验证
        test_params = {
            'topic': 'artificial intelligence',
            'time_range': '1y',
            'max_results': 5,
            'domain': 'ai',
            'recipients': ['test@example.com']
        }
        is_valid, errors = workflow_executor.validate_workflow_params(test_params)
        if is_valid:
            print_success("参数验证通过")
        else:
            print_error(f"参数验证失败: {errors}")

        # 测试任务调度器
        print_step("4", "测试任务调度器")
        task_scheduler = TaskScheduler(config_manager)

        # 获取所有任务
        all_tasks = task_scheduler.get_all_tasks()
        print_success(f"找到 {len(all_tasks)} 个任务（预设+自定义）")

        # 验证调度时间
        test_schedules = ["0 9 * * 1", "0 8 * * *", "1h"]
        for schedule in test_schedules:
            is_valid, error = task_scheduler.validate_task_schedule(schedule)
            status = "✓" if is_valid else "✗"
            print_info(f"  调度验证 {status} '{schedule}': {error if error else '有效'}")

        # 获取统计信息
        stats = task_scheduler.get_task_statistics()
        print_success(f"任务统计: 总数={stats['total_tasks']}, 启用={stats['enabled_tasks']}")

        # 测试主服务
        print_step("5", "测试主服务功能")
        service = PaperEmailService()

        # 显示服务状态
        status = service.show_service_status()
        print_success(f"服务状态: 配置={'✓' if status.get('config_loaded') else '✗'}, "
                     f"环境={'✓' if status.get('environment_ok') else '✗'}")

        # 测试预设任务详情
        if service.list_available_presets():
            first_preset = service.list_available_presets()[0]
            print_info(f"显示预设任务详情: {first_preset}")
            service.show_preset_details(first_preset)

        # 综合测试
        print_step("6", "综合功能测试")

        # 创建测试任务配置
        test_task_config = {
            'topic': 'machine learning',
            'time_range': '30d',
            'max_results': 10,
            'domain': 'ai',
            'recipients': ['test@example.com']
        }

        print_info("测试任务配置:")
        for key, value in test_task_config.items():
            print_info(f"  {key}: {value}")

        # 验证完整参数
        from utils.validators import validate_user_input
        is_valid, errors, normalized = validate_user_input(test_task_config)
        if is_valid:
            print_success("参数验证和规范化成功")
        else:
            print_error(f"参数验证失败: {errors}")

        # 测试配置构建器
        print_step("7", "测试配置构建器")
        from config_manager import ConfigBuilder
        builder = ConfigBuilder(config_manager)

        built_config = (builder
                       .with_topic("deep learning")
                       .with_time_range("2y")
                       .with_max_results(20)
                       .with_domain("ai")
                       .build())

        print_success("配置构建成功")
        print_info(f"  主题: {built_config.get('topic')}")
        print_info(f"  时间范围: {built_config.get('time_range')}")
        print_info(f"  最大结果: {built_config.get('max_results')}")

        # 测试格式化工具
        print_step("8", "测试格式化工具")
        from utils.formatters import DataFormatter, ReportFormatter

        # 测试论文数据格式化
        test_papers = [{
            'title': 'Test Paper',
            'authors': ['Author 1', 'Author 2'],
            'year': 2023,
            'abstract': 'This is a test abstract.',
            'venue': 'Test Journal',
            'citation_count': 100,
            'keywords': ['AI', 'ML'],
            'source': 'arXiv'
        }]

        formatted_papers = DataFormatter.format_paper_data(test_papers)
        print_success("论文数据格式化成功")
        print_info(f"  格式化后字段数: {len(formatted_papers[0].keys())}")

        # 测试报告摘要生成
        summary = ReportFormatter.generate_summary(formatted_papers, "AI", "1y")
        print_success("报告摘要生成成功")
        print_info(f"  论文总数: {summary.get('total_papers')}")
        print_info(f"  平均引用数: {summary.get('average_citations', 0):.1f}")

        # 最终总结
        print_header("测试总结")
        print_success("所有核心功能测试完成!")
        print_info("服务已准备就绪，可以执行以下操作:")
        print_info("1. 单次执行: python scripts/paper_email_service.py --single --topic 'AI'")
        print_info("2. 交互模式: python scripts/paper_email_service.py --interactive")
        print_info("3. 创建定时任务: python scripts/paper_email_service.py --create-task 'AI周报' --schedule '0 9 * * 1' --topic 'AI'")
        print_info("4. 查看服务状态: python scripts/paper_email_service.py --status")

        print_info("\n注意事项:")
        print_info("⚠️  首次使用前需要设置环境变量:")
        print_info("   - GMAIL_ADDRESS: 您的Gmail地址")
        print_info("   - GMAIL_APP_PASSWORD: Gmail应用专用密码")
        print_info("⚠️  如需访问Gmail，请配置代理:")
        print_info("   - SMTP_SOCKS_PROXY: socks5://127.0.0.1:7890")

        return 0

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())