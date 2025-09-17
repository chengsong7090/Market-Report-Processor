"""
PDF Processing Module

Handles PDF operations including:
- Text extraction
- Watermark removal
- PDF creation and manipulation
"""

import os
import fitz  # PyMuPDF
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from pathlib import Path
import tempfile

class PDFProcessor:
    """Handles PDF processing operations."""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def extract_text(self, pdf_path):
        """Extract text content from PDF for summarization."""
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            
            doc.close()
            return text_content
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")
    
    def remove_watermark(self, pdf_path, watermark_text):
        """Remove watermark from PDF using multiple techniques."""
        try:
            # Method 1: Try direct PDF editing
            clean_path = self._remove_watermark_direct(pdf_path, watermark_text)
            if clean_path:
                return clean_path
            
            # Method 2: Convert to images, process, and recreate PDF
            print("Direct removal failed, trying image-based approach...")
            return self._remove_watermark_via_images(pdf_path, watermark_text)
            
        except Exception as e:
            raise Exception(f"Error removing watermark: {str(e)}")
    
    def remove_watermarks(self, pdf_path, watermark_list):
        """Remove multiple watermarks from PDF using the list of watermark texts."""
        try:
            print(f"🔍 检测到 {len(watermark_list)} 个水印模式:")
            for i, watermark in enumerate(watermark_list, 1):
                print(f"   {i}. {watermark}")
            
            # Method 1: Try direct PDF editing for all watermarks
            clean_path = self._remove_watermarks_direct(pdf_path, watermark_list)
            if clean_path:
                return clean_path
            
            # Method 2: Convert to images, process, and recreate PDF
            print("直接移除失败，尝试基于图像的方法...")
            return self._remove_watermarks_via_images(pdf_path, watermark_list)
            
        except Exception as e:
            raise Exception(f"Error removing watermarks: {str(e)}")
    
    def _remove_watermarks_direct(self, pdf_path, watermark_list):
        """Try to remove multiple watermarks by direct PDF manipulation."""
        try:
            doc = fitz.open(pdf_path)
            modified = False
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Check each watermark in the list
                for watermark_text in watermark_list:
                    # Get text instances for this watermark
                    text_instances = page.search_for(watermark_text)
                    
                    if text_instances:
                        print(f"✅ 在页面 {page_num + 1} 找到水印: {watermark_text}")
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
                # Create output path in temp directory to avoid permission issues
                import tempfile
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(pdf_path)
                output_path = os.path.join(temp_dir, filename.replace('.pdf', '_clean.pdf'))
                doc.save(output_path)
                doc.close()
                print("✅ 水印移除成功 (直接方法)")
                return output_path
            else:
                doc.close()
                print("⚠️  未找到任何水印文本")
                return None
                
        except Exception as e:
            print(f"直接移除失败: {str(e)}")
            return None
    
    def _remove_watermarks_via_images(self, pdf_path, watermark_list):
        """Remove multiple watermarks by converting to images, processing, and recreating PDF."""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            processed_images = []
            
            for img in images:
                # Convert PIL image to OpenCV format
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                # Process image to remove all watermarks
                processed_img = self._remove_watermarks_from_image(img_cv, watermark_list)
                
                # Convert back to PIL
                processed_pil = Image.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
                processed_images.append(processed_pil)
            
            # Save as new PDF in temp directory
            import tempfile
            temp_dir = tempfile.gettempdir()
            filename = os.path.basename(pdf_path)
            output_path = os.path.join(temp_dir, filename.replace('.pdf', '_clean.pdf'))
            processed_images[0].save(
                output_path, 
                "PDF", 
                resolution=300.0, 
                save_all=True, 
                append_images=processed_images[1:]
            )
            
            print("✅ 水印移除成功 (图像方法)")
            return output_path
            
        except Exception as e:
            raise Exception(f"Image-based removal failed: {str(e)}")
    
    def _remove_watermarks_from_image(self, img, watermark_list):
        """Remove multiple watermarks from a single image using OpenCV."""
        try:
            # Convert to grayscale for text detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            # Use morphological operations to detect text regions
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            dilated = cv2.dilate(binary, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process each contour
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if this might be a watermark area (left side of image)
                if (x < img.shape[1] * 0.4 and  # Left side
                    h < 60 and h > 10 and  # Reasonable height for text
                    w > 50 and w < 400):  # Reasonable width for watermark text
                    
                    # Extract region
                    roi = img[y:y+h, x:x+w]
                    
                    # Check if this region contains any of the watermark texts
                    if self._is_watermark_region_multi(roi, watermark_list):
                        # Fill with white, extending slightly beyond the detected area
                        cv2.rectangle(img, 
                                    (max(0, x-5), max(0, y-5)), 
                                    (min(img.shape[1], x+w+5), min(img.shape[0], y+h+5)), 
                                    (255, 255, 255), -1)
            
            return img
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return img
    
    def _is_watermark_region_multi(self, roi, watermark_list):
        """Check if a region likely contains any of the watermark texts."""
        # This is a simplified check - in practice, you'd use OCR
        # For now, we'll check based on region characteristics
        if roi.shape[0] < 20 and roi.shape[1] < 200:
            return True
        return False
    
    def _remove_watermark_direct(self, pdf_path, watermark_text):
        """Try to remove watermark by direct PDF manipulation."""
        try:
            doc = fitz.open(pdf_path)
            modified = False
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get text instances
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
                # Create output path in temp directory to avoid permission issues
                import tempfile
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(pdf_path)
                output_path = os.path.join(temp_dir, filename.replace('.pdf', '_clean.pdf'))
                doc.save(output_path)
                doc.close()
                return output_path
            else:
                doc.close()
                return None
                
        except Exception as e:
            print(f"Direct removal failed: {str(e)}")
            return None
    
    def _remove_watermark_via_images(self, pdf_path, watermark_text):
        """Remove watermark by converting to images, processing, and recreating PDF."""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            processed_images = []
            
            for img in images:
                # Convert PIL image to OpenCV format
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                # Process image to remove watermark
                processed_img = self._remove_watermark_from_image(img_cv, watermark_text)
                
                # Convert back to PIL
                processed_pil = Image.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
                processed_images.append(processed_pil)
            
            # Save as new PDF in temp directory
            import tempfile
            temp_dir = tempfile.gettempdir()
            filename = os.path.basename(pdf_path)
            output_path = os.path.join(temp_dir, filename.replace('.pdf', '_clean.pdf'))
            processed_images[0].save(
                output_path, 
                "PDF", 
                resolution=300.0, 
                save_all=True, 
                append_images=processed_images[1:]
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Image-based removal failed: {str(e)}")
    
    def _remove_watermark_from_image(self, img, watermark_text):
        """Remove watermark from a single image using OpenCV."""
        try:
            # Convert to grayscale for text detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            # Use morphological operations to detect text regions
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            dilated = cv2.dilate(binary, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process each contour
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if this might be the watermark area (left side of image)
                # More specific criteria for the watermark
                if (x < img.shape[1] * 0.4 and  # Left side
                    h < 60 and h > 10 and  # Reasonable height for text
                    w > 50 and w < 400):  # Reasonable width for watermark text
                    
                    # Extract region
                    roi = img[y:y+h, x:x+w]
                    
                    # Check if this region contains text similar to watermark
                    if self._is_watermark_region(roi, watermark_text):
                        # Fill with white, extending slightly beyond the detected area
                        cv2.rectangle(img, 
                                    (max(0, x-5), max(0, y-5)), 
                                    (min(img.shape[1], x+w+5), min(img.shape[0], y+h+5)), 
                                    (255, 255, 255), -1)
            
            return img
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return img
    
    def _is_watermark_region(self, roi, watermark_text):
        """Check if a region likely contains the watermark text."""
        # This is a simplified check - in practice, you'd use OCR
        # For now, we'll check based on region characteristics
        if roi.shape[0] < 20 and roi.shape[1] < 200:
            return True
        return False
    
    def create_final_pdf(self, clean_pdf_path, chinese_summary, original_pdf_path):
        """Create final PDF with summary on first page and clean content."""
        try:
            # Create summary page
            summary_page = self._create_summary_page(chinese_summary)
            
            # Open clean PDF
            clean_doc = fitz.open(clean_pdf_path)
            
            # Create new document
            final_doc = fitz.open()
            
            # Add summary page first
            final_doc.insert_pdf(summary_page)
            
            # Add clean content pages
            final_doc.insert_pdf(clean_doc)
            
            # Save final PDF to temp directory first, then copy
            import tempfile
            temp_output = os.path.join(tempfile.gettempdir(), os.path.basename(original_pdf_path).replace('.pdf', '_processed.pdf'))
            final_doc.save(temp_output)
            
            # Copy to final location with timestamp to avoid conflicts
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = original_pdf_path.replace('.pdf', f'_processed_{timestamp}.pdf')
            import shutil
            shutil.copy2(temp_output, output_path)
            
            # Clean up
            clean_doc.close()
            final_doc.close()
            summary_page.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error creating final PDF: {str(e)}")
    
    def _create_summary_page(self, chinese_summary):
        """Create a PDF page with the Chinese summary using image-based approach."""
        try:
            # Create an image with Chinese text
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Create image (A4 size at 300 DPI)
            width, height = 2480, 3508  # A4 at 300 DPI
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a Chinese font, fallback to default
            try:
                # Try common Chinese fonts on Windows
                font_paths = [
                    'C:/Windows/Fonts/msyh.ttc',  # Microsoft YaHei
                    'C:/Windows/Fonts/simhei.ttf',  # SimHei
                    'C:/Windows/Fonts/simsun.ttc',  # SimSun
                    'C:/Windows/Fonts/arial.ttf'   # Arial fallback
                ]
                
                font_large = None
                font_small = None
                
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            font_large = ImageFont.truetype(font_path, 48)
                            font_small = ImageFont.truetype(font_path, 24)
                            break
                        except:
                            continue
                
                if font_large is None:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                    
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add title
            title = "PDF 摘要 (PDF Summary)"
            draw.text((100, 100), title, fill='black', font=font_large)
            
            # Add summary content with proper text wrapping
            y_position = 200
            line_height = 40
            max_width = width - 200
            
            # Split summary into lines and wrap text
            lines = chinese_summary.split('\n')
            for line in lines:
                if line.strip():
                    # Wrap long lines
                    wrapped_lines = textwrap.wrap(line, width=80)
                    for wrapped_line in wrapped_lines:
                        if y_position < height - 100:  # Leave margin at bottom
                            draw.text((100, y_position), wrapped_line, fill='black', font=font_small)
                            y_position += line_height
                        else:
                            break
                    y_position += 10  # Extra space between paragraphs
                else:
                    y_position += 20  # Space for empty lines
            
            # Convert image to PDF
            img_path = os.path.join(self.temp_dir, 'summary_page.png')
            img.save(img_path, 'PNG')
            
            # Create PDF from image
            doc = fitz.open()
            page = doc.new_page(width=595, height=842)  # A4 size
            
            # Insert image
            rect = fitz.Rect(0, 0, 595, 842)
            page.insert_image(rect, filename=img_path)
            
            return doc
            
        except Exception as e:
            raise Exception(f"Error creating summary page: {str(e)}")
    
    def cleanup(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
