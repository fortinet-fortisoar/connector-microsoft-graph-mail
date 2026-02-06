"""
Copyright start
Copyright (C) 2008 - 2025 FortinetInc.
All rights reserved.
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
Copyright end
"""

from base64 import b64encode, b64decode
from configparser import RawConfigParser
from datetime import datetime
from os import path
from time import time, ctime

from connectors.core.connector import get_logger, ConnectorError
from msal import ConfidentialClientApplication, ClientApplication

from .const import AUTH_BEHALF_OF_USER, AUTH_USING_APP, SCOPE, REFRESH_TOKEN_FLAG

CONFIG_SUPPORTS_TOKEN = True
try:
    from connectors.core.utils import update_connnector_config
except:
    CONFIG_SUPPORTS_TOKEN = False
    configfile = path.join(path.dirname(path.abspath(__file__)), 'config.conf')

logger = get_logger('microsoft-graph-mail')


class MicrosoftAuth:

    def __init__(self, config):
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.verify_ssl = config.get('verify_ssl')
        self.host = config.get("resource")
        tenant_id = config.get('tenant_id')
        self.auth_type = config.get("auth_type")
        self.authority_url = 'https://login.microsoftonline.com/{}'.format(tenant_id)
        self.scope = ['https://graph.microsoft.com/.default']
        if self.auth_type == AUTH_BEHALF_OF_USER:
            self.refresh_token = ""
            self.authorized_code = config.get("code")
            self.redirect_url = config.get("redirect_url") if config.get("redirect_url") else None

    def convert_ts_epoch(self, ts):
        try:
            datetime_object = datetime.strptime(ctime(ts), '%a %b %d %H:%M:%S %Y')
        except:
            datetime_object = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')

        return datetime_object.timestamp()

    def encode_token(self, token):
        try:
            token = token.encode('UTF-8')
            return b64encode(token)
        except Exception as err:
            logger.error(err)

    def generate_token(self, refresh_token_flag):
        try:
            if self.auth_type == AUTH_USING_APP:
                client = ConfidentialClientApplication(
                    self.client_id,
                    authority=self.authority_url,
                    client_credential=self.client_secret)
                token_resp = client.acquire_token_for_client(self.scope)
            else:
                token_resp = self.acquire_token_by_authorization_code(refresh_token_flag)
            error = token_resp.get('error')
            if error:
                raise ConnectorError(token_resp)
            ts_now = time()
            token_resp['expires_in'] = (ts_now + token_resp['expires_in']) if token_resp.get("expires_in") else None
            return token_resp

        except Exception as err:
            logger.error("{0}".format(err))
            raise ConnectorError("{0}".format(err))

    def write_config(self, token_resp, config, section_header):
        time_key = ['expires_in']
        token_key = ['access_token']

        config.add_section(section_header)
        for key, val in token_resp.items():
            if key not in time_key and key not in token_key:
                config.set(section_header, str(key), str(val))
        for key in time_key:
            config.set(section_header, str(key), self.convert_ts_epoch(token_resp['expires_in']))
        for key in token_key:
            config.set(section_header, str(key), self.encode_token(token_resp[key]).decode('utf-8'))

        try:
            with open(configfile, 'w') as fobj:
                config.write(fobj)
                fobj.close()
            return config
        except Exception as err:
            logger.error("{0}".format(str(err)))
            raise ConnectorError("{0}".format(str(err)))

    def handle_config(self, section_header, flag=False):
        # Lets setup the config parser.
        config = RawConfigParser()
        try:
            if path.exists(configfile) is False:
                token_resp = self.generate_token(REFRESH_TOKEN_FLAG)
                return self.write_config(token_resp, config, section_header)
            else:
                # Read existing config
                config.read(configfile)
                # Check for user
                if not config.has_section(section_header) and not flag:
                    # Write new config
                    token_resp = self.generate_token(REFRESH_TOKEN_FLAG)
                    return self.write_config(token_resp, config, section_header)
                else:
                    if flag:
                        config.remove_section(section_header)
                        with open(configfile, "w") as f:
                            config.write(f)
                    else:
                        config.read(config)
                return config

        except Exception as err:
            logger.error("Handle_config:Failure {0}".format(str(err)))
            raise ConnectorError(str(err))

    def validate_token(self, connector_config, connector_info):
        if CONFIG_SUPPORTS_TOKEN:
            ts_now = time()
            if not connector_config.get('access_token'):
                logger.error('Error occurred while connecting server: Unauthorized')
                raise ConnectorError('Error occurred while connecting server: Unauthorized')
            expires = connector_config['expires_in']
            expires_ts = self.convert_ts_epoch(expires)
            if ts_now > float(expires_ts):
                refresh_token_flag = True
                logger.debug("Token expired at {0}".format(expires))
                self.refresh_token = connector_config["refresh_token"]
                token_resp = self.generate_token(refresh_token_flag)
                connector_config['access_token'] = token_resp['access_token']
                connector_config['expires_in'] = token_resp['expires_in']
                connector_config['refresh_token'] = token_resp.get('refresh_token')
                update_connnector_config(connector_info['connector_name'], connector_info['connector_version'],
                                         connector_config,
                                         connector_config['config_id'])
                return "Bearer {0}".format(connector_config.get('access_token'))
            else:
                logger.debug("Token is valid till {0}".format(expires))

                return "Bearer {0}".format(connector_config.get('access_token'))
        else:
            client_id = connector_config.get('client_id')
            section_header = 'Microsoft-API-Auth-{0}'.format(client_id)
            time_key = ['expires_in']
            token_key = ['access_token']
            try:
                config = self.handle_config(section_header)
                ts_now = time()
                expires = config.get(section_header, 'expires_in')
                if ts_now > float(expires):
                    refresh_token_flag = True
                    self.refresh_token = config.get(section_header, 'refresh_token')
                    logger.info("Token expired at {0}".format(str(expires)))
                    new_token = self.generate_token(refresh_token_flag)
                    for key, val in new_token.items():
                        if key in time_key:
                            config.set(section_header, str(key), self.convert_ts_epoch(new_token.get(key)))
                        if key in token_key:
                            config.set(section_header, str(key), self.encode_token(new_token[key]).decode('utf-8'))

                    with open(configfile, 'w') as fobj:
                        config.write(fobj)
                else:
                    logger.info("Token is valid till {0}".format(str(expires)))

                encoded_token = config.get(section_header, 'access_token')
                decoded_token = b64decode(encoded_token.encode('utf-8'))
                token = "Bearer {0}".format(decoded_token.decode('utf-8'))
                return token
            except Exception as err:
                logger.error("{0}".format(str(err)))
                raise ConnectorError("{0}".format(str(err)))

    def remove_config(self):
        try:
            section_header = 'Microsoft-API-Auth-{0}'.format(self.client_id)
            self.handle_config(section_header, flag=True)
        except Exception as err:
            logger.error("{0}".format(str(err)))
            raise ConnectorError("{0}".format(str(err)))

    def acquire_token_by_authorization_code(self, refresh_token_flag):
        client_instance = ClientApplication(client_id=self.client_id, client_credential=self.client_secret,
                                            authority=self.authority_url)
        if refresh_token_flag:
            try:
                access_token = client_instance.acquire_token_by_refresh_token(refresh_token=self.refresh_token,
                                                                              scopes=SCOPE)
            except Exception as e:
                msg = 'Error in token generation using refresh token' + str(e)
                raise ConnectorError(msg)
        else:
            access_token = client_instance.acquire_token_by_authorization_code(code=self.authorized_code, scopes=SCOPE,
                                                                               redirect_uri=self.redirect_url)
        return access_token


