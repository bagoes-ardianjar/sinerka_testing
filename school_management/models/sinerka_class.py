from odoo import models, fields,api, _

class sinerka_class(models.Model):
    _name = 'sinerka.class'
    _description = 'Class Management'

    name = fields.Char(string='Class Name', required=True)
    subject = fields.Char(string='Subject')
    class_line_ids = fields.One2many('sinerka.class.line', 'class_id', string='Class Lines')

class sinerka_class_line(models.Model):
    _name = 'sinerka.class.line'
    _description = 'Daftar Siswa'

    @api.depends('student_id')
    def _get_nis(self):
        for this in self:
            if this.student_id:
                this.nis = this.student_id.nis
            else:
                this.nis = None

    class_id = fields.Many2one('sinerka.class', string='Class Id')
    student_id = fields.Many2one('sinerka.student', string='Student', required=True)
    nis = fields.Char(string='NIS', compute=_get_nis)