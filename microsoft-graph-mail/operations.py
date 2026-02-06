"""
Copyright start
Copyright (C) 2008 - 2025 FortinetInc.
All rights reserved.
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
Copyright end
"""

import base64
import json
import requests
import uuid
from connectors.core.connector import get_logger, ConnectorError
from connectors.cyops_utilities.builtins import download_file_from_cyops, upload_file_to_cyops, save_file_in_env
from django.conf import settings
from integrations.crudhub import make_request
from os.path import join, getsize, splitext

from .const import (WELL_KNOWN_FOLDERS, DEFAULT_MESSAGE_LIMIT, DEFAULT_FOLDER_LIMIT,
                    FILE_ATTACHMENT, ITEM_ATTACHMENT, DEFAULT_FOLDER, FLAG_STATUS, IMPORTANCE, CATEGORY)
from .microsoft_api_auth import MicrosoftAuth
from connectors.environment import expand

logger = get_logger('microsoft-graph-mail')


class MicrosoftGraphMail(object):
    def __init__(self, config):
        self.server_url = config.get('resource', '').strip('/')
        if not self.server_url.startswith('https://') and not self.server_url.startswith('http://'):
            self.server_url = 'https://' + self.server_url
        self.verify_ssl = config.get('verify_ssl')
        self.ms_auth = MicrosoftAuth(config)
        self.connector_info = config.pop('connector_info', '')
        self.token = self.ms_auth.validate_token(config, self.connector_info)

    def make_rest_call(self, endpoint, params=None, json=None, payload=None, method='POST'):
        headers = {'Authorization': self.token, 'Content-Type': 'application/json'}
        service_url = f'{self.server_url}{endpoint}'
        logger.debug('Request URL {}'.format(service_url))
        try:
            from connectors.debug_utils.curl_script import make_curl
            make_curl(method, endpoint, headers=headers, params=params, data=payload, verify_ssl=self.verify_ssl)
        except Exception as err:
            logger.error(f"Error in curl utils: {str(err)}")

        try:
            response = requests.request(method, service_url, data=payload, headers=headers, json=json, params=params,
                                        verify=self.verify_ssl)
            if response.ok:
                content_type = response.headers.get('Content-Type')
                if response.text != "" and 'application/json' in content_type:
                    return response.json()
                else:
                    return response.content
            else:
                if response.text != "":
                    err_resp = response.json()
                    if "error" in err_resp:
                        error_msg = "{}: {}".format(err_resp.get('error').get('code'),
                                                    err_resp.get('error').get('message'))
                        raise ConnectorError(error_msg)
                else:
                    error_msg = '{0}: {1}'.format(response.status_code, response.reason)
                    raise ConnectorError(error_msg)
        except requests.exceptions.SSLError:
            logger.error('An SSL error occurred')
            raise ConnectorError('An SSL error occurred')
        except requests.exceptions.ConnectionError:
            logger.error('A connection error occurred')
            raise ConnectorError('A connection error occurred')
        except requests.exceptions.Timeout:
            logger.error('The request timed out')
            raise ConnectorError('The request timed out')
        except requests.exceptions.RequestException:
            logger.error('There was an error while handling the request')
            raise ConnectorError('There was an error while handling the request')
        except Exception as e:
            logger.error('{0}'.format(e))
            raise ConnectorError('{0}'.format(e))

    def get_folder_details(self, user_id, folder_id):
        try:
            endpoint = '/v1.0/users/{0}/mailFolders/{1}'.format(user_id, folder_id)
            resp = self.make_rest_call(endpoint, method='GET')
            if resp and isinstance(resp, dict):
                return resp.get('id')
        except Exception as err:
            logger.error("{0}".format(err))
            raise ConnectorError(err)

    def get_folder_children(self, user_id, parent_folder_id, limit=None):
        try:
            limit = limit if limit else DEFAULT_FOLDER_LIMIT
            endpoint = '/v1.0/users/{0}/mailFolders/{1}/childFolders?$top={2}'.format(user_id, parent_folder_id, limit)
            resp = self.make_rest_call(endpoint, method='GET')
            if resp and isinstance(resp, dict):
                return resp.get('value')
        except Exception as err:
            logger.error("{0}".format(err))
            raise ConnectorError(err)

    def get_root_folder_children(self, user_id, limit=None):
        try:
            limit = limit if limit else DEFAULT_FOLDER_LIMIT
            endpoint = '/v1.0/users/{0}/mailFolders/msgfolderroot/childFolders?$top={1}'.format(user_id, limit)
            resp = self.make_rest_call(endpoint, method='GET')
            if resp and isinstance(resp, dict):
                return resp.get('value')
        except Exception as err:
            logger.error("{0}".format(err))
            raise ConnectorError(err)

    def build_endpoint_by_path(self, user_id, folder_path):
        try:
            list_folders = []
            endpoint = '/mailFolders'
            if folder_path:
                list_folders = folder_path.replace('\\', '/').split('/')
                if list_folders[0].lower() in WELL_KNOWN_FOLDERS:
                    folder_id = WELL_KNOWN_FOLDERS.get(list_folders[0].lower())
                    if len(list_folders) == 1:
                        folder_id = self.get_folder_details(user_id, folder_id)
                        endpoint += '/' + folder_id
                        return endpoint
                    else:
                        endpoint += '/' + folder_id
                        current_folder_child_folder = self.get_folder_children(user_id, folder_id)
                        list_folders.pop(0)
                else:
                    current_folder_child_folder = self.get_root_folder_children(user_id)
                    endpoint += '/msgfolderroot'

                for index, folder_name in enumerate(list_folders):
                    found_folder = [folder for folder in current_folder_child_folder if
                                    folder.get('displayName', '').lower() == folder_name.lower() or folder.get('id',
                                                                                                               '') == folder_name]
                    if not found_folder:
                        raise ConnectorError('No such folder exist: {}'.format(folder_path))
                    found_folder = found_folder[0]
                    endpoint += '/childFolders/' + found_folder.get('id')

                    if index == len(list_folders) - 1:
                        return endpoint

                    current_folder_child_folder = self.get_folder_children(user_id, found_folder.get('id', ''))
            return DEFAULT_FOLDER

        except Exception as err:
            logger.error("{0}".format(err))
            raise ConnectorError(err)

    def get_folder_id_by_path(self, user_id, folder_path):
        try:
            list_folders = []
            if folder_path:
                list_folders = folder_path.replace('\\', '/').split('/')
                if list_folders[0].lower() in WELL_KNOWN_FOLDERS:
                    folder_id = WELL_KNOWN_FOLDERS.get(list_folders[0].lower())
                    if len(list_folders) == 1:
                        return self.get_folder_details(user_id, folder_id)
                    else:
                        current_folder_child_folder = self.get_folder_children(user_id, folder_id)
                        list_folders.pop(0)
                else:
                    current_folder_child_folder = self.get_root_folder_children(user_id)

                for index, folder_name in enumerate(list_folders):
                    found_folder = [folder for folder in current_folder_child_folder if
                                    folder.get('displayName', '').lower() == folder_name.lower() or folder.get('id',
                                                                                                               '') == folder_name]
                    if not found_folder:
                        raise ConnectorError('No such folder exist: {}'.format(folder_path))
                    found_folder = found_folder[0]

                    if index == len(list_folders) - 1:
                        return found_folder.get('id')

                    current_folder_child_folder = self.get_folder_children(user_id, found_folder.get('id', ''))

        except Exception as err:
            logger.error("{0}".format(err))
            raise ConnectorError(err)


