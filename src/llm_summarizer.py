"""
LLM Summarizer Module

This module handles AI-powered summarization of PDF content using DeepSeek API as primary, 
with Google Gemini and Alibaba Qwen as fallbacks.
It provides intelligent summarization with multiple LLM providers.
"""

import os

class LLMSummarizer:
    def __init__(self):
        """Initialize the LLM summarizer with DeepSeek API as primary, Gemini and Qwen as fallbacks."""
        # Load API keys from config
        try:
            from config import DEEPSEEK_API_KEY, GEMINI_API_KEY, QWEN_API_KEY
            self.deepseek_api_key = DEEPSEEK_API_KEY
            self.gemini_api_key = GEMINI_API_KEY
            self.qwen_api_key = QWEN_API_KEY
        except ImportError:
            print("❌ 错误: 找不到配置文件 config.py")
            print("💡 请复制 config_template.py 为 config.py 并填入您的API密钥")
            raise Exception("配置文件缺失")
        
        # Initialize DeepSeek client (Primary)
        self.deepseek_available = False
        try:
            from openai import OpenAI
            self.deepseek_client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com",
            )
            self.deepseek_available = True
            print("✅ DeepSeek API 连接成功")
        except Exception as e:
            print(f"⚠️  DeepSeek API 初始化失败: {e}")
            print("💡 将尝试使用 Google Gemini 作为备选")
        
        # Initialize Gemini client (Secondary)
        self.gemini_available = False
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_available = True
            if not self.deepseek_available:
                print("✅ Google Gemini API 连接成功")
        except Exception as e:
            print(f"⚠️  Google Gemini API 初始化失败: {e}")
            print("💡 将尝试使用 Alibaba Qwen 作为备选")
        
        # Initialize Qwen client (Tertiary)
        self.qwen_available = False
        try:
            from openai import OpenAI
            self.qwen_client = OpenAI(
                api_key=self.qwen_api_key,
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            )
            self.qwen_available = True
            if not self.deepseek_available and not self.gemini_available:
                print("✅ Alibaba Qwen API 连接成功")
        except Exception as e:
            print(f"⚠️  Alibaba Qwen API 初始化失败: {e}")
            if not self.deepseek_available and not self.gemini_available:
                print("💡 请运行: pip install openai")
    
    def summarize_pdf_content(self, pdf_text):
        """
        Summarize PDF content using DeepSeek API as primary, with Gemini and Qwen fallbacks.
        
        Args:
            pdf_text (str): Raw text extracted from PDF
            
        Returns:
            tuple: (summary_text, llm_name) or ("", "") if all LLMs fail
        """
        # Try DeepSeek first (Primary)
        if self.deepseek_available:
            try:
                print("📝 正在使用DeepSeek进行智能分析...")
                summary = self._summarize_with_deepseek(pdf_text)
                return summary, "DeepSeek"
            except Exception as e:
                print(f"⚠️  DeepSeek失败: {e}")
                print("💡 尝试使用 Google Gemini 作为备选")
        
        # Fallback to Google Gemini (Secondary)
        if self.gemini_available:
            try:
                print("📝 正在使用Google Gemini进行智能分析...")
                summary = self._summarize_with_gemini(pdf_text)
                return summary, "Google Gemini"
            except Exception as e:
                print(f"⚠️  Google Gemini失败: {e}")
                print("💡 尝试使用 Alibaba Qwen 作为备选")
        
        # Fallback to Alibaba Qwen (Tertiary)
        if self.qwen_available:
            try:
                print("📝 正在使用Alibaba Qwen进行智能分析...")
                summary = self._summarize_with_qwen(pdf_text)
                return summary, "Alibaba Qwen"
            except Exception as e:
                print(f"⚠️  Alibaba Qwen失败: {e}")
                print("💡 将仅发送PDF文档，不包含AI总结")
                return "", ""
        else:
            print("⚠️  没有可用的LLM服务")
            print("💡 将仅发送PDF文档，不包含AI总结")
            return "", ""
    
    def _summarize_with_deepseek(self, pdf_text):
        """Summarize using DeepSeek API."""
        # Truncate text if too long (DeepSeek has token limits)
        max_length = 20000  # Conservative limit for DeepSeek
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
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的金融分析师和文档总结专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
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
    
    def _summarize_with_qwen(self, pdf_text):
        """Summarize using Alibaba Qwen API."""
        # Truncate text if too long (Qwen has token limits)
        max_length = 15000  # Conservative limit for Qwen
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
            response = self.qwen_client.chat.completions.create(
                model="qwen-plus",  # Using Qwen-Plus model
                messages=[
                    {"role": "system", "content": "你是一个专业的金融分析师和文档总结专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Qwen API调用失败: {str(e)}")
    
