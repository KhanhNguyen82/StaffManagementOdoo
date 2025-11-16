# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2025 tmistones.com
#
###################################################################################

from odoo import models, fields




class MyDocument(models.Model):

    name = fields.Char("Document Name")

    _name = "import_pdf_cv.document"
    _description = "My Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _attachment = True  # Cho phép đính kèm nhiều file

    name = fields.Char("Document Name", required=True, tracking=True)
    description = fields.Text("Description")