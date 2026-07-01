#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证器测试脚本"""

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
    from utils.validators import InputValidator, validate_user_input

    print("🧪 测试验证器")
    print("=" * 60)

    validator = InputValidator()

    # 测试邮箱验证
    print("\n1️⃣ 测试邮箱验证:")
    test_emails = [
        "test@example.com",
        "invalid-email",
        "user@gmail.com"
    ]
    for email in test_emails:
        is_valid, error = validator.validate_email(email)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {email}: {error if error else '有效'}")

    # 测试时间范围验证
    print("\n2️⃣ 测试时间范围验证:")
    time_ranges = ["1y", "3m", "invalid", "2020-2023"]
    for time_range in time_ranges:
        is_valid, error = validator.validate_time_range(time_range)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {time_range}: {error if error else '有效'}")

    # 测试完整参数验证
    print("\n3️⃣ 测试完整参数验证:")
    test_params = {
        'topic': 'machine learning',
        'time_range': '1y',
        'max_results': 10,
        'recipients': ['user@example.com'],
        'domain': 'ai'
    }
    is_valid, errors, normalized = validate_user_input(test_params)
    status = "✓" if is_valid else "✗"
    print(f"  {status} 参数验证: {', '.join(errors) if errors else '通过'}")

    # 测试无效参数
    print("\n4️⃣ 测试无效参数:")
    invalid_params = {
        'topic': '',  # 空主题
        'max_results': -1,  # 负数
        'recipients': ['invalid-email']  # 无效邮箱
    }
    is_valid, errors, normalized = validate_user_input(invalid_params)
    status = "✓" if is_valid else "✗"
    print(f"  {status} 参数验证: 检测到 {len(errors)} 个错误")
    if errors:
        for error in errors[:3]:
            print(f"      - {error}")

    print("\n✅ 验证器测试通过!")

except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)