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
from src.wechat_summarizer import WeChatSummarizer

class GTJAReportProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("GTJA Report Processor")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Variables for single PDF processing
        self.pdf_path = tk.StringVar()
        
        # Variables for batch processing
        self.folder_path = tk.StringVar()
        
        # Hardcoded watermark list - will remove any of these watermarks if found
        self.watermark_list = [
            "For the exclusive use of DAPHNE.WOO@GTJAS.COM.HK",
            "本文件专供 Guotai Junan Investments (Hong Kong) Limited 的 Daisy Zhu 使用",
            "􀀄􀀅􀀆􀀇􀀈􀀅􀀆􀀉􀀃􀀊􀀋􀀅􀀃􀀌􀀃􀀍􀀎􀀃􀀏􀀋􀀐􀀑􀀒􀀓􀀐􀀑􀀔􀀕􀀖􀀗􀀈􀀘􀀓􀀏􀀋􀀙􀀓􀀚􀀛",
            "Prepared for - W: colin.li@gtjas.com.hk"
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
        """Setup the tabbed user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="GTJA Report Processor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Tab 1: Single PDF Processing
        self.single_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.single_tab, text="Single PDF Processing")
        self.setup_single_pdf_tab()
        
        # Tab 2: Batch Analysis
        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text="Batch Analysis (WeChat)")
        self.setup_batch_analysis_tab()
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def setup_single_pdf_tab(self):
        """Setup the single PDF processing tab."""
        # PDF File Selection
        ttk.Label(self.single_tab, text="Select PDF File:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        file_frame = ttk.Frame(self.single_tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=10)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.pdf_path, width=50)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Watermark Info (read-only display)
        watermark_info = ttk.Label(self.single_tab, text="Watermarks to remove: Pre-configured list (English & Chinese)", 
                                 foreground="blue", font=("Arial", 9))
        watermark_info.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(20, 5), padx=10)
        
        # Output Path
        ttk.Label(self.single_tab, text="Output Path:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5), padx=10)
        output_frame = ttk.Frame(self.single_tab)
        output_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=10)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1)
        
        # Summarize PDF Checkbox
        self.summarize_checkbox = ttk.Checkbutton(self.single_tab, text="Summarize PDF content with AI (Chinese)", 
                                                variable=self.summarize_pdf)
        self.summarize_checkbox.grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.W, padx=10)
        
        # Email Section
        email_frame = ttk.LabelFrame(self.single_tab, text="📧 Email (Optional)", padding=10)
        email_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)
        
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
        self.process_button = ttk.Button(self.single_tab, text="Process PDF", 
                                       command=self.process_pdf, style="Accent.TButton")
        self.process_button.grid(row=7, column=0, columnspan=2, pady=30, padx=10)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.single_tab, mode='indeterminate', length=400)
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15, padx=10)
        
        # Status Label
        self.status_label = ttk.Label(self.single_tab, text="Ready to process PDF", 
                                     foreground="green")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=10, padx=10)
        
        # Configure grid weights
        self.single_tab.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        email_frame.columnconfigure(1, weight=1)
        
    def setup_batch_analysis_tab(self):
        """Setup the batch analysis tab for WeChat summaries."""
        # Folder Selection
        ttk.Label(self.batch_tab, text="Select Folder with PDFs:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        folder_frame = ttk.Frame(self.batch_tab)
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=10)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1)
        
        # Info Label
        info_text = ("Batch analysis for WeChat sharing:\n"
                    "• Analyzes all PDFs in folder about one company\n"
                    "• Generates 300-character Chinese summaries\n"
                    "• Focuses on buy/sell recommendations and key data")
        info_label = ttk.Label(self.batch_tab, text=info_text, 
                              foreground="blue", font=("Arial", 9), justify=tk.LEFT)
        info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(20, 5), padx=10)
        
        # Analyze Button
        self.batch_button = ttk.Button(self.batch_tab, text="Analyze PDFs", 
                                     command=self.analyze_batch, style="Accent.TButton")
        self.batch_button.grid(row=3, column=0, columnspan=2, pady=20, padx=10)
        
        # Progress Bar for batch
        self.batch_progress = ttk.Progressbar(self.batch_tab, mode='indeterminate', length=400)
        self.batch_progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        # Results Text Area
        ttk.Label(self.batch_tab, text="Analysis Results:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5), padx=10)
        
        # Text area with scrollbar
        text_frame = ttk.Frame(self.batch_tab)
        text_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=10)
        
        self.results_text = tk.Text(text_frame, height=15, width=70, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Copy to Clipboard Button
        ttk.Button(self.batch_tab, text="Copy to Clipboard", 
                  command=self.copy_to_clipboard).grid(row=7, column=0, columnspan=2, pady=10, padx=10)
        
        # Configure grid weights
        self.batch_tab.columnconfigure(0, weight=1)
        self.batch_tab.rowconfigure(6, weight=1)
        folder_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
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
            
    def browse_folder(self):
        """Browse for folder containing PDFs."""
        folder = filedialog.askdirectory(
            title="Select Folder with PDFs"
        )
        if folder:
            self.folder_path.set(folder)
            
    def analyze_batch(self):
        """Analyze all PDFs in the selected folder."""
        if not self.folder_path.get():
            messagebox.showerror("Error", "Please select a folder containing PDFs.")
            return
            
        if not os.path.exists(self.folder_path.get()):
            messagebox.showerror("Error", "Selected folder does not exist.")
            return
            
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Start processing in separate thread
        self.batch_button.config(state='disabled')
        self.batch_progress.start()
        
        thread = threading.Thread(target=self._analyze_batch_thread)
        thread.daemon = True
        thread.start()
        
    def copy_to_clipboard(self):
        """Copy results to clipboard."""
        content = self.results_text.get(1.0, tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Success", "Results copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No results to copy.")
            
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
    
    def _analyze_batch_thread(self):
        """Analyze batch of PDFs in separate thread."""
        try:
            folder_path = self.folder_path.get()
            
            # Find all PDF files in the folder
            pdf_files = []
            for file in os.listdir(folder_path):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(folder_path, file))
            
            if not pdf_files:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "No PDF files found in the selected folder."))
                return
                
            # Initialize the WeChat summarizer
            wechat_summarizer = WeChatSummarizer()
            
            # Process each PDF
            all_summaries = []
            for i, pdf_path in enumerate(pdf_files):
                try:
                    # Update UI to show progress
                    filename = os.path.basename(pdf_path)
                    self.root.after(0, lambda f=filename: self.results_text.insert(tk.END, f"📄 正在分析: {f}\n"))
                    
                    # Extract text from PDF
                    pdf_processor = PDFProcessor()
                    raw_text = pdf_processor.extract_text(pdf_path)
                    
                    if raw_text.strip():
                        # Generate WeChat summary
                        summary = wechat_summarizer.generate_wechat_summary(raw_text, filename)
                        all_summaries.append(summary)
                        
                        # Update UI with individual summary
                        self.root.after(0, lambda s=summary: self.results_text.insert(tk.END, f"{s}\n{'='*50}\n\n"))
                    else:
                        self.root.after(0, lambda f=filename: self.results_text.insert(tk.END, f"⚠️ 无法从 {f} 提取文本\n\n"))
                        
                except Exception as e:
                    error_msg = f"❌ 处理 {os.path.basename(pdf_path)} 时出错: {str(e)}\n\n"
                    self.root.after(0, lambda msg=error_msg: self.results_text.insert(tk.END, msg))
            
            # Generate combined summary if multiple PDFs
            if len(all_summaries) > 1:
                combined_summary = wechat_summarizer.combine_summaries(all_summaries)
                self.root.after(0, lambda: self.results_text.insert(tk.END, f"\n{'='*60}\n📋 综合总结 (适用于微信分享):\n{'='*60}\n\n{combined_summary}\n"))
            
            # Update UI completion
            self.root.after(0, lambda: self.results_text.insert(tk.END, f"\n✅ 批量分析完成! 共处理 {len(pdf_files)} 个PDF文件。\n"))
            
        except Exception as e:
            error_msg = f"❌ 批量分析出错: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            # Re-enable button and stop progress
            self.root.after(0, lambda: self.batch_button.config(state='normal'))
            self.root.after(0, lambda: self.batch_progress.stop())
    
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
