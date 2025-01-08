from odoo import models,fields,api
import requests
from odoo.exceptions import ValidationError

AADHAR_API_KEY = "key_live_g7766sn0gxuDKxV3wTIdB54plOM3lCmc"
AADHAR_API_SECRET = "secret_live_KCViTOI2UiyFeWGrrIY0R1C6Atvs7ov9"
class AadhaarAuth(models.Model):
    _name = 'aadhar.auth'
    _description = 'Aadhaar Authentication'
    _order = "id desc"
    access_token = fields.Char()
    user_id = fields.Many2one('res.users', string='User')

    def _create_access_token(self):
        url = "https://api.sandbox.co.in/authenticate"
        headers = {
            "accept": "application/json",
            "x-api-key": AADHAR_API_KEY,
            "x-api-secret": AADHAR_API_SECRET,
            "x-api-version": "2.0"
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            res = response.json()
            try:
                self.env['aadhar.auth'].sudo().create({
                    'access_token' : res.get('access_token'),
                    'user_id' : self.env.user.id,
                })
            except Exception as ex:
                print(ex)
                raise ValidationError("Could not generate access token")

    def _get_access_token(self):
        return self.search([],limit=1,order="id desc")

    def send_otp(self,aadhar_no):
        print(">>>>>>>>CALLES")
        url = "https://api.sandbox.co.in/kyc/aadhaar/okyc/otp"
        if len(aadhar_no) != 12:
            return {"error" : "Invalid Aadhar Number"}
        payload = {
            "@entity": "in.co.sandbox.kyc.aadhaar.okyc.otp.request",
            "aadhaar_number": aadhar_no,
            "consent": "y",
            "reason": "FOR KYC"
        }
        try:
            auth_id = self._get_access_token()
            headers = {
                "accept": "application/json",
                "authorization":auth_id.access_token,
                "x-api-key": AADHAR_API_KEY,
                "x-api-version": "2.0",
                "content-type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers)
            res = response.json()
            print(res)
            return res

        except Exception as ex:
            return {"error" : "Failed to send OTP. Status code"}

    def validate_otp(self,ref_id,otp):
        url = "https://api.sandbox.co.in/kyc/aadhaar/okyc/otp/verify"
        if len(otp) != 6:
            return {"error" : "Invalid OTP"}
        payload = {
            "@entity": "in.co.sandbox.kyc.aadhaar.okyc.request",
            "reference_id": ref_id,
            "otp": otp
        }
        try:
            auth_id = self._get_access_token()
            headers = {
                "accept": "application/json",
                "authorization": auth_id.access_token,
                "x-api-key": AADHAR_API_KEY,
                "x-api-version": "2.0",
                "content-type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200 or response.status_code==422:
                res = response.json()
                print(res)
                return res
        except Exception as ex:
            return {"error" : "Failed to validate OTP. Status code"}