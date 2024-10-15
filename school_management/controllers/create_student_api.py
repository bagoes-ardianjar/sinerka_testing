from odoo import http, _, exceptions
from odoo.http import content_disposition, request
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError
import math
import requests
import json

import logging

_logger = logging.getLogger(__name__)

class create_student(http.Controller):
    @http.route('/api/create_student/', type='json', auth='none', methods=["POST"], csrf=False, cors="*")
    def func_create_mr(self, **params):
        data_return = []
        db_name = params['database_sinerka']
        username = params['username_sinerka']
        password = params['password_sinerka']
        name = params['name']
        nis = params['nis']
        age = params['age']
        student_address = params['student_address']
        is_active = params['is_active']
        try:
            http.request.session.authenticate(db_name, username, password)

            vals = {
                'name': name,
                'nis': nis,
                'age': age,
                'student_address': student_address,
                'is_active': is_active
            }
            new_student = request.env['sinerka.student'].sudo().create(vals)
            data = {
                'status': 200,
                'message': 'Success',
                'response': 'Data Siswa Berhasil Dibuat'
            }
            return data
        except Exception as exc:
            data = {
                'status': 400,
                'message': 'Error',
                'response': str(exc)
            }
            return data