#!/usr/bin/env python3
"""
PDF Watermark Remover - Small GUI Application

A lightweight GUI application that removes watermarks from PDF files using only PyMuPDF.
This version is much smaller as it doesn't include OpenCV.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import fitz  # PyMuPDF
import tempfile
import shutil
import datetime

class PDFWatermarkRemover:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Watermark Remover")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.watermark_text = tk.StringVar(value="For the exclusive use of DAPHNE.WOO@GTJAS.COM.HK")
        self.output_path = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF Watermark Remover", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # PDF File Selection
        ttk.Label(main_frame, text="Select PDF File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.pdf_path, width=50)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Watermark Text
        ttk.Label(main_frame, text="Watermark Text:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        self.watermark_entry = ttk.Entry(main_frame, textvariable=self.watermark_text, width=60)
        self.watermark_entry.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Output Path
        ttk.Label(main_frame, text="Output Path:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1)
        
        # Process Button
        self.process_button = ttk.Button(main_frame, text="Remove Watermark", 
                                       command=self.process_pdf, style="Accent.TButton")
        self.process_button.grid(row=7, column=0, columnspan=2, pady=30)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="Ready to process PDF", 
                                     foreground="green")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        
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
            
        if not self.watermark_text.get():
            messagebox.showerror("Error", "Please enter watermark text")
            return
            
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify output path")
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
            # Remove watermark using PyMuPDF only
            clean_pdf_path = self._remove_watermark_pymupdf(
                self.pdf_path.get(),
                self.watermark_text.get()
            )
            
            # Copy to output location
            shutil.copy2(clean_pdf_path, self.output_path.get())
            
            # Update UI on main thread
            self.root.after(0, self._process_complete, True, f"Success! Clean PDF saved to:\n{self.output_path.get()}")
            
        except Exception as e:
            self.root.after(0, self._process_complete, False, f"Error: {str(e)}")
            
    def _remove_watermark_pymupdf(self, pdf_path, watermark_text):
        """Remove watermark using PyMuPDF only (no OpenCV)."""
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            modified = False
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Search for watermark text
                text_instances = page.search_for(watermark_text)
                
                if text_instances:
                    # Add white rectangles over watermark text
                    for inst in text_instances:
                        rect = fitz.Rect(inst)
                        # Extend rectangle slightly to cover watermark
                        rect.x0 -= 5
                        rect.y0 -= 2
                        rect.x1 += 5
                        rect.y1 += 2
                        
                        # Add white rectangle
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()
                        modified = True
            
            if modified:
                # Save to temp file
                temp_dir = tempfile.gettempdir()
                temp_filename = os.path.basename(pdf_path).replace('.pdf', '_clean_temp.pdf')
                temp_path = os.path.join(temp_dir, temp_filename)
                doc.save(temp_path)
                doc.close()
                return temp_path
            else:
                doc.close()
                # If no watermark found, just copy original
                temp_dir = tempfile.gettempdir()
                temp_filename = os.path.basename(pdf_path).replace('.pdf', '_clean_temp.pdf')
                temp_path = os.path.join(temp_dir, temp_filename)
                shutil.copy2(pdf_path, temp_path)
                return temp_path
                
        except Exception as e:
            raise Exception(f"Error removing watermark: {str(e)}")
            
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
    
    app = PDFWatermarkRemover(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
