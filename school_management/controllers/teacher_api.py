from odoo import http, _, exceptions
from odoo.http import content_disposition, request
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError
import math
import requests
import json

import logging

_logger = logging.getLogger(__name__)


class glaccnt_controller(http.Controller):
    @http.route('/api/teacher/', type='json', auth='none', methods=["POST"], csrf=False, cors="*")
    def func_glaccnt(self, **params):
        data_return = []
        db_name = params['database_sinerka']
        username = params['username_sinerka']
        password = params['password_sinerka']
        try:
            http.request.session.authenticate(db_name, username, password)
            res = request.env['ir.http'].session_info()
            if res['db'] == db_name and res['is_admin'] == True:
                check_data = request.env['sinerka.teacher'].sudo().search([])
                if check_data:
                    for data in check_data:
                        data_return.append({
                            'id': data.id,
                            'name': data.name,
                            'nip': data.nip,
                            'phone': data.phone,
                            'address': data.address,
                            'total_students': data.total_students,
                            })
                data = {
                    'status': 200,
                    'message': 'Success',
                    'response': data_return
                }
                return data
            else:
                data = {
                    'status': 400,
                    'message': 'Error',
                    'response': 'Mohon Check Ulang Data Pada Order Entry'
                }
                return data
        except Exception as exc:
            data = {
                'status': 400,
                'message': 'Error',
                'response': str(exc)
            }
            return data