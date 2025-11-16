# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2025 tmistones.com
#
###################################################################################


from collections import defaultdict

from odoo.addons.hr_recruitment.models.hr_applicant import AVAILABLE_PRIORITIES

from odoo import api, models, fields, SUPERUSER_ID, tools, _
from odoo.exceptions import UserError
from odoo.osv import expression


class HrCandidate(models.Model):

    _inherit = 'hr.candidate'

    brief_introduction = fields.Text( string ='Brief introduction')
    gpa_score = fields.Char(string='GPA Score',  help="GPA score of the candidate")
    experience = fields.Html(string='Experience', help="Experience of the candidate")
    projects = fields.Html(string='Projects', help="Projects the candidate has worked on")
    interests = fields.Text(string='Interests', help="Interests of the candidate")
    github_link = fields.Char(string='GitHub Link', help="GitHub profile link of the candidate")
    education = fields.Html(string='Education', help="Education background of the candidate")

    experience_years = fields.Integer(string='Experience Years')
    best_skill = fields.Char(string='Best Skill', help="Best skill of the candidate")

    # Sẽ bỏ trong tương lai
    candidate_type = fields.Selection([('tester', 'Tester'),('dev', 'Developer'), ('ba', 'Business Analyst')], string='Candidate Type', help="Type of the candidate")

    tm_candidate_skill = fields.One2many(comodel_name='import_pdf.candidate.skill',
                                         string='Skill list',
                                         inverse_name='candidate_id', help="Skills list of the candidate")

    language = fields.Char(string = 'Language', help="Language proficiency of the candidate")

    @api.depends('tm_candidate_skill.skill_id')
    def _compute_skill_id(self):
        for candidate in self:
            candidate.import_cv_skill_ids = candidate.tm_candidate_skill.mapped('skill_id')

    import_cv_skill_ids = fields.Many2many(
        comodel_name='hr.skill',
        relation='import_pdf_candidate_2_skill_rel', column1='candidate_id', column2='hr_skill_id',
        compute = '_compute_skill_id', store=True, readonly=False,
        string='Skills', help="Skills of the candidate",)
    

class TM_CandidateSkill(models.Model):
    _name = 'import_pdf.candidate.skill'
    _description = "Skill for a candidate"

    _rec_name = 'skill_type_id'

    candidate_id = fields.Many2one(
        comodel_name='hr.candidate',
        required=True,
        ondelete='cascade')
    skill_type_id = fields.Many2one(
        comodel_name='hr.skill.type',
        required=True)
    skill_id = fields.Many2many(
        comodel_name='hr.skill',
        relation='import_pdf_candidate_skill_rel', column1='candidate_id', column2='hr_skill_id',
        domain="[('skill_type_id', '=', skill_type_id)]",
        readonly=False)