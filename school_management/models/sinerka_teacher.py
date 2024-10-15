from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class sinerka_teacher(models.Model):
    _name = 'sinerka.teacher'
    _description = 'Teacher Management'

    @api.model
    def create(self, vals):
        res = super(sinerka_teacher, self).create(vals)
        for rec in res:
            seq = self.env['ir.sequence'].next_by_code('sinerka.teacher') or 'New'
            rec.nip = seq
        return res

    @api.constrains('phone')
    def _check_unique_phone(self):
        for this in self:
            if this.phone:
                existing_teacher = self.search([('phone', '=', this.phone), ('id', '!=', this.id)], limit=1)
                if existing_teacher:
                    raise ValidationError("Nomor telepon %s sudah terdaftar untuk guru lain." % this.phone)

    @api.depends('teacher_line_ids.students_count')
    def _compute_total_students(self):
        for teacher in self:
            teacher.total_students = sum(line.students_count for line in teacher.teacher_line_ids)

    name = fields.Char(string='Nama', required=True)
    nip = fields.Char(string='NIP', default='New')
    address = fields.Text(string='Alamat')
    phone = fields.Char(string='No. Hp')
    total_students = fields.Integer(string='Total Siswa', compute='_compute_total_students', store=True)
    teacher_line_ids = fields.One2many('sinerka.teacher.line', 'teacher_id', string='Class Lines')

class sinerka_teacher_line(models.Model):
    _name = 'sinerka.teacher.line'
    _description = 'Teacher Line (relasi guru dan kelas)'

    @api.depends('class_id.class_line_ids')
    def _compute_students_count(self):
        for line in self:
            line.students_count = len(line.class_id.class_line_ids)

    def open_student_management_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sinerka.teacher.student.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('school_management.sinerka_teacher_student_wizard_form_view').id,
            'target': 'new',
            'context': {
                'active_id': self.id,
                'class_id': self.class_id.id
            },
        }

    class_id = fields.Many2one('sinerka.class', string='Kelas', required=True)
    teacher_id = fields.Many2one('sinerka.teacher', string='Guru')
    students_count = fields.Integer(string='Jumlah Siswa di Kelas', compute='_compute_students_count', store=True)

class sinerka_teacher_student_wizard(models.TransientModel):
    _name = 'sinerka.teacher.student.wizard'
    _description = 'Wizard untuk Mengelola Siswa di Kelas'

    student_ids = fields.Many2many('sinerka.student', string='Students', required=True)
    is_active = fields.Boolean(string='Is Active')

    @api.model
    def default_get(self, fields):
        res = super(sinerka_teacher_student_wizard, self).default_get(fields)
        class_id = self.env.context.get('class_id')
        if class_id:
            students_in_class = self.env['sinerka.class.line'].search([('class_id', '=', class_id)])
            res.update({
                'student_ids': [(6, 0, students_in_class.mapped('student_id').ids)]
            })
        return res

    def action_update_status(self):
        for wizard in self:
            for student in wizard.student_ids:
                student.is_active = student.is_active

class TeacherReport(models.AbstractModel):
    _name = 'report.school_management.report_teacher_student'
    _description = 'Teacher and Student List Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sinerka.teacher'].search([])
        teacher_class_lines = {}
        teacher_students = {}

        for teacher in docs:
            classes = teacher.teacher_line_ids.mapped('class_id')

            class_lines = []
            students_by_class = {}

            for cls in classes:
                class_line = cls
                students = cls.class_line_ids.mapped('student_id')
                students_by_class[class_line.id] = students
                class_lines.append(class_line)

            teacher_class_lines[teacher.id] = class_lines
            teacher_students[teacher.id] = students_by_class

        return {
            'doc_ids': docs.ids,
            'docs': docs,
            'teacher_class_lines': teacher_class_lines,
            'teacher_students': teacher_students,
        }