"""
LLM Summarizer Module

This module handles AI-powered summarization of PDF content using Google Gemini API.
It provides intelligent summarization with Google's free tier.
"""

import os

class LLMSummarizer:
    def __init__(self):
        """Initialize the LLM summarizer with Google Gemini API."""
        # Load API key from config
        try:
            from config import GEMINI_API_KEY
            self.api_key = GEMINI_API_KEY
        except ImportError:
            print("❌ 错误: 找不到配置文件 config.py")
            print("💡 请复制 config_template.py 为 config.py 并填入您的API密钥")
            raise Exception("配置文件缺失")
        
        # Initialize Gemini client
        self.gemini_available = False
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_available = True
            print("✅ Google Gemini API 连接成功")
        except Exception as e:
            print(f"⚠️  Google Gemini API 初始化失败: {e}")
            print("💡 请运行: pip install google-generativeai")
    
    def summarize_pdf_content(self, pdf_text):
        """
        Summarize PDF content using Google Gemini API only.
        
        Args:
            pdf_text (str): Raw text extracted from PDF
            
        Returns:
            str: Formatted Chinese summary or empty string if LLM fails
        """
        # Only try Google Gemini - no fallback
        if self.gemini_available:
            try:
                return self._summarize_with_gemini(pdf_text)
            except Exception as e:
                print(f"⚠️  Google Gemini失败: {e}")
                print("💡 将仅发送PDF文档，不包含AI总结")
                return ""
        else:
            print("⚠️  Google Gemini不可用")
            print("💡 将仅发送PDF文档，不包含AI总结")
            return ""
    
    def _summarize_with_gemini(self, pdf_text):
        """Summarize using Google Gemini API."""
        import google.generativeai as genai
        
        # Truncate text if too long (Gemini has token limits)
        max_length = 20000  # Gemini 1.5 Flash has higher limits
        if len(pdf_text) > max_length:
            pdf_text = pdf_text[:max_length] + "\n\n[内容已截断...]"
        
        prompt = f"""
你是一个专业的金融分析师和文档总结专家。请仔细分析以下PDF文档内容，并以中文提供详细、结构化的总结。

文档内容：
{pdf_text}

请按以下格式提供中文总结：
## 主要观点
- 核心论点
- 投资建议
- 风险因素

## 核心财务数据
- 目标价格/评级
- 关键财务表现
- 重要数字和指标

## 关键洞察
- 市场趋势分析
- 行业前景
- 竞争优势

## 重要风险
- 主要风险点
- 不确定性因素

请确保总结准确、全面，并且易于理解。如果文档是英文的，请将所有关键信息翻译成中文。
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API调用失败: {str(e)}")
    
