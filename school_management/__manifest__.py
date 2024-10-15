{
    'name': 'School Management',
    'version': '16.0',
    'category': 'management',
    'summary': 'School Management Module',
    'description': """
        School Management Module Sinerka By Bagoes
    """,
    'website': '',
    'author': 'Bagoes Ardianjar',
    'depends': ['web','base'],
    'data': [
        'data/invoice_scheduler.xml',
        'security/ir.model.access.csv',
        'views/sinerka_school_view.xml',
        'views/sinerka_school_action.xml',
        'views/sinerka_school_menuitem.xml',
        'views/sinerka_school_sequence.xml',
        'reports/report_teacher_student.xml',
        'reports/sinerka_invoice_template.xml',
        'reports/paper_format_report.xml',
        'reports/report_pdf.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
}