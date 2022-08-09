from distutils.util import change_root
import logging
import requests
import odoorpc

from ntpath import join
from xml.dom import ValidationErr
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self, vals):
        _logger.warning(f"VALS: {vals}")

        res = super(MailMessage, self).create(vals)

        # channel_id = vals.get("id")
        # if channel_id:
        #     _logger.warning(f"CHANNEL ID: {channel_id}")
        #     channel = self.env["mail.channel"].search_read([("id", "=", channel_id)])
        #     _logger.warning(f"CHANNEL: {channel}")
        #     if channel:
        #         channel_partners = channel[0].get("channel_partner_ids")
        #         _logger.warning(f"CHANNEL PARTNER IDS: {self.env.user.partner_id.name}")

        # headers = {
        #     'Content-Type': 'text/plain',
        # }
        # data = 'MESSAGE HERE'
        # test = requests.post('http://hoary.vertel.se:5280/msg/to@hoary.vertel.se', headers=headers, data=data, auth=('admin@hoary.vertel.se', 'admin'))


        # _logger.warning(f"RES: {res}")
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        #_logger.error(f"{self=}")
        #_logger.error(f"{fields=}")

        keys = self.fields_get()
        for i, dom in enumerate(domain):
            field = dom[0]
            if 'many2one' in keys[field]["type"]:
                try:
                    possible_int = int(domain[i][2])
                except:
                    pass
                else: 
                    domain[i][2] = possible_int
            elif 'many2many' in keys[field]["type"]:
                try:
                    possible_int = int(domain[i][2])
                except:
                    pass
                else: 
                    domain[i][2] = possible_int
        #_logger.error(f"{domain=}")
        res = super().search_read(domain, fields, offset, limit, order)
        return res 

class TestSearchRead(models.Model):
    _inherit = "res.users"

    def search_read_custom(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super().search_read(domain, fields, offset, limit, order)
        return res 

class ChannelSearchRead(models.Model):
    _inherit = "mail.channel"

    def search_read_custom(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super().search_read(domain, fields, offset, limit, order)
        return res 

    @api.model
    def search_custom(self, *args, offset=0, limit=None, order=None, count=False):
        new_args =[]
        for arg in args:
            new_arg=[]
            for a in arg:
                new_arg.append(int(a) if a.isdigit() else a)
            new_args.append(new_arg)
        _logger.error(f"{new_args=}")
        res = super(ChannelSearchRead, self).search(new_args, offset, limit, order, count)
        return res.ids if res else 0

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *,
                     body='', subject=None, message_type='notification',
                     email_from=None, author_id=None, parent_id=False,
                     subtype_xmlid=None, subtype_id=False, partner_ids=None, channel_ids=None,
                     attachments=None, attachment_ids=None,
                     add_sign=True, record_name=False,
                     **kwargs):

                    #_logger.error(f"{kwargs=}")

                    res = super().message_post(body=body, subject=subject, message_type=message_type,
                                                email_from=email_from, author_id=author_id, parent_id=parent_id,
                                                subtype_xmlid=subtype_xmlid, subtype_id=subtype_id, partner_ids=partner_ids,
                                                channel_ids=channel_ids, attachments=attachments, attachment_ids=attachment_ids,
                                                add_sign=add_sign, record_name=record_name, **kwargs)
                    #_logger.error(f"res {res=}")
                    if res.id and not kwargs.get("prosody"):
                        url = "https://hoary.vertel.se:5281/rest"
                        js = {'body': body, 'kind': 'message', 'to': 'dostoevsky@hoary.vertel.se', 
                              'type': 'chat', 'id': 'ODOOODOO' + str(res.id)}
                        headers = {'Content-type': 'application/json'}
                        request_post = requests.post(url, json=js, headers=headers, verify=False, auth=("admin", "admin"))
                    return res


class MessagePost(models.Model):
    _name = "message.post.test"
    _inherit = ["mail.thread"]

    @api.model
    def message_post_test(self, *args):   
        #_logger.error(f"{self=}")
        # _logger.error(f"{self.name=}")
        for arg in args:
            #_logger.error(f"{arg=}")
            if (channel:=self.env["mail.channel"].browse(arg.get('id'))):
                _logger.error(f"{channel=}")
                new_arg = {a:arg[a] for a in arg}
                new_arg["prosody"] = True

                #_logger.error(f"{new_arg=}")
                #_logger.error(f"{arg=}")
                #_logger.error("before message_post")
                message_post = channel.message_post(**new_arg).id
                  
                return message_post
                #_logger.error(f"message_post_test {ids=}")

