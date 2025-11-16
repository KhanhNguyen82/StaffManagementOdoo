# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2025 tmistones.com
#
###################################################################################


import warnings

warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,

)

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError
import json
import base64
import io
import PyPDF2
from PyPDF2 import PdfReader
import openai
from typing import Dict, Any
import time
import tempfile
import os
import zipfile
import rarfile

import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


OPENAI_API_KEY=""
BASE_URL = "https://api.openai.com/v1/"

openai.api_key = OPENAI_API_KEY
#
# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a CV parser."},
#         {"role": "user", "content": "Parse this CV: ..."}
#     ]
# )



template_json = """
{
  "Personal Information": {
    "Full Name": "",
    "Job Title": "",
    "Date of Birth": "",
    "Gender": "",
    "ID Card Number": "",
    "Phone Number": "",
    "Email": "",
    "Linkedin": "",
    "GitHub": "",
    "Website": "",
    "Address": ""
  },
  "Brief introduction": "",
  "Objective": [
    {
      "Duration": "",
      "Description": ""
    }
  ],
  "Education": {
    "Period": "",
    "University": "",
    "Major": "",
    "GPA score": ""
  },
  "Work Experience": [
    {
      "Period": "",
      "Company": "",
      "job title": "",
      "Responsibilities": []
    }
  ],
  "Projects": [
    {
      "Project Name": "",
      "Description": "",
      "role": [],
      "Duration": "",
    }
  ],
  "Candidate Type": "",
  "Skills": [{
    "Skill Type": "",
    "Skills": []
    }],
  "Best Skill": "",
  "Product kind": "",
  "Certificates": [],
  "Languages": "",
  "Interests": "",
  "Experience Years": 0
}
"""


