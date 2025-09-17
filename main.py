#!/usr/bin/env python3
"""
GTJA Report Processor - GUI Application

A comprehensive GUI application that processes PDF reports for GTJA.
Features include watermark removal, AI-powered summarization, and email distribution.
Users can upload a PDF, specify watermark text, and get a clean PDF with AI summary.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from src.pdf_processor import PDFProcessor
from src.llm_summarizer import LLMSummarizer
from src.email_sender import EmailSender

class GTJAReportProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("GTJA Report Processor")
        self.root.geometry("600x550")
        self.root.resizable(True, True)
        
        # Variables
        self.pdf_path = tk.StringVar()
        
        # Hardcoded watermark list - will remove any of these watermarks if found
        self.watermark_list = [
            "For the exclusive use of DAPHNE.WOO@GTJAS.COM.HK",
            "本文件专供 Guotai Junan Investments (Hong Kong) Limited 的 Daisy Zhu 使用"
        ]
        
        # Load default values from config
        try:
            from config import DEFAULT_RECIPIENT_EMAIL
            self.email_recipient = tk.StringVar()
        except ImportError:
            # Fallback defaults if config not available
            self.email_recipient = tk.StringVar()
        
        self.output_path = tk.StringVar()
        self.summarize_pdf = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="GTJA Report Processor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # PDF File Selection
        ttk.Label(main_frame, text="Select PDF File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.pdf_path, width=50)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Watermark Info (read-only display)
        watermark_info = ttk.Label(main_frame, text="Watermarks to remove: Pre-configured list (English & Chinese)", 
                                 foreground="blue", font=("Arial", 9))
        watermark_info.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(20, 5))
        
        # Output Path
        ttk.Label(main_frame, text="Output Path:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1)
        
        # Summarize PDF Checkbox
        self.summarize_checkbox = ttk.Checkbutton(main_frame, text="Summarize PDF content with AI (Chinese)", 
                                                variable=self.summarize_pdf)
        self.summarize_checkbox.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Email Section
        email_frame = ttk.LabelFrame(main_frame, text="📧 Email (Optional)", padding=10)
        email_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Email Recipient
        ttk.Label(email_frame, text="Recipient Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(email_frame, textvariable=self.email_recipient, width=40)
        self.email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Set default recipient from config
        try:
            from config import DEFAULT_RECIPIENT_EMAIL
            self.email_entry.insert(0, DEFAULT_RECIPIENT_EMAIL)
        except ImportError:
            self.email_entry.insert(0, "charles.song@gtjas.com.hk")  # Fallback default
        
        # Process Button
        self.process_button = ttk.Button(main_frame, text="Process PDF", 
                                       command=self.process_pdf, style="Accent.TButton")
        self.process_button.grid(row=8, column=0, columnspan=2, pady=30)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="Ready to process PDF", 
                                     foreground="green")
        self.status_label.grid(row=10, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        email_frame.columnconfigure(1, weight=1)
        
    def browse_file(self):
        """Browse for PDF file."""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            # Auto-set output path
            base_name = os.path.splitext(filename)[0]
            self.output_path.set(f"{base_name}_clean.pdf")
            
    def browse_output(self):
        """Browse for output location."""
        filename = filedialog.asksaveasfilename(
            title="Save Clean PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            
    def process_pdf(self):
        """Process the PDF to remove watermark."""
        if not self.pdf_path.get():
            messagebox.showerror("Error", "Please select a PDF file")
            return
            
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify output path")
            return
        
        # Validate email if provided
        email_provided = self.email_recipient.get().strip()
        if email_provided:
            # Basic email validation
            email = self.email_recipient.get().strip()
            if "@" not in email or "." not in email:
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            
        # Disable button and show progress
        self.process_button.config(state="disabled")
        self.progress.start()
        self.status_label.config(text="Processing PDF...", foreground="blue")
        
        # Process in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._process_pdf_thread)
        thread.daemon = True
        thread.start()
        
    def _process_pdf_thread(self):
        """Process PDF in separate thread."""
        try:
            # Initialize processor
            pdf_processor = PDFProcessor()
            summary_text = ""
            
            # Summarize PDF if requested
            if self.summarize_pdf.get():
                summary_text = self._summarize_pdf_content(pdf_processor)
            
            # Remove watermarks using the hardcoded list
            clean_pdf_path = pdf_processor.remove_watermarks(
                self.pdf_path.get(),
                self.watermark_list
            )
            
            # Copy to output location
            import shutil
            shutil.copy2(clean_pdf_path, self.output_path.get())
            
            # Send email if provided
            email_sent = False
            email_provided = self.email_recipient.get().strip()
            if email_provided:
                print(f"📧 准备发送邮件，PDF文件路径: {self.output_path.get()}")
                email_sent = self._send_email(self.output_path.get(), summary_text)
            
            # Prepare success message
            success_msg = f"Success! Clean PDF saved to:\n{self.output_path.get()}"
            if self.summarize_pdf.get() and summary_text:
                success_msg += f"\n\nAI summary displayed in terminal above."
            elif self.summarize_pdf.get() and not summary_text:
                success_msg += f"\n\nAI summary failed - only PDF processed."
            if email_sent:
                success_msg += f"\n\n📧 Email sent successfully to: {self.email_recipient.get()}"
            
            # Update UI on main thread
            self.root.after(0, self._process_complete, True, success_msg)
                
        except Exception as e:
            self.root.after(0, self._process_complete, False, f"Error: {str(e)}")
            
    def _summarize_pdf_content(self, pdf_processor):
        """Extract text from PDF and summarize using ChatGPT."""
        try:
            print("\n" + "="*80)
            print("🤖 AI 正在分析PDF内容...")
            print("="*80)
            
            # Extract raw text
            raw_text = pdf_processor.extract_text(self.pdf_path.get())
            
            if not raw_text.strip():
                print("⚠️  警告: 无法从PDF中提取文本内容")
                return ""
            
            # Initialize LLM summarizer
            summarizer = LLMSummarizer()
            
            # Get AI summary (LLM will print which service it's using)
            result = summarizer.summarize_pdf_content(raw_text)
            
            # Handle tuple return (summary, llm_name)
            if isinstance(result, tuple):
                summary, llm_name = result
            else:
                summary, llm_name = result, "Unknown"
            
            # Display summary in terminal if available
            if summary:
                print("\n" + "="*80)
                print(f"📋 AI 智能总结 ({llm_name})")
                print("="*80)
                print(summary)
                print("="*80)
                print("✅ 总结完成！")
                print("="*80 + "\n")
            
            return summary
            
        except Exception as e:
            print(f"\n❌ 总结过程中出现错误: {str(e)}")
            print("💡 提示: 请检查网络连接和Google Gemini API密钥")
            return ""
    
    def _send_email(self, pdf_path, summary_text):
        """Send email with PDF attachment and summary."""
        try:
            print("\n" + "="*80)
            print("📧 正在发送邮件...")
            print("="*80)
            
            # Initialize email sender
            email_sender = EmailSender()
            
            # Get original filename with .pdf extension
            original_filename = os.path.basename(self.pdf_path.get())
            
            # Send email
            success = email_sender.send_pdf_summary_email(
                recipient_email=self.email_recipient.get().strip(),
                pdf_path=pdf_path,
                summary_text=summary_text,
                original_filename=original_filename
            )
            
            if success:
                print("✅ 邮件发送成功！")
                return True
            else:
                print("❌ 邮件发送失败！")
                return False
                
        except Exception as e:
            print(f"❌ 邮件发送过程中出现错误: {str(e)}")
            return False
            
    def _process_complete(self, success, message):
        """Handle process completion."""
        self.progress.stop()
        self.process_button.config(state="normal")
        
        if success:
            self.status_label.config(text="Processing completed successfully!", foreground="green")
            messagebox.showinfo("Success", message)
        else:
            self.status_label.config(text="Processing failed", foreground="red")
            messagebox.showerror("Error", message)

def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    
    # Set window icon (optional)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    app = GTJAReportProcessor(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
