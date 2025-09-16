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
        Summarize PDF content using Google Gemini API.
        
        Args:
            pdf_text (str): Raw text extracted from PDF
            
        Returns:
            str: Formatted Chinese summary
        """
        # Try Google Gemini first
        if self.gemini_available:
            try:
                return self._summarize_with_gemini(pdf_text)
            except Exception as e:
                print(f"⚠️  Google Gemini失败，使用本地分析: {e}")
        
        # Fallback to local analysis
        return self._fallback_summarization(pdf_text)
    
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
    
    def _fallback_summarization(self, pdf_text):
        """Enhanced fallback summarization when API is unavailable."""
        lines = pdf_text.split('\n')
        
        # Extract different types of content
        headers = []
        financial_data = []
        key_metrics = []
        important_points = []
        company_info = []
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Headers and titles
            if (line.isupper() and len(line) > 5) or line.endswith(':') or any(word in line.lower() for word in ['summary', 'conclusion', 'overview', '概览', '总结']):
                headers.append(f"📋 {line}")
            
            # Financial data
            elif any(keyword in line.lower() for keyword in ['市值', '目标价', '评级', '买入', '卖出', '持有', 'market cap', 'target price', 'rating', 'buy', 'sell', 'hold', 'rmb', 'usd']):
                financial_data.append(f"💰 {line}")
            
            # Key metrics and numbers
            elif any(char in line for char in ['%', 'Rmb', '$', 'bn', 'mn', '亿', '万']) or (len(line) > 20 and any(char.isdigit() for char in line)):
                key_metrics.append(f"📊 {line}")
            
            # Company and entity information
            elif any(keyword in line.lower() for keyword in ['公司', '企业', '集团', 'corporation', 'company', 'inc', 'ltd', 'limited']):
                company_info.append(f"🏢 {line}")
            
            # Recommendations and conclusions
            elif any(keyword in line.lower() for keyword in ['建议', '推荐', '结论', 'recommendation', 'conclusion', '建议', '风险', '优势', '机会']):
                recommendations.append(f"💡 {line}")
            
            # Important content (substantial lines)
            elif len(line) > 30:
                important_points.append(f"• {line}")
        
        # Create enhanced summary
        summary = "=" * 80 + "\n"
        summary += "📋 PDF 智能分析总结 (本地模式)\n"
        summary += "=" * 80 + "\n\n"
        
        if headers:
            summary += "## 📋 文档结构:\n"
            summary += "\n".join(headers[:8]) + "\n\n"
        
        if company_info:
            summary += "## 🏢 公司信息:\n"
            summary += "\n".join(company_info[:5]) + "\n\n"
        
        if financial_data:
            summary += "## 💰 财务数据:\n"
            summary += "\n".join(financial_data[:10]) + "\n\n"
        
        if key_metrics:
            summary += "## 📊 关键指标:\n"
            summary += "\n".join(key_metrics[:10]) + "\n\n"
        
        if recommendations:
            summary += "## 💡 投资建议:\n"
            summary += "\n".join(recommendations[:8]) + "\n\n"
        
        if important_points:
            summary += "## 📝 重要内容:\n"
            summary += "\n".join(important_points[:15]) + "\n\n"
        
        summary += "=" * 80 + "\n"
        summary += "💡 提示: 这是本地智能分析模式。如需更详细的AI分析，请检查网络连接。\n"
        summary += "=" * 80
        
        return summary