class CandidateImportWizard(models.TransientModel):
    _name = 'candidate.import.wizard'
    _description = 'Candidate PDF Upload Wizard'




    pdf_file = fields.Binary(string="PDF File")
    filename = fields.Char("Tên tệp")
    zip_file = fields.Binary(string="Zip file")
    filename_2 = fields.Char("Zip file name")


    def extract_text_from_pdf(self,pdf_file):
        """Extract text content from PDF file"""
        text = ""
        try:
            _logger.info(f"Starting text extraction from PDF...")

            # Decode base64
            pdf_data = base64.b64decode(pdf_file)
            pdf_file = io.BytesIO(pdf_data)

            # Đọc PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            page_count = len(pdf_reader.pages)
            _logger.info(f"PDF has {page_count} pages")
            for i, page in enumerate(pdf_reader.pages):
                _logger.debug(f"Extracting text from page {i + 1}/{page_count}")
                page_text = page.extract_text()
                text += page_text + "\n"
            _logger.info(f"Text extraction complete. Extracted {len(text)} characters")
            _logger.info("Extracted text from PDF: %s", text)  # Log first 200 characters for brevity
            return text
        except Exception as e:
            _logger.error(f"Failed to extract text from PDF: %s", str(e), exc_info=True)
            raise UserError('Lỗi chuyển đổi tệp PDF sang văn bản: %s' % str(e))

    def generate_json_from_text(self, cv_text: str):
        """Send CV text to OpenAI and get JSON response"""
        try:
            _logger.info(f"Sending CV text to OpenAI API (length: {len(cv_text)} chars)")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert CV analyzer. Extract the following information from a resume and return it in strict JSON format following exactly this template:\n\n{template_json}\n\nFor missing data, keep the key and use empty string, list, or object as appropriate. Do not explain or add comments.I want to know if this candidate is: Tester, Business Analyst or Developer, if the candidate is not in the above group you can return an empty string. Try to find out what the candidate's best skills are?. If the candidate has no skills, return an empty list. If the candidate has no experience, return an empty list. If the candidate has no projects, return an empty list. If the candidate has no education, return an empty object with Period, University, Major and GPA score as keys. If the candidate has no languages, return an empty string. If the candidate is a developer, find out what kind of product the candidate has an advantage in, such as web (abbreviated as W), mobile (abbreviated as M) , API (abbreviated as API), AI ((abbreviated as AI), machine learning ((abbreviated as ML), IoT, etc, return this information in the Product kind key. If the candidate is a tester, return Product kind key is M if Manual test, A if Automatic test. Return only valid JSON. No markdown, no extra text. Output must begin with '{' and end with '}'."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this CV text and return the structured information as JSON:\n\n{cv_text}"
                    }
                ],

            )

            _logger.debug(f"OpenAI API response: %s", response)  # Log the full response for debugging
            _logger.info("Received response from OpenAI API")

            # Parse the JSON string into a Python dictionary json.dumps
            content = response.choices[0].message.content
            if not content:
                _logger.info("OpenAI API returned empty content")
                return {}
            #content = json.dumps(content_1, ensure_ascii=False)
            _logger.error(f"OpenAI return xxx------- : {content}")
            json_data = json.loads(content.replace("```json", "").replace("```","").replace("\0","").replace("'",""))  # Clean up
            #json_data = json.loads(content.replace("```json", ""))  # Clean up
            #content = response.choices[0].message.content
            # if isinstance(content, str):
            #     json_data = json.loads(content.replace("```json", "").replace("```",""))
            # else:
            #     json_data = content

            _logger.info(f"Successfully parsed JSON response with {len(json_data)} top-level fields")
            return json_data

            #parsed = response.choices[0].message.parsed
            #content = json.dumps(parsed, ensure_ascii=False)
            #json_data = json.loads(content)

        except Exception as e:
            _logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            #_logger.error(f"OpenAI return ------- : {content}")

            #raise Exception(f"OpenAI API error: {str(e)}")
            return {}

    def convert_experience_to_html(self, experience: list[Any]) -> str:
        """Convert experience list to HTML format"""
        if not experience:
            return "<p>No work experience provided.</p>"
        html = "<ul>"
        for exp in experience:
            html += f"<li><strong>{exp.get('job title', '')}</strong> at {exp.get('Company', '')} ({exp.get('Period', '')})<br/>"
            if 'Responsibilities' in exp:
                html += "Responsibilities<ul>"
                for responsibility in exp['Responsibilities']:
                    html += f"<li>{responsibility}</li>"
                html += "</ul>"

            html += f"</li>"
        html += "</ul>"
        return html
    def convert_projects_to_html(self, experience: list[Any]) -> str:
        """Convert projects list to HTML format"""
        if not experience:
            return "<p>No projects provided.</p>"
        html = "<ul>"
        for exp in experience:
            html += f"<li><strong>{exp.get('Project Name', '')}</strong><br/>"
            html += f"<p>{exp.get('Description', '')}</p>"
            if 'role' in exp:
                if exp['role']:
                    html += "<p>Role:</p><ul>"
                    for role in exp['role']:
                        html += f"<li>{role}</li>"
                    html += "</ul>"
            if 'Duration' in exp:
                if exp['Duration']:
                    html += f"<p>Duration: {exp.get('Duration', '')}</p>"

            html += f"</li>"
        html += "</ul>"
        return html
    def convert_education_to_html(self, experience: Dict[str,Any]) -> str:
        """Convert education list to HTML format"""
        if not experience:
            return "<p>No education information provided.</p>"
        html = ""
        html += f"<p><strong>{experience.get('Major', '')}</strong> at {experience.get('University', '')} ({experience.get('Period', '')})<br/>"
        if 'GPA score' in experience:
            html += f"GPA Score: {experience.get('GPA score', '')}</p>"
        return html

    def convert_lang_to_string(self, lang) -> str:
        if not lang:
            return "No language information provided."
        return lang

    def action_import_one_pdf(self):
        if self.pdf_file:
            text = self.extract_text_from_pdf(self.pdf_file, )
            if len(text) < 100 or len(text) > 16550:
                _logger.error(f"No text extracted from {self.filename}")
                #_logger.error(f"Text extracted {text}")
                raise UserError(f"Unable to extract text from file {self.filename}. (This is probably an image file converted to PDF.) This module does not support OCR yet.")


            candidate, last_filename = self.action_proceess_pdf(text, single_pdf_file=True)
            if candidate==None and last_filename==None:
                raise UserError(f"Failed to process PDF file: OpenAI API not enought quota or the file PDF is not the type that can be converted to text (image)  {self.filename} !.")
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hr.candidate',
                'view_mode': 'form',
                'res_id': candidate.id,
                'target': 'current',
            }


    def action_proceess_pdf(self, text_string, single_pdf_file=True):
        #Cần tạo mới 1 bản ghi hr.candidate từ tệp PDF được tải lên
        #Bước 1: Chuyển pdf thành text
        #Bước 2: Phân tich text, lấy tên và các thông tin liên quan  (Dùng API OpenAI hoặc các thư viện khác để phân tích nội dung PDF)
        #Bước 3: Tạo bản ghi hr.candidate mới với các thông tin đã phân tích
        #Buớc 4: Lưu tệp PDF và đổi tên theo luật định trước và gán thành tệp đính kèm của hồ sơ ứng viên

        if text_string:
            # Bước 2: Phân tich text, lấy tên và các thông tin liên quan  (Dùng API OpenAI hoặc các thư viện khác để phân tích nội dung PDF)

            json = self.generate_json_from_text(text_string)

            if not json:
                _logger.error("Failed to generate JSON from text")
                return None, None

            _logger.info("Generated JSON from text: %s", json)
            # Kiểm tra xem JSON có chứa thông tin cần thiết không

            vals_partner_id = {
                'name': json.get("Personal Information", {}).get("Full Name", 'Unknown'),
                'email': json.get("Personal Information", {}).get("Email"),
                'phone': json.get("Personal Information", {}).get("Phone Number"),
            }
            partner = self.env['res.partner'].create(vals_partner_id)
            if not partner:
                _logger.error("Failed to create partner from JSON data")
                raise UserError('Failed to create partner from JSON data')
            candidate_type = json.get("Candidate Type", '')

            if candidate_type == 'Tester':
                candidate_type_select = 'tester'
            elif candidate_type == 'Business Analyst':
                candidate_type_select = 'ba'
            elif candidate_type == 'Developer':
                candidate_type_select = 'dev'
            else:
                candidate_type_select = ''



            vals_candidate = {
                'partner_name': json.get("Personal Information", {}).get("Full Name", 'Unknown'),
                'partner_id': partner.id,
                'github_link': json.get("Personal Information", {}).get("GitHub", ''),
                'linkedin_profile': json.get("Personal Information", {}).get("Linkedin", ''),
                'gpa_score': json.get("Education", {}).get("GPA score", '') or 0.0,
                'experience': self.convert_experience_to_html(json.get("Work Experience", [])),
                'projects': self.convert_projects_to_html(json.get("Projects", [])),
                'education': self.convert_education_to_html(json.get("Education", [])),
                'interests': json.get("Interests", ''),
                'brief_introduction': json.get("Brief introduction", ''),
                'best_skill': json.get("Best Skill", ''),
                'candidate_type': candidate_type_select,
                'experience_years': json.get("Experience Years", 0),
                'language': self.convert_lang_to_string(json.get("Languages", '')),
                'user_id': False,

                # 'education_ids': [(0, 0, {
                #     'degree': edu.get('degree', ''),
                #     'institution': edu.get('institution', ''),
                #     'start_date': edu.get('start_date', ''),
                #     'end_date': edu.get('end_date', '')
                # }) for edu in json.get('Education', [])],
                # 'work_experience_ids': [(0, 0, {
                #     'job_title': exp.get('job_title', ''),
                #     'company_name': exp.get('company_name', ''),
                #     'start_date': exp.get('start_date', ''),
                #     'end_date': exp.get('end_date', '')
                # }) for exp in json.get('experience', [])],
                # Thêm các trường khác nếu cần
            }
            #_logger.info("Creating candidate with values: %s", vals_candidate)
            # Bước 3: Tạo bản ghi hr.candidate mới với các thông tin đã phân tích
            candidate = self.env['hr.candidate'].create(vals_candidate)
            #Bước 3.5: Cập nhật skill
            # ---Xử lý skill types và skills trên DB chưa liên quan đến ứng viên
            skill_list = json.get('Skills', [])
            skill_type_model = self.env['hr.skill.type'].sudo()
            skill_model = self.env['hr.skill'].sudo()
            for skill_type in skill_list:
                skill_type_obj = skill_type_model.search([('name', '=', skill_type.get('Skill Type'))], limit=1)
                if not skill_type_obj:
                    # Nếu không tìm thấy, tạo mới skill type
                    skill_type_obj = skill_type_model.create({'name': skill_type.get('Skill Type')})
                    _logger.info("Created new skill type: %s", skill_type_obj.name)
                else:
                    _logger.info("Found existing skill type: %s", skill_type_obj.name)
                candidate_skill_obj = self.env['import_pdf.candidate.skill'].create({
                    'candidate_id': candidate.id,
                    'skill_type_id': skill_type_obj.id,

                })
                for skill in skill_type.get('Skills', []):
                    # Tạo hoặc cập nhật skill cho DB
                    skill_obj = skill_model.search([('name', '=', skill)], limit=1)
                    if not skill_obj:
                        skill_obj = skill_model.create({
                            'name': skill,
                            'skill_type_id': skill_type_obj.id,
                        })
                        _logger.info("Created new skill: %s", skill_obj.name)
                    else:
                        _logger.info("Found existing skill: %s", skill)
                    # Thêm skill vào candidate_skill_obj của ứng viên
                    candidate_skill_obj.skill_id = [(4, skill_obj.id)]

                _logger.info("Candidate skills created/updated successfully")
            # ---Xử lý skill types và skills trên DB chưa liên quan đến ứng viên

            # Cập nhật skill vào ứng viên
            # Buớc 4: Lưu tệp PDF và đổi tên theo luật định trước và gán thành tệp đính kèm của hồ sơ ứng viên
            # 4.1 Đặt tên file của ứng viên theo định dạng "Tên ứng viên - Ngày tháng năm - Loại ứng viên.pdf"
            #
            # dev_product_years_name_language
            # W_TranVanA_Python -> W: Web (tương tự A: API, M: Mobile, AI: AI...)
            # tester_A_5_TranVanA
            # ba_3_TranVanA
            #
            if candidate.candidate_type == 'dev':
                product_kind = json.get("Product kind", '').replace(' ', '_')
                best_skill = json.get("Best Skill", '').replace(' ', '_')
                last_filename = f"dev_{product_kind}_{candidate.partner_name.replace(' ', '_')}_{best_skill}.pdf"
            elif candidate.candidate_type == 'tester':
                years = json.get("Experience Years", 0)
                product_kind = json.get("Product kind", '').replace(' ', '_')
                last_filename = f"tester_{product_kind}_{years}_{candidate.partner_name.replace(' ', '_')}.pdf"
            elif candidate.candidate_type == 'ba':
                years = json.get("Experience Years", 0)
                last_filename = f"ba_{years}_{candidate.partner_name.replace(' ', '_')}.pdf"
            else:
                last_filename = f"other_{candidate.partner_name.replace(' ', '_')}.pdf"

            '''
            
            tên file của dev em đặt theo quy ước
            product_years_name_language
            product là sản phẩm mà dev có kinh nghiệm làm việc
            có thể là web ký hiệu W
            api ký hiệu là A
            mobile ký hiệu là M
            AI kỳ hiệu là AI
            có kinh nghiệm làm cả web và API thì ký hiệu là WA
            years là số năm kinh nghiệm
            name là tên của dev
            language là ngôn ngữ dev có kinh nghiệm nhất
            như java
            C
            thêm field để biết bạn này là tester hay dev hay ba
            quy tắc đặt tên file của tester là type_years_name
            type là A nghĩa là automation tester
            M là manual tester
            years là số năm kinh nghiệm
            name là tên người đó
            các vị trí khác thì chỉ cần year_name
            '''

        if text_string and single_pdf_file:
            attachment = self.env['ir.attachment'].create({
                'name': last_filename,
                'type': 'binary',
                'datas': self.pdf_file,
                'res_model': 'hr.candidate',
                'res_id':   candidate.id,
                'mimetype': 'application/pdf',
            })


        return candidate, last_filename


    def action_upload_zip_file_and_extraction(self):
        if not self.zip_file:
            raise UserError("Please select ZIP or RAR file.")

        # Tạo file tạm
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, self.filename_2)

        with open(tmp_path, "wb") as f:
            f.write(base64.b64decode(self.zip_file))

        extracted_files = []

        # Giải nén theo định dạng
        if self.filename_2.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(tmp_path, "r") as zf:
                    zf.extractall(tmp_dir)
                    all_files = zf.namelist()
                    # Lọc bỏ file rác __MACOSX/ và file ẩn bắt đầu bằng ._
                    extracted_files = [
                        f for f in all_files
                        if not (f.startswith("__MACOSX/") or f.startswith("._"))
                    ]
            except Exception as e:
                raise UserError("Unable to unpack ZIP: %s" % e)
        elif self.filename_2.lower().endswith(".rar"):
            try:
                with rarfile.RarFile(tmp_path, "r") as rf:
                    rf.extractall(tmp_dir)
                    all_files = rf.namelist()
                    extracted_files = [
                        f for f in all_files
                        if not (f.startswith("__MACOSX/") or f.startswith("._"))
                    ]
            except Exception as e:
                raise UserError("Unable to unpack RAR: %s" % e)

        else:
            raise UserError("Only ZIP or RAR format is supported.")

        _logger.info("Extracted valid files: %s", extracted_files)

        # Xử lý các file đã giải nén
        for file_name in extracted_files:
            _logger.info("Extracted_files file: %s", file_name)
            file_path = os.path.join(tmp_dir, file_name)
            if not os.path.isfile(file_path):
                _logger.warning("File not found: %s", file_path)
                continue
            try:
                with open(file_path, "rb") as f:
                    file_content = f.read()
                    if file_name and file_name.lower().endswith('.pdf'):
                        # Tạo attachment tạm thời và đánh dấu để xử lý
                        attachment = self.env['ir.attachment'].sudo().create({
                            'name': file_name,
                            'type': 'binary',
                            'datas': base64.b64encode(file_content).decode('utf-8', errors='ignore'),
                            'mimetype': 'application/pdf',
                            'processing': True
                        })

            except Exception as e:
                _logger.error("Can not read PDF %s: %s", file_name, e)
            #candidate = self.action_proceess_pdf(file_name)
        self.env.cr.commit()


        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'ZIP file Upload queued',
                'message': f'ZIP or RAR file has uploaded and extracted. The system is processing PDF files. '
                           f'Processing time estimated {(len(extracted_files)+3)} min, '
                           f'the results will be generated automatically.',
                'sticky': True,
                'type': 'success',
            }
        }




