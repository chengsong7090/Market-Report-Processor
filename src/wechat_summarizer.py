#!/usr/bin/env python3
"""
WeChat Summarizer - Specialized summarizer for WeChat sharing

Creates concise, readable summaries optimized for WeChat group sharing.
Focuses on buy/sell recommendations, key data points, and investment logic.
"""

import re
from src.llm_summarizer import LLMSummarizer

class WeChatSummarizer:
    def __init__(self):
        """Initialize WeChat summarizer with LLM backend."""
        self.llm_summarizer = LLMSummarizer()
        
    def generate_wechat_summary(self, pdf_text, filename=""):
        """
        Generate WeChat-friendly summary from PDF text.
        
        Args:
            pdf_text (str): Raw text extracted from PDF
            filename (str): Original filename for source attribution
            
        Returns:
            str: Formatted WeChat summary (≤300 characters)
        """
        try:
            # Create specialized prompt for WeChat format
            wechat_prompt = self._create_wechat_prompt(pdf_text, filename)
            
            # Get LLM summary using existing infrastructure
            if self.llm_summarizer.deepseek_available:
                try:
                    print("📱 正在使用DeepSeek生成微信分享格式...")
                    summary = self._summarize_with_deepseek_wechat(wechat_prompt)
                    return self._format_wechat_output(summary, filename)
                except Exception as e:
                    print(f"⚠️ DeepSeek失败: {e}")
            
            if self.llm_summarizer.gemini_available:
                try:
                    print("📱 正在生成微信分享格式...")
                    summary = self._summarize_with_gemini_wechat(wechat_prompt)
                    return self._format_wechat_output(summary, filename)
                except Exception as e:
                    print(f"⚠️ Gemini失败: {e}")
            
            if self.llm_summarizer.qwen_available:
                try:
                    print("📱 使用Qwen生成微信格式...")
                    summary = self._summarize_with_qwen_wechat(wechat_prompt)
                    return self._format_wechat_output(summary, filename)
                except Exception as e:
                    print(f"⚠️ Qwen失败: {e}")
            
            # Fallback to basic extraction
            return self._fallback_summary(pdf_text, filename)
            
        except Exception as e:
            return f"❌ 分析失败: {filename}\n错误: {str(e)}"
    
    def _create_wechat_prompt(self, pdf_text, filename):
        """Create specialized prompt for WeChat summary."""
        # Truncate text if too long
        max_length = 15000
        if len(pdf_text) > max_length:
            pdf_text = pdf_text[:max_length] + "\n\n[内容已截断...]"
        
        prompt = f"""
你是一个专业的金融分析师，需要为微信群分享创建内容详实、论据充分的研报总结。

**处理流程：**
1.  **识别来源与对象**：首先准确识别研报的**发布机构**（如高盛、摩根大通）及其主要分析的**公司或行业**。
2.  **提炼核心观点与结论**：客观提炼报告的核心判断，包括但不限于：行业趋势预测、公司前景展望、投资评级（增持/买入/中性等）及目标价。
3.  **详实总结支撑论据**：这是关键。必须深入提取支持其核心结论的**2-3个主要逻辑和关键数据**作为支撑论点，要求具体、详实。
4.  **聚焦关键数据**：突出呈现最重要的具体数据，如增长率、市场份额、规模预测、估值倍数、订单情况等。
5.  **严格规避内容**：删除所有风险提示、免责声明、主观臆断及冗余背景信息。

**输出要求：**
-   **语言**：纯中文，行文专业且平实，适合金融从业者阅读。
-   **字数**：**200至400字之间**，确保内容充实且不超限。
-   **内容**：必须严格基于研报原文，客观呈现其观点与论据。

**输出格式：**
[机构名称]发布关于[公司名称/行业名称]的最新研究。[其主要观点/认为]：[用1-2句话概括核心判断或趋势预测]。
**核心支撑论据包括**：
1.  [第一个详细支撑论点，包含具体数据或事实]；
2.  [第二个详细支撑论点，包含具体数据或事实]；
3.  [（可选）第三个详细支撑论点，包含具体数据或事实]。
(基于上述分析，[机构名称]维持/给予[股票代码]"[评级]"评级及目标价[目标价]。)

**参考案例：**
高盛发布关于中国半导体行业的最新研究。其认为中国半导体行业正迎来新一轮资本支出扩张与技术升级。
**核心支撑论据包括**：
1.  资本支出大幅上调：将2025-2030年行业资本支出预测上调至430-460亿美元，投资重点更多转向存储器和先进制程节点；
2.  本土厂商深度受益：预计本土半导体生产设备（SPE）供应商的市场份额将从2025年的26%显著提升至2030年的36%；
3.  光刻机需求庞大：提出到2035年，中国需新增超过2261台光刻机才能满足全部芯片需求，揭示了巨大的设备市场空间。
高盛看好中国半导体发展的核心逻辑还包括庞大的本土市场、技术生态持续成熟及生成式AI推动供应链发展，并具体看好半导体设备（SPE）及先进制程相关子行业（IP、设计、代工、封装等）。

请根据上述规则，对以下文档进行分析和总结：
文档: {filename}
内容: {pdf_text}
"""
        return prompt
    
    def _summarize_with_deepseek_wechat(self, prompt):
        """Use DeepSeek for WeChat summary."""
        response = self.llm_summarizer.deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是专业的金融分析师，擅长创建简洁的微信分享内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    
    def _summarize_with_gemini_wechat(self, prompt):
        """Use Gemini for WeChat summary."""
        response = self.llm_summarizer.model.generate_content(prompt)
        return response.text.strip()
    
    def _summarize_with_qwen_wechat(self, prompt):
        """Use Qwen for WeChat summary."""
        response = self.llm_summarizer.qwen_client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是专业的金融分析师，擅长创建简洁的微信分享内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    
    def _format_wechat_output(self, summary, filename):
        """Format and validate WeChat output."""
        # Clean up the summary
        summary = summary.strip()
        
        # Remove any markdown formatting
        summary = re.sub(r'\*\*([^*]+)\*\*', r'\1', summary)
        summary = re.sub(r'\*([^*]+)\*', r'\1', summary)
        
        # Ensure it's not too long (400 characters max)
        if len(summary) > 400:
            # Try to truncate at sentence boundary
            sentences = summary.split('。')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + "。") <= 395:
                    truncated += sentence + "。"
                else:
                    break
            if truncated:
                summary = truncated
            else:
                summary = summary[:395] + "..."
        
        return summary
    
    def _fallback_summary(self, pdf_text, filename):
        """Create basic summary when LLMs are unavailable."""
        # Extract key information using simple text processing
        lines = pdf_text.split('\n')
        
        # Look for common patterns
        company_name = self._extract_company_name(lines)
        rating = self._extract_rating(lines)
        target_price = self._extract_target_price(lines)
        source = self._extract_source(filename)
        
        summary = f"{source}观点: {company_name}\n"
        if rating:
            summary += f"{rating}评级"
        if target_price:
            summary += f"，目标价{target_price}"
        
        summary += f"\n📄 来源: {filename}"
        
        return summary[:400]
    
    def _extract_company_name(self, lines):
        """Extract company name from text."""
        for line in lines[:10]:  # Check first 10 lines
            if any(keyword in line for keyword in ['股份', '公司', '科技', '集团']):
                # Simple extraction - could be improved
                words = line.split()
                for word in words:
                    if any(keyword in word for keyword in ['股份', '公司', '科技', '集团']):
                        return word[:10]  # Limit length
        return "目标公司"
    
    def _extract_rating(self, lines):
        """Extract investment rating."""
        rating_keywords = {
            'buy': '买入', 'overweight': '增持', 'hold': '持有', 
            'sell': '卖出', 'underweight': '减持',
            '买入': '买入', '增持': '增持', '持有': '持有'
        }
        
        text = ' '.join(lines[:20]).lower()
        for eng, chn in rating_keywords.items():
            if eng in text:
                return chn
        return ""
    
    def _extract_target_price(self, lines):
        """Extract target price."""
        import re
        text = ' '.join(lines[:20])
        
        # Look for price patterns
        price_patterns = [
            r'目标价[：:]?\s*([¥$]?\d+\.?\d*)',
            r'target price[：:]?\s*([¥$]?\d+\.?\d*)',
            r'([¥$]?\d+\.?\d*)\s*元',
            r'([¥$]?\d+\.?\d*)\s*港元'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
    
    def _extract_source(self, filename):
        """Extract source institution from filename."""
        sources = {
            'jpmorgan': '摩根大通', 'jp': '摩根大通', 'jpm': '摩根大通',
            'goldman': '高盛', 'gs': '高盛',
            'morgan': '摩根士丹利', 'ms': '摩根士丹利',
            'citi': '花旗', 'citigroup': '花旗',
            'ubs': '瑞银', 'credit': '瑞信',
            'bofa': '美银', 'bank of america': '美银'
        }
        
        filename_lower = filename.lower()
        for key, value in sources.items():
            if key in filename_lower:
                return value
        
        return "研究机构"
    
    def combine_summaries(self, summaries):
        """Combine multiple summaries into one comprehensive summary."""
        if not summaries:
            return "未找到有效分析结果"
        
        if len(summaries) == 1:
            return summaries[0]
        
        # Extract common elements
        sources = set()
        companies = set()
        ratings = []
        
        for summary in summaries:
            # Extract source
            if '观点:' in summary:
                source = summary.split('观点:')[0].strip()
                sources.add(source)
            
            # Extract ratings
            if '买入' in summary:
                ratings.append('买入')
            elif '增持' in summary:
                ratings.append('增持')
            elif '持有' in summary:
                ratings.append('持有')
        
        # Create combined summary
        if sources:
            source_text = '、'.join(list(sources)[:2])  # Max 2 sources
        else:
            source_text = "多家机构"
        
        # Determine consensus rating
        if ratings:
            most_common_rating = max(set(ratings), key=ratings.count)
        else:
            most_common_rating = "关注"
        
        combined = f"{source_text}综合观点:\n"
        combined += f"一致{most_common_rating}评级\n"
        combined += f"基于{len(summaries)}份研报的综合分析\n"
        combined += "详细观点请见上方各机构分析"
        
        return combined[:400]
