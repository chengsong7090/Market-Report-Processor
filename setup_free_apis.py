"""
Free LLM API Setup Script

This script helps you set up free LLM APIs for PDF summarization.
Run this script to get instructions and API keys for free services.
"""

def main():
    print("=" * 80)
    print("🆓 免费LLM API 设置指南")
    print("=" * 80)
    print()
    
    print("📋 可用的免费LLM服务:")
    print()
    
    print("1. 🚀 Groq API (推荐 - 最快最稳定)")
    print("   - 网站: https://console.groq.com/")
    print("   - 免费额度: 14,400 requests/day")
    print("   - 速度: 极快 (GPU加速)")
    print("   - 模型: Llama 3.1 70B, Mixtral 8x7B")
    print("   - 获取步骤:")
    print("     a) 访问 https://console.groq.com/")
    print("     b) 注册账号 (免费)")
    print("     c) 创建API密钥")
    print("     d) 复制密钥到 src/llm_summarizer.py 第179行")
    print()
    
    print("2. 🤗 Hugging Face API")
    print("   - 网站: https://huggingface.co/settings/tokens")
    print("   - 免费额度: 1,000 requests/month")
    print("   - 速度: 中等")
    print("   - 模型: BART, T5等")
    print("   - 获取步骤:")
    print("     a) 访问 https://huggingface.co/settings/tokens")
    print("     b) 创建新的访问令牌")
    print("     c) 复制令牌到 src/llm_summarizer.py 第248行")
    print()
    
    print("3. 🏠 Ollama (本地运行)")
    print("   - 网站: https://ollama.ai/")
    print("   - 免费额度: 无限制 (本地)")
    print("   - 速度: 取决于你的硬件")
    print("   - 模型: Llama 3.1, Mistral, CodeLlama等")
    print("   - 安装步骤:")
    print("     a) 下载 Ollama: https://ollama.ai/download")
    print("     b) 安装并启动服务")
    print("     c) 运行: ollama pull llama3.1")
    print("     d) 无需API密钥")
    print()
    
    print("4. 🌐 Together AI")
    print("   - 网站: https://api.together.xyz/")
    print("   - 免费额度: $25 credit")
    print("   - 速度: 快")
    print("   - 模型: Llama 2, Mistral等")
    print("   - 获取步骤:")
    print("     a) 访问 https://api.together.xyz/")
    print("     b) 注册账号")
    print("     c) 获取API密钥")
    print("     d) 复制密钥到 src/llm_summarizer.py 第330行")
    print()
    
    print("=" * 80)
    print("⚡ 推荐设置顺序:")
    print("=" * 80)
    print("1. 首选: Groq API (最快最稳定)")
    print("2. 备选: Ollama (本地，无网络限制)")
    print("3. 其他: Hugging Face 或 Together AI")
    print()
    
    print("🔧 设置完成后，运行 python main.py 测试")
    print("=" * 80)

if __name__ == "__main__":
    main()
