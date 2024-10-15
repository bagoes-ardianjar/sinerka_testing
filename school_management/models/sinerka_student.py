from odoo import models, fields,api, _

class sinerka_student(models.Model):
    _name = 'sinerka.student'
    _description = 'Student Management'

    @api.model
    def create(self, vals):
        res = super(sinerka_student, self).create(vals)
        for rec in res:
            seq = self.env['ir.sequence'].next_by_code('sinerka.student') or 'New'
            rec.nis = seq
        return res

    name = fields.Char(string='Nama', required=True)
    nis = fields.Char(string='NIS', default='New')
    age = fields.Integer(string='Umur')
    student_address = fields.Text(string='Alamat')
    is_active = fields.Boolean(string='Active', default=True)
    class_ids = fields.Many2many('school.class', string='Classes')