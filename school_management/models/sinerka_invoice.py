from odoo import models, fields, api
from datetime import datetime

class sinerka_invoice(models.Model):
    _name = 'sinerka.invoice'
    _description = 'Student Invoice'

    def print_sinerka_invoice(self):
        return self.env.ref('school_management.action_report_print_sinerka_invoice').report_action(self)

    @api.model
    def create(self, vals):
        res = super(sinerka_invoice, self).create(vals)
        for rec in res:
            seq = self.env['ir.sequence'].next_by_code('sinerka.invoice') or 'New'
            rec.name = seq
        return res

    def action_mark_as_paid(self):
        for invoice in self:
            invoice.status = 'paid'

    @api.depends('student_id')
    def _compute_nis(self):
        for invoice in self:
            invoice.nis = invoice.student_id.nis

    @api.depends('student_id')
    def _compute_classes(self):
        for invoice in self:
            classes = self.env['sinerka.class.line'].search([('student_id', '=', invoice.student_id.id)])
            class_names = classes.mapped('class_id.name')
            invoice.class_ids = ', '.join(class_names)

    name = fields.Char(string='No. Transaksi', default='New')
    student_id = fields.Many2one('sinerka.student', string='Student', required=True)
    nis = fields.Char('NIS', compute='_compute_nis', store=True)
    class_ids = fields.Char('Classes', compute='_compute_classes', store=True)
    amount = fields.Float(string='Amount')
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.context_today)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid')
    ], string='Status', default='draft')
    description = fields.Text('Description')
    invoice_line_ids = fields.One2many('sinerka.invoice.line', 'invoice_id',string='Invoice Lines')
    total_amount = fields.Float('Total Amount', compute='_compute_total_amount')

    @api.depends('invoice_line_ids.amount')
    def _compute_total_amount(self):
        for invoice in self:
            invoice.total_amount = sum(invoice.invoice_line_ids.mapped('amount'))

class sinerka_invoice_line(models.Model):
    _name = 'sinerka.invoice.line'
    _description = 'Invoice Line for Sinerka Invoices'

    invoice_id = fields.Many2one('sinerka.invoice', string='Invoice')
    description = fields.Char('Description', required=True)
    amount = fields.Float('Amount', required=True)

class SinerkaInvoiceScheduler(models.Model):
    _name = 'sinerka.invoice.scheduler'

    def create_monthly_invoices(self):
        current_date = datetime.now()
        month = current_date.strftime('%B')
        year = current_date.year

        biaya_pendidikan = 50000
        biaya_daftar_ulang = 975000

        students = self.env['sinerka.student'].search([])

        for student in students:
            invoice_data = {
                'student_id': student.id,
                'invoice_date': current_date,
                'description': f'Biaya Penyelenggaraan Pendidikan - {month} {year} dan Biaya Daftar Ulang',
                'status': 'draft',
            }

            invoice = self.env['sinerka.invoice'].create(invoice_data)

            self.env['sinerka.invoice.line'].create({
                'invoice_id': invoice.id,
                'description': f'Biaya Penyelenggaraan Pendidikan - {month} {year}',
                'amount': biaya_pendidikan,
            })

            self.env['sinerka.invoice.line'].create({
                'invoice_id': invoice.id,
                'description': f'Biaya Daftar Ulang',
                'amount': biaya_daftar_ulang,
            })

class sinerka_invoice_template(models.AbstractModel):
    _name = 'report.school_management.sinerka_invoice_template'

    def _convert_hundreds(self, n):
        n = int(n)
        units = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan"]
        words = []

        if n >= 100:
            words.append(units[n // 100] + " ratus")
            n %= 100
        if n >= 20:
            words.append(units[n // 10] + " puluh")
            n %= 10
        if n > 0:
            words.append(units[n])

        return " ".join(words)

    def _convert(self, amount):
        if amount == 0:
            return "nol"

        units = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan"]
        levels = ["", "ribu", "juta", "miliar", "triliun"]

        result = []
        level = 0

        while amount > 0:
            if amount % 1000 != 0:
                result.append(
                    self._convert_hundreds(amount % 1000) + ('' if levels[level] == '' else ' ' + levels[level]))
            amount //= 1000
            level += 1

        return " ".join(reversed(result)) + " rupiah"

    def _get_report_values(self, docids, data=None):
        invoice_id = docids[0]
        sinerka_invoice = self.env['sinerka.invoice'].sudo().search([('id', '=', invoice_id)])
        data_header = []
        for check in sinerka_invoice:
            current_time = datetime.now().strftime("%H:%M:%S")
            terbilang = self._convert(check.total_amount)
            tanggal_sekarang = datetime.now().strftime("%d %B %Y")
            data_header.append({
                'name': check.name,
                'student_id': check.student_id.name,
                'invoice_date': check.invoice_date,
                'current_time': current_time,
                'nis': check.nis,
                'class_ids': check.class_ids,
                'total_amount': check.total_amount,
                'terbilang': terbilang,
                'tanggal_sekarang': tanggal_sekarang,
            })

        sinerka_invoice_line = self.env['sinerka.invoice.line'].sudo().search([('invoice_id', '=', invoice_id)])
        data_line = []
        for data in sinerka_invoice_line:
            data_line.append({
                'amount': data.amount,
                'description': data.description,
            })
        result = {
            'data_header': data_header,
            'data_line': data_line,
        }
        return result