def update_message(ms, endpoint, email_id):
    try:
        payload = json.dumps({"isRead": True})
        message_endpoint = ''
        message_endpoint = '{}/{}'.format(endpoint, email_id)
        resp = ms.make_rest_call(message_endpoint, method='PATCH', payload=payload)
        return True if resp else False
    except Exception as err:
        logger.error("{0}".format(err))


def get_attachments_details(ms, endpoints, list_attachments_ids):
    try:
        attachments_data = []
        for attachments_id in list_attachments_ids:
            attachment_endpoint = ''
            attachment_endpoint = f'{endpoints}/{attachments_id}'
            resp = ms.make_rest_call(attachment_endpoint, method='GET')
            if resp and isinstance(resp, dict):
                attachments = resp.get('value')
                attachments_data.append(attachments)
        return attachments_data
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def _create_file(file_content, file_extension='', filename=''):
    try:
        if not filename:
            filename = uuid.uuid4().hex + '.' + file_extension
        file_path = join(settings.TMP_FILE_ROOT, filename)
        binary_content = base64.b64decode(file_content) if not isinstance(file_content, bytes) else file_content
        mode = 'w{}'.format('b' if type(binary_content) is bytes else '')
        with open(file_path, mode) as fp:
            fp.write(binary_content)
        return filename
    except Exception as e:
        logger.error('file operation error %s' % e)


