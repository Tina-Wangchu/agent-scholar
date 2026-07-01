#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单配置测试脚本"""

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

    print("🧪 测试配置管理器")
    print("=" * 60)

    # 创建配置管理器
    manager = ConfigManager()

    # 测试默认配置加载
    print("\n1️⃣ 测试默认配置加载:")
    default_config = manager.load_config('default')
    print(f"✓ 成功加载默认配置")
    print(f"✓ 服务名称: {default_config.get('service', {}).get('name', 'N/A')}")
    print(f"✓ 默认时间范围: {default_config.get('search_defaults', {}).get('time_range', 'N/A')}")

    # 测试合并配置
    print("\n2️⃣ 测试合并配置:")
    merged_config = manager.load_config('merged')
    print(f"✓ 成功加载合并配置")

    # 测试预设任务
    print("\n3️⃣ 测试预设任务:")
    presets = manager.get_preset_tasks()
    print(f"✓ 找到 {len(presets)} 个预设任务:")
    for preset_id in list(presets.keys())[:3]:
        print(f"  - {preset_id}")

    # 测试默认参数
    print("\n4️⃣ 测试默认参数:")
    defaults = manager.get_default_params()
    print(f"✓ 时间范围: {defaults.get('time_range', 'N/A')}")
    print(f"✓ 最大结果: {defaults.get('max_results', 'N/A')}")
    print(f"✓ 研究领域: {defaults.get('domain', 'N/A')}")

    print("\n✅ 配置管理器测试通过!")

except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)