def _check_health(config):
    try:
        ms_auth = MicrosoftAuth(config)
        connector_info = config.pop('connector_info', '')
        if CONFIG_SUPPORTS_TOKEN:
            if not 'access_token' in config:
                token_resp = ms_auth.generate_token(REFRESH_TOKEN_FLAG)
                config['access_token'] = token_resp.get('access_token')
                config['expires_in'] = token_resp.get('expires_in')
                config['refresh_token'] = token_resp.get('refresh_token')
                update_connnector_config(connector_info['connector_name'], connector_info['connector_version'], config,
                                         config['config_id'])
                return True
            else:
                if config.get('auth_type') == AUTH_USING_APP:
                    if config.get('access_token'):
                        token_resp = ms_auth.validate_token(config, connector_info)
                        return True
                    else:
                        msg = 'Error occurred while connecting server: Unauthorized'
                        logger.error(msg)
                        raise ConnectorError(msg)
                else:
                    token_resp = ms_auth.validate_token(config, connector_info)
                    return True

        else:
            ms_auth.remove_config()
            client_id = config.get('client_id')
            section_header = 'Microsoft-API-Auth-{0}'.format(client_id)
            ms_auth.handle_config(section_header)
            return True
    except Exception as err:
        logger.error(str(err))
        raise ConnectorError(str(err))