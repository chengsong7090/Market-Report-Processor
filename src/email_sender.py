"""
Email Sender Module

This module handles sending emails with PDF attachments and text summaries.
Uses Gmail SMTP for reliable email delivery.
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class EmailSender:
    def __init__(self):
        """Initialize email sender with Gmail credentials."""
        # Gmail SMTP settings
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Load email credentials from config
        try:
            from config import EMAIL_SENDER_ACCOUNT, EMAIL_SENDER_USERNAME, EMAIL_SENDER_PASSWORD
            self.email_sender_account = EMAIL_SENDER_ACCOUNT
            self.email_sender_username = EMAIL_SENDER_USERNAME
            self.email_sender_password = EMAIL_SENDER_PASSWORD
        except ImportError:
            print("❌ 错误: 找不到配置文件 config.py")
            print("💡 请复制 config_template.py 为 config.py 并填入您的邮箱凭据")
            raise Exception("配置文件缺失")
    
    def send_pdf_summary_email(self, recipient_email, pdf_path, summary_text, original_filename):
        """
        Send email with PDF attachment and summary.
        
        Args:
            recipient_email (str): Recipient's email address
            pdf_path (str): Path to the clean PDF file
            summary_text (str): AI-generated summary text
            original_filename (str): Original PDF filename for reference
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_sender_account
            msg['To'] = recipient_email
            msg['Subject'] = f"Research Report - {original_filename}"
            
            # Create HTML email body - Lotus Notes compatible (table-based, inline CSS)
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; color: #333;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td style="padding: 20px;">
                {self._format_summary_html_lotus_notes(summary_text)}
                
                <table width="100%" cellpadding="10" cellspacing="0" border="0" bgcolor="#f0f0f0">
                    <tr>
                        <td style="font-size: 12px; color: #666;">
                            📎 Attachment: PDF Document
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
            
            # Attach HTML body to email
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Attach PDF file
            print(f"📎 检查PDF文件: {pdf_path}")
            print(f"📎 文件是否存在: {os.path.exists(pdf_path)}")
            if os.path.exists(pdf_path):
                print(f"📎 文件大小: {os.path.getsize(pdf_path)} bytes")
                print(f"📎 文件扩展名: {os.path.splitext(pdf_path)[1]}")
                
                # Read PDF file
                with open(pdf_path, "rb") as pdf_file:
                    pdf_data = pdf_file.read()
                
                # Create PDF attachment with proper MIME type
                part = MIMEBase('application', 'pdf')
                part.set_payload(pdf_data)
                encoders.encode_base64(part)
                
                # Use original filename for attachment
                clean_filename = original_filename
                
                print(f"📎 附件文件名: {clean_filename}")
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{clean_filename}"'
                )
                
                msg.attach(part)
                print(f"✅ PDF附件已添加: {clean_filename}")
            else:
                print(f"⚠️  PDF文件不存在: {pdf_path}")
                return False
            
            # Connect to Gmail SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.email_sender_username, self.email_sender_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_sender_account, recipient_email, text)
            server.quit()
            
            print(f"✅ 邮件发送成功: {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ 邮件发送失败: {str(e)}")
            return False
    
    def test_connection(self):
        """Test Gmail SMTP connection."""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_sender_username, self.email_sender_password)
            server.quit()
            print("✅ Gmail SMTP 连接测试成功")
            return True
        except Exception as e:
            print(f"❌ Gmail SMTP 连接测试失败: {str(e)}")
            return False
    
    def _format_summary_html_lotus_notes(self, summary_text):
        """Format the summary text into Lotus Notes compatible HTML using tables and inline CSS."""
        print(f"🔍 调试: 开始格式化Lotus Notes兼容HTML内容")
        print(f"🔍 调试: 摘要文本长度: {len(summary_text)}")
        
        # Split into sections based on ## headers
        sections = []
        current_section = ""
        current_content = []
        
        lines = summary_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for both ## and **## formats
            if line.startswith('## ') or line.startswith('**## '):
                # Save previous section
                if current_section and current_content:
                    sections.append((current_section, current_content))
                
                # Start new section
                if line.startswith('**## '):
                    current_section = line[5:-2].strip()  # Remove **## and **
                else:
                    current_section = line[3:].strip()  # Remove ##
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections.append((current_section, current_content))
        
        # Create Lotus Notes compatible HTML sections using tables
        html_sections = []
        for i, (section_title, content) in enumerate(sections):
            print(f"🔍 调试: 处理第{i+1}个部分: '{section_title}' (内容行数: {len(content)})")
            html_sections.append(self._create_lotus_notes_section(section_title, content))
        
        result = '\n'.join(html_sections)
        print(f"🔍 调试: 生成了 {len(html_sections)} 个Lotus Notes兼容HTML部分")
        print(f"🔍 调试: HTML内容长度: {len(result)}")
        return result

    def _format_summary_html(self, summary_text):
        """Format the summary text into beautiful HTML sections."""
        print(f"🔍 调试: 开始格式化HTML内容")
        print(f"🔍 调试: 摘要文本长度: {len(summary_text)}")
        
        # Split into sections based on ## headers
        sections = []
        current_section = ""
        current_content = []
        
        lines = summary_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for both ## and **## formats
            if line.startswith('## ') or line.startswith('**## '):
                # Save previous section
                if current_section and current_content:
                    sections.append((current_section, current_content))
                
                # Start new section
                if line.startswith('**## '):
                    current_section = line[5:-2].strip()  # Remove **## and **
                else:
                    current_section = line[3:].strip()  # Remove ##
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections.append((current_section, current_content))
        
        # Create HTML sections
        html_sections = []
        for i, (section_title, content) in enumerate(sections):
            print(f"🔍 调试: 处理第{i+1}个部分: '{section_title}' (内容行数: {len(content)})")
            html_sections.append(self._create_beautiful_html_section(section_title, content))
        
        result = '\n'.join(html_sections)
        print(f"🔍 调试: 生成了 {len(html_sections)} 个HTML部分")
        print(f"🔍 调试: HTML内容长度: {len(result)}")
        return result
    
    def _create_lotus_notes_section(self, title, content):
        """Create a Lotus Notes compatible HTML section using tables and inline CSS."""
        if not content:
            return ""
        
        # Process content into structured HTML
        html_content = self._process_section_content_lotus_notes(content)
        
        return f"""
        <table width="100%" cellpadding="15" cellspacing="0" border="0" bgcolor="#f9f9f9" style="margin-bottom: 20px; border: 1px solid #ccc;">
            <tr>
                <td>
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td style="font-size: 18px; font-weight: bold; color: #333; border-bottom: 2px solid #333; padding-bottom: 5px; margin-bottom: 15px;">
                                {title}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding-top: 10px;">
                                {html_content}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """

    def _create_beautiful_html_section(self, title, content):
        """Create a beautiful HTML section with proper formatting."""
        if not content:
            return ""
        
        # Determine section type and CSS class
        css_class = self._get_section_css_class(title)
        
        # Process content into structured HTML
        html_content = self._process_section_content(content)
        
        return f"""
        <div class="section">
            <h2>{title}</h2>
            {html_content}
        </div>
        """
    
    def _get_section_css_class(self, title):
        """Get CSS class based on section title."""
        # Simplified for Lotus Notes compatibility - all sections use same styling
        return ""
    
    def _process_section_content_lotus_notes(self, content):
        """Process section content into Lotus Notes compatible HTML using tables."""
        html_parts = []
        current_subsection = ""
        current_items = []
        
        for line in content:
            line = line.strip()
            if not line:
                continue
                
            # Check for bold subsection headers (like **## 主要观点**)
            if line.startswith('**## ') and line.endswith('**'):
                # Save previous subsection
                if current_subsection and current_items:
                    html_parts.append(self._create_subsection_html_lotus_notes(current_subsection, current_items))
                
                # Start new subsection
                current_subsection = line[5:-2].strip()  # Remove **## and **
                current_items = []
            elif line.startswith('- **') and ':**' in line:
                # Bold key point with description
                parts = line.split(':**', 1)
                if len(parts) == 2:
                    key = parts[0][2:].strip()  # Remove - **
                    value = parts[1].strip()
                    current_items.append(f"<strong>{key}:</strong> {value}")
                else:
                    current_items.append(line[2:])  # Remove - 
            elif line.startswith('- **') and not ':**' in line:
                # Bold text without colon
                current_items.append(f"<strong>{line[2:]}</strong>")  # Remove - **
            elif line.startswith('- '):
                # Regular bullet point
                current_items.append(line[2:])  # Remove - 
            else:
                # Regular text
                current_items.append(line)
        
        # Add the last subsection
        if current_subsection and current_items:
            html_parts.append(self._create_subsection_html_lotus_notes(current_subsection, current_items))
        elif current_items:
            # No subsection, just items
            html_parts.append(self._create_items_html_lotus_notes(current_items))
        
        return '\n'.join(html_parts)

    def _process_section_content(self, content):
        """Process section content into beautiful HTML."""
        html_parts = []
        current_subsection = ""
        current_items = []
        
        for line in content:
            line = line.strip()
            if not line:
                continue
                
            # Check for bold subsection headers (like **## 主要观点**)
            if line.startswith('**## ') and line.endswith('**'):
                # Save previous subsection
                if current_subsection and current_items:
                    html_parts.append(self._create_subsection_html(current_subsection, current_items))
                
                # Start new subsection
                current_subsection = line[5:-2].strip()  # Remove **## and **
                current_items = []
            elif line.startswith('- **') and ':**' in line:
                # Bold key point with description
                parts = line.split(':**', 1)
                if len(parts) == 2:
                    key = parts[0][2:].strip()  # Remove - **
                    value = parts[1].strip()
                    current_items.append(f"<strong>{key}:</strong> {value}")
                else:
                    current_items.append(line[2:])  # Remove - 
            elif line.startswith('- **') and not ':**' in line:
                # Bold text without colon
                current_items.append(f"<strong>{line[2:]}</strong>")  # Remove - **
            elif line.startswith('- '):
                # Regular bullet point
                current_items.append(line[2:])  # Remove - 
            else:
                # Regular text
                current_items.append(line)
        
        # Add the last subsection
        if current_subsection and current_items:
            html_parts.append(self._create_subsection_html(current_subsection, current_items))
        elif current_items:
            # No subsection, just items
            html_parts.append(self._create_items_html(current_items))
        
        return '\n'.join(html_parts)
    
    def _create_subsection_html_lotus_notes(self, title, items):
        """Create Lotus Notes compatible HTML for a subsection with title and items."""
        items_html = self._create_items_html_lotus_notes(items)
        return f"""
        <table width="100%" cellpadding="8" cellspacing="0" border="0" bgcolor="#ffffff" style="margin: 10px 0;">
            <tr>
                <td>
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td style="font-size: 14px; font-weight: bold; color: #333; margin-bottom: 8px;">
                                {title}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding-top: 5px;">
                                {items_html}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """

    def _create_items_html_lotus_notes(self, items):
        """Create Lotus Notes compatible HTML for a list of items using tables."""
        if not items:
            return ""
        
        html_items = []
        for item in items:
            if item.strip():
                html_items.append(f"""
                <table width="100%" cellpadding="5" cellspacing="0" border="0">
                    <tr>
                        <td style="padding-left: 20px; line-height: 1.4;">
                            • {item}
                        </td>
                    </tr>
                </table>
                """)
        
        return '\n'.join(html_items)

    def _create_subsection_html(self, title, items):
        """Create HTML for a subsection with title and items."""
        items_html = self._create_items_html(items)
        return f"""
        <div class="subsection">
            <h3>{title}</h3>
            {items_html}
        </div>
        """
    
    def _create_items_html(self, items):
        """Create HTML for a list of items."""
        if not items:
            return ""
        
        html_items = []
        for item in items:
            if item.strip():
                html_items.append(f"<li>{item}</li>")
        
        if html_items:
            return f"<ul>{''.join(html_items)}</ul>"
        return ""
    
    def _create_html_section(self, title, content, css_class):
        """Create an HTML section with proper formatting."""
        if not content:
            return ""
        
        # Format content as HTML list
        html_content = "<ul>"
        for item in content:
            if item.strip():
                # Clean up the item and format it
                clean_item = item.replace('**', '').replace('*', '')
                if clean_item.startswith('- '):
                    clean_item = clean_item[2:]
                html_content += f"<li>{clean_item}</li>"
        html_content += "</ul>"
        
        return f"""
        <div class="section">
            <h2>{title}</h2>
            {html_content}
        </div>
        """