class CandidateImportWizard_2(models.TransientModel):
    _name = "candidate.import.wizard_2"
    _description = "Candidate Import Wizard"

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'wizard_ir_attachments_rel',  # bảng quan hệ
        'wizard_id',
        'attachment_id',
        string="PDF CV to import"
    )




    def choose_pdf_file(self):
        if not self.attachment_ids:
            raise UserError("Please upload at least one file.")

        for att in self.attachment_ids:
            # If the attachment is not stored yet, raise
            if not att.datas:
                # Could be user added via widget but not saved, skip or raise
                _logger.warning("Attachment %s has no data, skipping", att.name)
                continue
            # mark for processing (custom boolean field on ir.attachment)
            att.sudo().write({'processing': True})

            # Ensure DB commit so cron sees the flags immediately
        self.env.cr.commit()
        time_to_process = len(self.attachment_ids)+3  # Rough estimate: 1 min. per file
        # Return a notification to user immediately

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Upload queued',
                'message': f'The system is processing PDF files, please wait. '
                           f'Processing time about {time_to_process} min, '
                           f'the results will be generated automatically.',
                'sticky': True,
                'type': 'info',
            }
        }

    def choose_pdf_file_old(self):
        for attachment in self.attachment_ids:
            if attachment.mimetype != "application/pdf":

                # attachment.datas (base64)
                _logger.info(attachment.name)
                raise UserError(f"File {attachment.name} is not PDF.")
                # self.env['hr.candidate'].create({...})
            else:
                pdf_data = base64.b64decode(attachment.datas)
                pdf_file = io.BytesIO(pdf_data)
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                _logger.info(f"Extracted text from {attachment.name}, length {len(text)}")


                if len(text) < 100 or len(text) > 16500:
                    _logger.error(f"No text extracted from {attachment.name}")
                    #_logger.error(f"Text extracted {text}")
                    _logger.error(f"Unable to extract text from pdf file (image file) {attachment.name}")
                    continue

                # Gọi hàm xử lý của bạn
                candidate, last_filename = self.env['candidate.import.wizard'].action_proceess_pdf(text, single_pdf_file=False)
                _logger.error("Processing candidate pdf to create %s: file name %s", candidate, last_filename)
                # Xử lý file pdf đính kèm vào ứng viên

                attachment = self.env['ir.attachment'].create({
                    'name': last_filename,
                    'type': 'binary',
                    'datas': attachment.datas,
                    'res_model': 'hr.candidate',
                    'res_id': candidate.id,
                    'mimetype': 'application/pdf',
                })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.candidate',
            'view_mode': 'list,form',
            'target': 'current',
        }

