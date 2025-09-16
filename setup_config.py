#!/usr/bin/env python3
"""
Setup Configuration for GTJA Report Processor

This script helps users set up their configuration file with the required credentials.
"""

import os
import shutil

def setup_config():
    """Setup configuration file for the application."""
    print("🔧 GTJA Report Processor - 配置设置")
    print("=" * 50)
    
    # Check if config.py already exists
    if os.path.exists("config.py"):
        print("⚠️  配置文件 config.py 已存在")
        response = input("是否要重新配置? (y/N): ").strip().lower()
        if response != 'y':
            print("✅ 保持现有配置")
            return
    
    # Copy template to config.py
    if not os.path.exists("config_template.py"):
        print("❌ 错误: 找不到 config_template.py 文件")
        return
    
    try:
        shutil.copy2("config_template.py", "config.py")
        print("✅ 已创建 config.py 文件")
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return
    
    print("\n📝 请编辑 config.py 文件并填入以下信息:")
    print("   1. Gmail 邮箱地址和密码")
    print("   2. Google Gemini API 密钥")
    print("   3. 默认收件人邮箱")
    print("   4. 默认水印文本")
    
    print("\n💡 提示:")
    print("   - Gmail 密码需要使用应用专用密码，不是普通密码")
    print("   - Google Gemini API 密钥可以从 https://makersuite.google.com/app/apikey 获取")
    print("   - 配置完成后，运行 python main.py 启动应用程序")
    
    print("\n🔒 安全提醒:")
    print("   - config.py 文件包含敏感信息，不会被上传到 Git")
    print("   - 请妥善保管您的配置文件")

if __name__ == "__main__":
    setup_config()
