# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2025 tmistones.com
#
###################################################################################



import base64
import time
from odoo import http
from odoo.http import request
import io
from PyPDF2 import PdfReader
import json
import logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

class DirectoryUploadController(http.Controller):

    @http.route("/upload_directory", type="http", auth="user", methods=["POST"], csrf=False)
    def upload_directory(self, **kwargs):
        uploaded_files = request.httprequest.files.getlist("files[]")
        _logger.info("Upload file ------  %s", uploaded_files)
        for storage in uploaded_files:
            filename = storage.filename
            _logger.info("Upload file filename------  %s", filename)

            if filename and filename.lower().endswith('.pdf'):
                file_content = storage.read()

                attachment = request.env['ir.attachment'].sudo().create({
                    'name': filename,
                    'type': 'binary',
                    'datas': base64.b64encode(file_content).decode('utf-8', errors='ignore'),
                    'mimetype': 'application/pdf',
                    'processing': True
                })

        request.cr.commit()
        val = {'status': "OK", 'time': len(uploaded_files)+3}
        return json.dumps(val)

    # @http.route("/upload_directory", type="http", auth="user", methods=["POST"], csrf=False)
    # def upload_directory(self, **kwargs):
    #     uploaded_files = request.httprequest.files.getlist("files[]")
    #     _logger.info("Upload file ------  %s", uploaded_files)
    #     for storage in uploaded_files:
    #         filename = storage.filename
    #         _logger.info("Upload file filename------  %s", filename)
    #
    #         if filename and filename.lower().endswith('.pdf'):
    #             file_content = storage.read()
    #             # pdf_data = base64.b64decode(file_content)
    #             pdf_file = io.BytesIO(file_content)
    #             reader = PdfReader(pdf_file)
    #             text = ""
    #             for page in reader.pages:
    #                 text += page.extract_text() or ""
    #             _logger.info(f"Extracted text from {filename}, length {len(text)}")
    #
    #             if len(text) < 100:
    #                 _logger.error(f"No text extracted from {filename}")
    #                 _logger.error(f"Text extracted {text}")
    #                 _logger.error(f"Không thể trích xuất văn bản từ file pdf (file ảnh) {filename}")
    #                 continue
    #
    #             candidate, last_filename = request.env['candidate.import.wizard'].action_proceess_pdf(text,
    #                                                                                                   single_pdf_file=False)
    #             _logger.info("Xu ly pdf ứng viên tao %s: tên file %s", candidate, last_filename)
    #             # Xử lý file pdf đính kèm vào ứng viên
    #
    #             attachment = request.env['ir.attachment'].create({
    #                 'name': last_filename,
    #                 'type': 'binary',
    #                 'datas': base64.b64encode(file_content).decode('utf-8', errors='ignore'),
    #                 'res_model': 'hr.candidate',
    #                 'res_id': candidate.id,
    #                 'mimetype': 'application/pdf',
    #             })
    #             time.sleep(1)
    #
    #     return "OK"