def handle_attachment(attachment, attachment_name, attachment_content, email_attachments, is_eml=False, **kwargs):
    try:
        env = kwargs.get('env', {})
        file_name, filetype = splitext(attachment_name)
        file_name = file_name.replace("/", '-')
        filetype = filetype.strip('.')
        if is_eml and not filetype:
            filetype = 'eml'
            file_name = file_name + '.' + filetype
        else:
            file_name = attachment_name
        _file_name = _create_file(attachment_content, filetype)
        attachment['name'] = file_name
        attachment['cyops_file_path'] = _file_name if _file_name else ''
        email_attachments.append(attachment)
        save_file_in_env(env=env, filename=_file_name)
        return email_attachments
    except Exception as err:
        logger.error("{0}".format(err))


def extract_attachments(ms, endpoint, body_content, parse_inline, is_eml=False, **kwargs):
    try:
        resp = ms.make_rest_call(endpoint, method='GET')
        email_attachments = []
        if resp:
            list_attachments = resp.get('value')
            for attachment in list_attachments:
                is_inline = attachment.get('isInline', '')
                attachment_name = attachment.get('name', '')
                if not attachment_name:
                    attachment['name'] = 'untitled_attachment'
                attachment_type = attachment.get('@odata.type', '')
                attachment_content = attachment.pop('contentBytes', '')
                if is_inline and parse_inline:
                    contentId = attachment.get('contentId', '')
                    content_type = attachment.get('contentType', '')
                    img_content = f"data:{content_type};base64,{attachment_content}"
                    body_content = body_content.replace('\"{}\"'.format('cid:' + contentId), img_content)
                    handle_attachment(attachment, attachment_name, attachment_content, email_attachments, **kwargs)

                elif attachment_type == FILE_ATTACHMENT and not is_inline:
                    handle_attachment(attachment, attachment_name, attachment_content, email_attachments, **kwargs)

                elif attachment_type == ITEM_ATTACHMENT:
                    attachment_id = attachment.get('id', '')
                    mime_endpoint = f'{endpoint}/{attachment_id}/$value'
                    mime_content = ms.make_rest_call(mime_endpoint, method='GET')
                    handle_attachment(attachment, attachment_name, mime_content, email_attachments, is_eml=True,
                                      **kwargs)

        list_attachments = email_attachments if email_attachments else []
        return list_attachments, body_content
    except Exception as err:
        logger.error("{0}".format(err))
    return [], body_content


def get_email_attachments(ms, endpoint, email, parse_inline=False, **kwargs):
    try:
        message_id = email.get('id')
        body_content = email.get('body', {}).get('content')
        is_attachments = email.get('hasAttachments')
        if is_attachments or parse_inline:
            attachments_endpoint = f'{endpoint}/{message_id}/attachments'
            list_attachments, body_content = extract_attachments(ms, attachments_endpoint, body_content, parse_inline,
                                                                 **kwargs)
            if email.get('body'):
                email['body']['content'] = body_content
            return list_attachments
        return {}
    except Exception as err:
        logger.error("{0}".format(err))


