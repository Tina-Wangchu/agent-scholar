#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""技能集成测试脚本"""

import sys
import os
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加scripts目录到路径
script_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(script_dir))

try:
    from config_manager import ConfigManager
    from workflow_executor import WorkflowExecutor

    print("🧪 测试技能集成")
    print("=" * 60)

    # 创建组件
    config_manager = ConfigManager()
    executor = WorkflowExecutor(config_manager)

    # 测试技能路径定位
    print("\n1️⃣ 测试技能路径定位:")
    skill_paths = executor.skill_paths
    for skill_name, skill_path in skill_paths.items():
        exists = skill_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {skill_name}: {skill_path}")
        if not exists:
            print(f"      警告: {skill_name} 技能脚本不存在")

    # 检查所有技能是否都存在
    all_exist = all(path.exists() for path in skill_paths.values())
    if not all_exist:
        print("\n⚠️  部分技能脚本缺失，完整工作流测试将跳过")
        print("💡 提示: 请确保以下技能已正确安装:")
        missing = [name for name, path in skill_paths.items() if not path.exists()]
        for name in missing:
            print(f"      - {name}")
        sys.exit(0)

    # 测试参数验证
    print("\n2️⃣ 测试工作流参数验证:")
    test_params = {
        'topic': 'artificial intelligence',
        'time_range': '1y',
        'max_results': 3,
        'domain': 'ai',
        'recipients': ['test@example.com'],
        'report_format': 'pdf',
        'email_body_type': 'html'
    }

    is_valid, errors = executor.validate_workflow_params(test_params)
    status = "✓" if is_valid else "✗"
    print(f"  {status} 参数验证: {', '.join(errors) if errors else '通过'}")

    if not is_valid:
        print("⚠️  参数验证失败，无法继续测试")
        sys.exit(1)

    # 测试配置加载
    print("\n3️⃣ 测试默认参数加载:")
    defaults = config_manager.get_default_params()
    print(f"  ✓ 默认时间范围: {defaults.get('time_range', 'N/A')}")
    print(f"  ✓ 默认最大结果: {defaults.get('max_results', 'N/A')}")
    print(f"  ✓ 默认研究领域: {defaults.get('domain', 'N/A')}")

    # 测试临时目录设置
    print("\n4️⃣ 测试临时目录设置:")
    temp_dir = executor.temp_dir
    temp_exists = temp_dir.exists()
    status = "✓" if temp_exists else "✗"
    print(f"  {status} 临时目录: {temp_dir}")
    if not temp_exists:
        print("      注意: 临时目录不存在，将在执行时自动创建")

    print("\n✅ 技能集成测试通过!")
    print("\n💡 下一步: 可以测试完整工作流")
    print("   命令: python scripts/paper_email_service.py --test-mode --topic 'AI'")

except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)