class IrAttachmentProcessor(models.Model):
    _inherit = "ir.attachment"

    processing = fields.Boolean(string="Processing", default=False)
    process_fault = fields.Boolean(string="Process Fault", default=False)



    @api.model
    def _cron_process_pending_attachments(self, limit=6):
        """
        Cron job: pick up attachments with processing=True and process them.
        Limit param to avoid long runs.


        """

        def safe_extract_text_from_pdf(attachment):
            """
            Đọc file PDF từ attachment (ir.attachment)
            Trả về chuỗi text hoặc "" nếu lỗi / không có nội dung.
            """
            try:
                if not attachment.datas:
                    _logger.warning(f"[{attachment.name}] ⚠️ File không có dữ liệu.")
                    return ""

                # Giải mã base64
                try:
                    pdf_data = base64.b64decode(attachment.datas)
                except Exception as e:
                    _logger.error(f"[{attachment.name}] ❌ Không thể decode base64: {e}")
                    return ""

                # Kiểm tra header PDF
                if not pdf_data.startswith(b"%PDF"):
                    _logger.warning(f"[{attachment.name}] ⚠️ File không phải PDF hợp lệ.")
                    return ""

                pdf_file = io.BytesIO(pdf_data)

                try:
                    reader = PdfReader(pdf_file)
                except Exception as e:
                    _logger.error(f"[{attachment.name}] ❌ Lỗi khi đọc PDF: {e}")
                    return ""

                text = ""
                for page in reader.pages:
                    try:
                        extracted = page.extract_text() or ""
                        text += extracted
                    except Exception as e:
                        _logger.warning(f"[{attachment.name}] ⚠️ Không thể đọc 1 trang: {e}")

                text = text.strip()
                if not text:
                    _logger.warning(f"[{attachment.name}] ⚠️ PDF có thể là ảnh scan, không có văn bản.")
                else:
                    if len(text) > 16500:
                        _logger.warning(f"[{attachment.name}] ⚠️ Văn bản quá dài ({len(text)} ký tự).")
                    else:
                        _logger.info(f"[{attachment.name}] ✅ Trích xuất {len(text)} ký tự văn bản thành công.")

                return text

            except Exception as e:
                _logger.error(f"[{attachment.name}] ❌ Lỗi không xác định khi xử lý PDF: {e}")
                return ""


        _logger.info("cron_process_pending_attachments start, looking for attachments to process")
        # Find pending attachments (PDFs)
        pending = self.search(
            [('processing', '=', True), ('mimetype', '=', 'application/pdf'), ('process_fault', '=', False)],
            limit=limit,
            order='create_date asc'
        )
        if not pending:
            _logger.debug("No pending attachments found.")
            return True

        for attachment in pending:
            if attachment.mimetype != "application/pdf":
                _logger.info(attachment.name)
                _logger.debug(f"File {attachment.name} is not PDF type.")
                attachment.sudo().write({'processing': True, 'process_fault': True})
                continue
            else:
                text = safe_extract_text_from_pdf(attachment)

                # pdf_data = base64.b64decode(attachment.datas)
                # pdf_file = io.BytesIO(pdf_data)
                # reader = PdfReader(pdf_file)
                # text = ""
                # for page in reader.pages:
                #     text += page.extract_text() or ""
                # _logger.info(f"Extracted text from {attachment.name}, length {len(text)}")

                if not text or len(text) < 100 or len(text) > 16500:
                    _logger.error(f"No text extracted from {attachment.name}")
                    #_logger.error(f"Text extracted {text}")
                    _logger.error(f"Unable to extract text from pdf file (image file) {attachment.name}")
                    attachment.sudo().write({'processing': True, 'process_fault': True})
                    continue

                # Gọi hàm xử lý của bạn
                candidate, last_filename = self.env['candidate.import.wizard'].action_proceess_pdf(text, single_pdf_file=False)
                _logger.error("Processing candidate pdf to create %s: file name %s", candidate, last_filename)
                # Xử lý file pdf đính kèm vào ứng viên

                new_attachment = self.env['ir.attachment'].create({
                    'name': last_filename,
                    'type': 'binary',
                    'datas': attachment.datas,
                    'res_model': 'hr.candidate',
                    'res_id': candidate.id,
                    'mimetype': 'application/pdf',
                })
                attachment.sudo().write({'processing': False})
                _logger.info("Finished processing attachment %s", attachment.name)

        _logger.info("cron_process_pending_attachments finished")
        return True