def save_eml_file_as_attachment(ms, base_url, email, file_name):
    try:
        id = email.get('id')
        email_subject = email.get('subject')
        message_url = f'{base_url}/messages/{id}/$value'
        file_path = join(settings.TMP_FILE_ROOT, file_name)
        file_content = ms.make_rest_call(message_url, method='GET')
        with open(file_path, 'wb') as fp:
            fp.write(file_content)
        attach_response = upload_file_to_cyops(file_path=file_name, filename=file_name,
                                               name=file_name, create_attachment=True, description=email_subject)


        return attach_response
    except Exception as err:
        logger.error("{0}".format(err))


def get_unread_emails(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        user_id = params.get('user_id')
        folder_path = params.get('folder_id')
        mark_as_read = params.get('mark_as_read')
        is_save_email_as_eml = params.get('save_email')
        parse_inline = params.get('parse_inline')
        limit = params.get('limit') if params.get('limit') else DEFAULT_MESSAGE_LIMIT
        mailbox_endpoint = ms.build_endpoint_by_path(user_id, folder_path)
        base_url = f'/v1.0/users/{user_id}'
        message_endpoint = f'{base_url}{mailbox_endpoint}/messages'
        query_string = f'?$filter=isRead eq false&$top={limit}'
        endpoint = f'{message_endpoint}{query_string}'
        response = ms.make_rest_call(endpoint, method='GET')
        emails = response.get('value')
        email_ids = [email.get('id') for email in emails if emails]
        for email in emails:
            list_attachments = []
            message_id = email.get('id', '')
            email['email_as_attachment'] = {}
            email['parsed_attachment_data'] = []
            attachments = get_email_attachments(ms, message_endpoint, email, parse_inline, **kwargs)
            if attachments:
                list_attachments.extend(attachments)
            if is_save_email_as_eml and email_ids:
                attachment_response = save_eml_file_as_attachment(ms, base_url, email, f'{message_id}.eml')
                email['email_as_attachment'] = attachment_response
            if mark_as_read and update_message(ms, message_endpoint, email.get('id')):
                email['isRead'] = True
            email['attachments'] = list_attachments
        return emails
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def search_emails(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        user_id = params.get('user_id')
        limit = params.get('limit') if params.get('limit') else DEFAULT_MESSAGE_LIMIT
        folder_path = params.get('folder_id')
        odata = params.get('odata_query')
        parse_inline = params.get('parse_inline')
        search = params.get('search')
        mark_as_read = params.get('mark_read')
        mailbox_endpoint = ms.build_endpoint_by_path(user_id, folder_path)
        if not mailbox_endpoint.startswith('/'):
            message_endpoint = f'/v1.0/users/{user_id}/{mailbox_endpoint}/messages'
        else:
            message_endpoint = f'/v1.0/users/{user_id}{mailbox_endpoint}/messages'
        endpoint = message_endpoint
        query_string = f'{odata}&$top={limit}' if odata else f'$top={limit}'
        if search:
            query_string = f'{query_string}&$search="{search}"'
        endpoint += f'?{query_string}'
        response = ms.make_rest_call(endpoint, method='GET')
        emails = response.get('value')
        for email in emails:
            list_attachments = []
            if mark_as_read and update_message(ms, message_endpoint, email.get('id')):
                email['isRead'] = True
            attachments = get_email_attachments(ms, message_endpoint, email, parse_inline, **kwargs)
            if attachments:
                list_attachments.extend(attachments)
            email['attachments'] = list_attachments

        return emails
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def update_email_categories(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        user_id = params.get('user_id')
        message_id = params.get('message_id')
        categories = params.get('categories')
        try:
            cat_list = [c.strip() for c in categories.split(',')]
        except Exception as e:
            cat_list = [categories.strip()]
        request_body = json.dumps({"categories": cat_list})
        endpoint = f'/v1.0/users/{user_id}/messages/{message_id}'
        return ms.make_rest_call(endpoint, method='PATCH', payload=request_body)
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def add_email_category(config, params, **kwargs):
    try:
        new_category = params.get('category', '').split(',')
        categories_resp = get_email_categories(config, params)
        existing_categories = categories_resp.get('categories')
        # Ensure current_categories is a list
        if isinstance(existing_categories, str):
            cat_list = [c.strip() for c in existing_categories.split(',')]
        else:
            cat_list = existing_categories
        if isinstance(new_category, list):
            for category in new_category:
                if category.strip() not in cat_list:
                    cat_list.append(category.strip())
        else:
            if new_category.strip() not in cat_list:
                cat_list.append(new_category.strip())
        params['categories'] = ','.join(cat_list)
        return update_email_categories(config, params)
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def remove_email_category(config, params, **kwargs):
    try:
        categories_resp = get_email_categories(config, params)
        existing_categories = categories_resp.get('categories')
        category_to_delete = params.get('category','').split(',')
        if isinstance(existing_categories, str):
            cat_list = [c.strip() for c in existing_categories.split(',')]
        else:
            cat_list = existing_categories
        if isinstance(category_to_delete, list):
            for category in category_to_delete:
                if category.strip() in cat_list:
                    cat_list.remove(category.strip())
        else:
            if category_to_delete.strip() in cat_list:
                cat_list.remove(category_to_delete.strip())
        params['categories'] = ','.join(cat_list)
        return update_email_categories(config, params)
    except Exception as err:
        logger.error(f"Error deleting email category: {err}")
        raise ConnectorError(err)


def get_email_categories(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        user_id = params.get('user_id')
        message_id = params.get('message_id')
        endpoint = f'/v1.0/users/{user_id}/messages/{message_id}'
        resp = ms.make_rest_call(endpoint, method='GET')
        response = {'emai_address': user_id, 'message_id': message_id, 'categories': []}
        if response and isinstance(response, dict):
            response.update({'categories': resp.get('categories', [])})
        return response
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def get_folders(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        user_id = params.get('user_id')
        limit = params.get('limit')
        return ms.get_root_folder_children(user_id, limit)
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def get_child_folders(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        user_id = params.get('user_id')
        limit = params.get('limit')
        source = params.get('source_folder')
        folder_id = params.get('folder_id')
        if source == 'Folder Path' or '/' in folder_id:
            folder_id = ms.get_folder_id_by_path(user_id, folder_id)
        return ms.get_folder_children(user_id, folder_id, limit)
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def copy_move_email(config, params, action):
    try:
        ms = MicrosoftGraphMail(config)
        user_id = params.get('user_id')
        message_id = params.get('message_id')
        destination_folder = params.get('destination_folder')
        folder_path = params.get('folder_id')
        if destination_folder == 'Folder Path':
            destination_folder_id = ms.get_folder_id_by_path(user_id, folder_path)
        else:
            destination_folder_id = folder_path
        endpoint = f'/v1.0/users/{user_id}/messages/{message_id}/{action}'
        request_body = json.dumps({'destinationId': destination_folder_id})
        return ms.make_rest_call(endpoint, method='POST', payload=request_body)
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def move_email(config, params, **kwargs):
    return copy_move_email(config, params, 'move')


def copy_email(config, params, **kwargs):
    return copy_move_email(config, params, 'copy')


def delete_email(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        user_id = params.get('user_id')
        folder_path = params.get('folder_id')
        message_id = params.get('message_id')
        if folder_path:
            mailbox_endpoint = ms.build_endpoint_by_path(user_id, folder_path)
            folder_path = f'/v1.0/users/{user_id}{mailbox_endpoint}/messages/{message_id}'
        default_path = f'/v1.0/users/{user_id}/messages/{message_id}'
        endpoint = folder_path if folder_path else default_path
        resp = ms.make_rest_call(endpoint, method="DELETE")
        if not resp:
            return {'status': 'success', 'message': 'Message successfully deleted'}
    except Exception as e:
        logger.error('{0}'.format(e))
        raise ConnectorError('{0}'.format(e))


def build_list_recipient(recipients):
    if recipients and isinstance(recipients, str):
        recipients = recipients.split(',')
    if recipients and isinstance(recipients[0], dict):
        return recipients
    list_recipients = [{'emailAddress': {'address': email.strip()}} for email in recipients] if recipients else []
    return list_recipients



def build_message_payload(params, env={}):
    try:
        file_attachment = []
        to_recipients = params.get('to_recipients')
        cc_recipients = params.get('cc_recipients')
        bcc_recipients = params.get('bcc_recipients')
        importance = params.get('importance')
        flag = params.get('flag')
        iri_list = params.get('iri_list')
        if params.get('body_type') == 'Email Template':
            email_template = params.get('email_templates')
            subject, body = _email_template_handler(email_template, env=env)
        else:
            body = params.get('body')
            subject = str(params.get('subject'))
        if iri_list:
            file_attachment = _handle_attachments(iri_list)
        message = {
            'toRecipients': build_list_recipient(to_recipients),
            'ccRecipients': build_list_recipient(cc_recipients),
            'bccRecipients': build_list_recipient(bcc_recipients),
            'subject': subject,
            'body': {"content": body, "contentType": "html"},
            'importance': IMPORTANCE.get(importance),
            'bodyPreview': body[:255],
            'flag': {'flagStatus': FLAG_STATUS.get(flag)},
            'attachments': file_attachment
        }
        return message

    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def _handle_attachments(iri_list, inline=False):
    try:
        list_attachments = []
        if iri_list and isinstance(iri_list, str):
            iri_list = iri_list.split(',')
        for iri in iri_list:
            iri_type = 'attachment'
            if not iri.startswith('/api/3/'):
                iri = '/api/3/attachments/' + iri
            elif iri.startswith('/api/3/files'):
                iri_type = 'file'
            file_name, file_path, file_data = read_file_from_cyops(iri, iri_type)
            attachment = build_attachment_payload(file_data, file_name, file_path, inline)
            if attachment:
                list_attachments.append(attachment)
        return list_attachments
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def build_attachment_payload(file_data, filename, file_path, inline=False):
    if file_data:
        attachment = {
            '@odata.type': FILE_ATTACHMENT,
            'contentBytes': file_data.decode('utf-8'),
            'isInline': inline,
            'name': filename,
            'size': getsize(file_path)}
        return attachment
    return None


def read_file_from_cyops(iri, iri_type):
    try:
        file_name = None
        if iri_type == 'attachment':
            attachment_data = make_request(iri, 'GET')
            file_iri = attachment_data['file']['@id']
            file_name = attachment_data['file']['filename']
        else:
            file_iri = iri
        file_download_response = download_file_from_cyops(file_iri)
        if not file_name:
            file_name = file_download_response['filename']
        file_path = join('/tmp', file_download_response['cyops_file_path'])
        with open(file_path, 'rb') as attachment:
            file_data = base64.b64encode(attachment.read())
        return file_name, file_path, file_data

    except Exception as err:
        logger.exception('{0}'.format(err))
        logger.exception(str(err))


def send_email(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        from_email = params.get('from')
        endpoint = f'/v1.0/users/{from_email}/sendMail'
        env = kwargs.get('env', {})
        message_payload = build_message_payload(params, env)
        request_payload = json.dumps({'message': message_payload})
        resp = ms.make_rest_call(endpoint, method="POST", payload=request_payload)
        return {'status': 'success', 'message': 'Email successfully sent'} if not resp else resp
    except Exception as e:
        logger.exception('{0}'.format(e))
        raise ConnectorError('{0}'.format(e))


def build_reply_message_payload(params):
    try:
        file_attachment = []
        to_recipients = params.get('to')
        cc_recipients = params.get('cc_recipients')
        bcc_recipients = params.get('bcc_recipients')
        body = params.get('body')
        iri_list = params.get('iri_list')
        if iri_list:
            file_attachment = _handle_attachments(iri_list)
        list_to_recipients = build_list_recipient(to_recipients)
        message = {
            'ccRecipients': build_list_recipient(cc_recipients),
            'bccRecipients': build_list_recipient(bcc_recipients),
            'bodyPreview': body[:255],
            'attachments': file_attachment
        }
        if list_to_recipients:
            message.update({'toRecipients': list_to_recipients})
        return message
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def forward_email(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        from_recipients = params.get('from_recipients')
        to_recipients = params.get('to_recipients')
        body = params.get('body')
        message_id = params.get('message_id')
        if to_recipients:
            to_recipients = build_list_recipient(to_recipients)
        endpoint = f'/v1.0/users/{from_recipients}/messages/{message_id}/forward'
        request_payload = json.dumps({'toRecipients': to_recipients, 'comment': body})
        resp = ms.make_rest_call(endpoint, payload=request_payload, method='POST')
        return resp if resp else {'status': 'success', 'message': 'Email successfully forward'}
    except Exception as e:
        logger.error('{0}'.format(e))
        raise ConnectorError('{0}'.format(e))


def send_email_as_reply(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        body = params.get('body')
        from_recipients = params.get('from_recipients')
        message_id = params.get('message_id')
        message = build_reply_message_payload(params)
        request_payload = json.dumps({'message': message, 'comment': body})
        reply_endpoint = f'/v1.0/users/{from_recipients}/messages/{message_id}/reply'
        resp = ms.make_rest_call(reply_endpoint, payload=request_payload, method='POST')
        result = resp if resp else {'status': 'success', 'message': 'Email successfully reply'}
        return result
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)


def create_email_threat_submission(config, params, **kwargs):
    try:
        ms = MicrosoftGraphMail(config)
        params = _build_payload(params, CATEGORY)
        if params.pop('input') == 'Email Content Threat Submission':
            file_content = params.get('fileContent')
            encoded_content = base64.b64encode(file_content.encode()).decode()
            params.update({'fileContent': encoded_content})

        reply_endpoint = f'/beta/security/threatSubmission/emailThreats'
        resp = ms.make_rest_call(reply_endpoint, payload=json.dumps(params), method='POST')
        return resp
    except Exception as err:
        logger.error("{0}".format(err))
        raise ConnectorError(err)

def execute_api_request(config, params, **kwargs):
    ms = MicrosoftGraphMail(config)
    endpoint = params.get('endpoint','')
    query_params = params.get('query_params',{})
    method = params.get('method', '')
    payload = params.get('payload')
    if not endpoint.startswith('/'):
        endpoint = f'/{endpoint}'
    return ms.make_rest_call(endpoint=endpoint, method=method,params=query_params, payload=json.dumps(payload))


def _build_payload(params: dict, options_dict: dict = {}) -> dict:
    if params.get('other_params'):
        params.update(params.pop('other_params'))

    return {key: options_dict.get(val, val) if isinstance(val, str) else val for key, val in params.items() if
            isinstance(val, (bool, int)) or val}

def _email_template_handler(email_template, env={}):
    request_body = {'logic': 'OR', 'filters': [{'field': 'name', 'operator': 'eq', 'value': email_template}]}
    response = make_request('/api/query/email_templates', 'POST', body=request_body)['hydra:member']
    subject = ''
    content = ''
    if response:
        subject = response[0]['subject']
        content = response[0]['content']
        try:
            subject = expand(env, subject)
            content = expand(env, content)
        except Exception as err:
            logger.error('err: {}'.format(err))
            raise ConnectorError(err)
    return subject, content


def get_email_templates(config, params, **kwargs):
    email_template_names = []
    response = make_request('/api/3/email_templates', 'GET')['hydra:member']
    for email_template in response:
        email_template_names.append(email_template['name'])
    return email_template_names

operations = {
    'get_unread_emails': get_unread_emails,
    'search_emails': search_emails,
    'get_folders': get_folders,
    'get_child_folders': get_child_folders,
    'move_email': move_email,
    'copy_email': copy_email,
    'delete_email': delete_email,
    'send_email': send_email,
    'forward_email': forward_email,
    'send_email_as_reply': send_email_as_reply,
    'create_email_threat_submission': create_email_threat_submission,
    'update_email_categories': update_email_categories,
    'add_email_category': add_email_category,
    'remove_email_category': remove_email_category,
    'get_email_categories': get_email_categories,
    'execute_api_request': execute_api_request,
    'get_email_templates': get_email_templates
}
