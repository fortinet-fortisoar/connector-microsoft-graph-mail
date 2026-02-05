# Edit the config_and_params.json file and add the required parameter values.
# Add any specific assertions in each test case, based on the expected response.
# Add logic for validating conditional_output_schema.

"""
Copyright start
Copyright (C) 2008 - 2025 Fortinet Inc.
All rights reserved.
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
Copyright end
"""

import pytest
from pprint import pformat
from testframework.conftest import initial_setup, info_json, params_json, validate_params, connector_id, connector_details,\
    valid_configuration, invalid_configuration, valid_configuration_with_token, conn_cleanup
from testframework.helpers.test_helpers import run_health_check_success, run_invalid_config_test, run_success_test,\
    run_output_schema_validation, run_invalid_param_test, set_report_metadata
from testframework.helpers.test_constants import VALID_CONFIG_TITLE, VALID_INPUT_TITLE, INVALID_PARAM_TITLE,\
    SCHEMA_VALIDATION_TITLE, STATUS_MISMATCH_ERROR
    

@pytest.mark.check_health
@pytest.mark.success
def test_check_health_success(valid_configuration, connector_details):
    set_report_metadata(connector_details, "Health Check", VALID_CONFIG_TITLE)
    result = run_health_check_success(valid_configuration, connector_details)
    assert result.get('status', '').lower() == 'available',\
        STATUS_MISMATCH_ERROR.format(expected='available', result=pformat(result))
    

@pytest.mark.check_health
@pytest.mark.invalid_input
def test_check_health_invalid_client_secret(invalid_configuration, connector_id, connector_details, params_json):
    set_report_metadata(connector_details, "Health Check", INVALID_PARAM_TITLE.format(param='Application (Client) Secret'))
    result = run_invalid_config_test(invalid_configuration, connector_id, connector_details, param_name='client_secret',
                                     param_type='password', config=params_json['config'])
    assert result.get('status', '').lower() == "disconnected",\
        STATUS_MISMATCH_ERROR.format(expected='disconnected', result=pformat(result))
    

@pytest.mark.check_health
@pytest.mark.invalid_input
def test_check_health_invalid_tenant_id(invalid_configuration, connector_id, connector_details, params_json):
    set_report_metadata(connector_details, "Health Check", INVALID_PARAM_TITLE.format(param='Directory (tenant) ID'))
    result = run_invalid_config_test(invalid_configuration, connector_id, connector_details, param_name='tenant_id',
                                     param_type='text', config=params_json['config'])
    assert result.get('status', '').lower() == "disconnected",\
        STATUS_MISMATCH_ERROR.format(expected='disconnected', result=pformat(result))
    

@pytest.mark.check_health
@pytest.mark.invalid_input
def test_check_health_invalid_client_id(invalid_configuration, connector_id, connector_details, params_json):
    set_report_metadata(connector_details, "Health Check", INVALID_PARAM_TITLE.format(param='Application (client) ID'))
    result = run_invalid_config_test(invalid_configuration, connector_id, connector_details, param_name='client_id',
                                     param_type='text', config=params_json['config'])
    assert result.get('status', '').lower() == "disconnected",\
        STATUS_MISMATCH_ERROR.format(expected='disconnected', result=pformat(result))
    

@pytest.mark.get_unread_emails
@pytest.mark.success
def test_get_unread_emails_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Unread Emails", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='get_unread_emails',
                                   action_params=params_json['get_unread_emails']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.get_unread_emails
@pytest.mark.schema_validation
def test_validate_get_unread_emails_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Get Unread Emails", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'get_unread_emails', info_json, params_json['get_unread_emails'])
    

@pytest.mark.get_unread_emails
@pytest.mark.invalid_input
def test_get_unread_emails_invalid_limit(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Unread Emails", INVALID_PARAM_TITLE.format(param='Limit'))
    result = run_invalid_param_test(connector_details, operation_name='get_unread_emails', param_name='limit',
                                    param_type='integer', action_params=params_json['get_unread_emails'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.get_unread_emails
@pytest.mark.invalid_input
def test_get_unread_emails_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Unread Emails", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='get_unread_emails', param_name='user_id',
                                    param_type='text', action_params=params_json['get_unread_emails'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.get_unread_emails
@pytest.mark.invalid_input
def test_get_unread_emails_invalid_folder_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Unread Emails", INVALID_PARAM_TITLE.format(param='Folder Path'))
    result = run_invalid_param_test(connector_details, operation_name='get_unread_emails', param_name='folder_id',
                                    param_type='text', action_params=params_json['get_unread_emails'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.search_emails
@pytest.mark.success
def test_search_emails_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Search Emails", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='search_emails',
                                   action_params=params_json['search_emails']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.search_emails
@pytest.mark.schema_validation
def test_validate_search_emails_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Search Emails", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'search_emails', info_json, params_json['search_emails'])
    

@pytest.mark.search_emails
@pytest.mark.invalid_input
def test_search_emails_invalid_limit(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Search Emails", INVALID_PARAM_TITLE.format(param='Limit'))
    result = run_invalid_param_test(connector_details, operation_name='search_emails', param_name='limit',
                                    param_type='integer', action_params=params_json['search_emails'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.search_emails
@pytest.mark.invalid_input
def test_search_emails_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Search Emails", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='search_emails', param_name='user_id',
                                    param_type='text', action_params=params_json['search_emails'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.search_emails
@pytest.mark.invalid_input
def test_search_emails_invalid_search(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Search Emails", INVALID_PARAM_TITLE.format(param='Search'))
    result = run_invalid_param_test(connector_details, operation_name='search_emails', param_name='search',
                                    param_type='text', action_params=params_json['search_emails'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

    
@pytest.mark.search_emails
@pytest.mark.invalid_input
def test_search_emails_invalid_folder_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Search Emails", INVALID_PARAM_TITLE.format(param='Folder Path'))
    result = run_invalid_param_test(connector_details, operation_name='search_emails', param_name='folder_id',
                                    param_type='text', action_params=params_json['search_emails'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.get_folders
@pytest.mark.success
def test_get_folders_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Folders", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='get_folders',
                                   action_params=params_json['get_folders']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.get_folders
@pytest.mark.schema_validation
def test_validate_get_folders_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Get Folders", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'get_folders', info_json, params_json['get_folders'])
    

@pytest.mark.get_folders
@pytest.mark.invalid_input
def test_get_folders_invalid_limit(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Folders", INVALID_PARAM_TITLE.format(param='Limit'))
    result = run_invalid_param_test(connector_details, operation_name='get_folders', param_name='limit',
                                    param_type='integer', action_params=params_json['get_folders'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.get_folders
@pytest.mark.invalid_input
def test_get_folders_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Folders", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='get_folders', param_name='user_id',
                                    param_type='text', action_params=params_json['get_folders'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.get_child_folders
@pytest.mark.success
def test_get_child_folders_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Child Folders", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='get_child_folders',
                                   action_params=params_json['get_child_folders']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.get_child_folders
@pytest.mark.schema_validation
def test_validate_get_child_folders_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Get Child Folders", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'get_child_folders', info_json, params_json['get_child_folders'])
    

@pytest.mark.get_child_folders
@pytest.mark.invalid_input
def test_get_child_folders_invalid_limit(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Child Folders", INVALID_PARAM_TITLE.format(param='Limit'))
    result = run_invalid_param_test(connector_details, operation_name='get_child_folders', param_name='limit',
                                    param_type='integer', action_params=params_json['get_child_folders'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.get_child_folders
@pytest.mark.invalid_input
def test_get_child_folders_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Child Folders", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='get_child_folders', param_name='user_id',
                                    param_type='text', action_params=params_json['get_child_folders'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.get_child_folders
@pytest.mark.invalid_input
def test_get_child_folders_invalid_folder_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Child Folders", INVALID_PARAM_TITLE.format(param='Folder Path'))
    result = run_invalid_param_test(connector_details, operation_name='get_child_folders', param_name='folder_id',
                                    param_type='text', action_params=params_json['get_child_folders'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.move_email
@pytest.mark.success
def test_move_email_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Move Email", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='move_email',
                                   action_params=params_json['move_email']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.move_email
@pytest.mark.schema_validation
def test_validate_move_email_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Move Email", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'move_email', info_json, params_json['move_email'])


@pytest.mark.move_email
@pytest.mark.invalid_input
def test_move_email_invalid_message_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Move Email", INVALID_PARAM_TITLE.format(param='Message ID'))
    result = run_invalid_param_test(connector_details, operation_name='move_email', param_name='message_id',
                                    param_type='text', action_params=params_json['move_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.move_email
@pytest.mark.invalid_input
def test_move_email_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Move Email", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='move_email', param_name='user_id',
                                    param_type='text', action_params=params_json['move_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.move_email
@pytest.mark.invalid_input
def test_move_email_invalid_folder_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Move Email", INVALID_PARAM_TITLE.format(param='Folder Path'))
    result = run_invalid_param_test(connector_details, operation_name='move_email', param_name='folder_id',
                                    param_type='text', action_params=params_json['move_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.copy_email
@pytest.mark.success
def test_copy_email_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Copy Email", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='copy_email',
                                   action_params=params_json['copy_email']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.copy_email
@pytest.mark.schema_validation
def test_validate_copy_email_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Copy Email", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'copy_email', info_json, params_json['copy_email'])
    

@pytest.mark.copy_email
@pytest.mark.invalid_input
def test_copy_email_invalid_message_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Copy Email", INVALID_PARAM_TITLE.format(param='Message ID'))
    result = run_invalid_param_test(connector_details, operation_name='copy_email', param_name='message_id',
                                    param_type='text', action_params=params_json['copy_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.copy_email
@pytest.mark.invalid_input
def test_copy_email_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Copy Email", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='copy_email', param_name='user_id',
                                    param_type='text', action_params=params_json['copy_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.copy_email
@pytest.mark.invalid_input
def test_copy_email_invalid_folder_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Copy Email", INVALID_PARAM_TITLE.format(param='Folder Path'))
    result = run_invalid_param_test(connector_details, operation_name='copy_email', param_name='folder_id',
                                    param_type='text', action_params=params_json['copy_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.delete_email
@pytest.mark.success
def test_delete_email_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Delete Email", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='delete_email',
                                   action_params=params_json['delete_email']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.delete_email
@pytest.mark.schema_validation
def test_validate_delete_email_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Delete Email", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'delete_email', info_json, params_json['delete_email'])


@pytest.mark.delete_email
@pytest.mark.invalid_input
def test_delete_email_invalid_message_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Delete Email", INVALID_PARAM_TITLE.format(param='Message ID'))
    result = run_invalid_param_test(connector_details, operation_name='delete_email', param_name='message_id',
                                    param_type='text', action_params=params_json['delete_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.delete_email
@pytest.mark.invalid_input
def test_delete_email_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Delete Email", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='delete_email', param_name='user_id',
                                    param_type='text', action_params=params_json['delete_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.delete_email
@pytest.mark.invalid_input
def test_delete_email_invalid_folder_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Delete Email", INVALID_PARAM_TITLE.format(param='Folder Path'))
    result = run_invalid_param_test(connector_details, operation_name='delete_email', param_name='folder_id',
                                    param_type='text', action_params=params_json['delete_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.send_email
@pytest.mark.success
def test_send_email_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Email", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='send_email',
                                   action_params=params_json['send_email']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.send_email
@pytest.mark.schema_validation
def test_validate_send_email_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Send Email", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'send_email', info_json, params_json['send_email'])
    

@pytest.mark.send_email
@pytest.mark.invalid_input
def test_send_email_invalid_cc_recipients(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Email", INVALID_PARAM_TITLE.format(param='Cc Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='send_email', param_name='cc_recipients',
                                    param_type='text', action_params=params_json['send_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email
@pytest.mark.invalid_input
def test_send_email_invalid_bcc_recipients(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Email", INVALID_PARAM_TITLE.format(param='Bcc Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='send_email', param_name='bcc_recipients',
                                    param_type='text', action_params=params_json['send_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email
@pytest.mark.invalid_input
def test_send_email_invalid_from(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Email", INVALID_PARAM_TITLE.format(param='From'))
    result = run_invalid_param_test(connector_details, operation_name='send_email', param_name='from',
                                    param_type='text', action_params=params_json['send_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email
@pytest.mark.invalid_input
def test_send_email_invalid_iri_list(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Email", INVALID_PARAM_TITLE.format(param='Attachment IRIs'))
    result = run_invalid_param_test(connector_details, operation_name='send_email', param_name='iri_list',
                                    param_type='text', action_params=params_json['send_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email
@pytest.mark.invalid_input
def test_send_email_invalid_to_recipients(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Email", INVALID_PARAM_TITLE.format(param='To Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='send_email', param_name='to_recipients',
                                    param_type='text', action_params=params_json['send_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    


@pytest.mark.forward_email
@pytest.mark.success
def test_forward_email_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Forward Email", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='forward_email',
                                   action_params=params_json['forward_email']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.forward_email
@pytest.mark.schema_validation
def test_validate_forward_email_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Forward Email", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'forward_email', info_json, params_json['forward_email'])
    

@pytest.mark.forward_email
@pytest.mark.invalid_input
def test_forward_email_invalid_message_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Forward Email", INVALID_PARAM_TITLE.format(param='Message ID'))
    result = run_invalid_param_test(connector_details, operation_name='forward_email', param_name='message_id',
                                    param_type='text', action_params=params_json['forward_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.forward_email
@pytest.mark.invalid_input
def test_forward_email_invalid_from_recipients(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Forward Email", INVALID_PARAM_TITLE.format(param='From Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='forward_email', param_name='from_recipients',
                                    param_type='text', action_params=params_json['forward_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.forward_email
@pytest.mark.invalid_input
def test_forward_email_invalid_to_recipients(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Forward Email", INVALID_PARAM_TITLE.format(param='To Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='forward_email', param_name='to_recipients',
                                    param_type='text', action_params=params_json['forward_email'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email_as_reply
@pytest.mark.success
def test_send_email_as_reply_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Mail as Reply", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='send_email_as_reply',
                                   action_params=params_json['send_email_as_reply']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.send_email_as_reply
@pytest.mark.schema_validation
def test_validate_send_email_as_reply_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Send Mail as Reply", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'send_email_as_reply', info_json, params_json['send_email_as_reply'])


@pytest.mark.send_email_as_reply
@pytest.mark.invalid_input
def test_send_email_as_reply_invalid_message_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Mail as Reply", INVALID_PARAM_TITLE.format(param='Message ID'))
    result = run_invalid_param_test(connector_details, operation_name='send_email_as_reply', param_name='message_id',
                                    param_type='text', action_params=params_json['send_email_as_reply'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email_as_reply
@pytest.mark.invalid_input
def test_send_email_as_reply_invalid_cc_recipients(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Mail as Reply", INVALID_PARAM_TITLE.format(param='Cc Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='send_email_as_reply', param_name='cc_recipients',
                                    param_type='text', action_params=params_json['send_email_as_reply'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email_as_reply
@pytest.mark.invalid_input
def test_send_email_as_reply_invalid_from_recipients(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Mail as Reply", INVALID_PARAM_TITLE.format(param='From Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='send_email_as_reply', param_name='from_recipients',
                                    param_type='text', action_params=params_json['send_email_as_reply'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email_as_reply
@pytest.mark.invalid_input
def test_send_email_as_reply_invalid_bcc_recipients(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Mail as Reply", INVALID_PARAM_TITLE.format(param='Bcc Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='send_email_as_reply', param_name='bcc_recipients',
                                    param_type='text', action_params=params_json['send_email_as_reply'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email_as_reply
@pytest.mark.invalid_input
def test_send_email_as_reply_invalid_iri_list(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Mail as Reply", INVALID_PARAM_TITLE.format(param='Attachment IRIs'))
    result = run_invalid_param_test(connector_details, operation_name='send_email_as_reply', param_name='iri_list',
                                    param_type='text', action_params=params_json['send_email_as_reply'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.send_email_as_reply
@pytest.mark.invalid_input
def test_send_email_as_reply_invalid_to(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Send Mail as Reply", INVALID_PARAM_TITLE.format(param='To Recipients'))
    result = run_invalid_param_test(connector_details, operation_name='send_email_as_reply', param_name='to',
                                    param_type='text', action_params=params_json['send_email_as_reply'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.create_email_threat_submission
@pytest.mark.success
def test_create_email_threat_submission_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Create Email Threat Submission", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='create_email_threat_submission',
                                   action_params=params_json['create_email_threat_submission']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.create_email_threat_submission
@pytest.mark.schema_validation
def test_validate_create_email_threat_submission_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Create Email Threat Submission", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'create_email_threat_submission', info_json, params_json['create_email_threat_submission'])


@pytest.mark.create_email_threat_submission
@pytest.mark.invalid_input
def test_create_email_threat_submission_invalid_filecontent(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Create Email Threat Submission", INVALID_PARAM_TITLE.format(param='File Content'))
    result = run_invalid_param_test(connector_details, operation_name='create_email_threat_submission', param_name='fileContent',
                                    param_type='text', action_params=params_json['create_email_threat_submission'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.create_email_threat_submission
@pytest.mark.invalid_input
def test_create_email_threat_submission_invalid_other_params(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Create Email Threat Submission", INVALID_PARAM_TITLE.format(param='Other Parameters'))
    result = run_invalid_param_test(connector_details, operation_name='create_email_threat_submission', param_name='other_params',
                                    param_type='json', action_params=params_json['create_email_threat_submission'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.create_email_threat_submission
@pytest.mark.invalid_input
def test_create_email_threat_submission_invalid__odata_type(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Create Email Threat Submission", INVALID_PARAM_TITLE.format(param='Data Type'))
    result = run_invalid_param_test(connector_details, operation_name='create_email_threat_submission', param_name='@odata.type',
                                    param_type='text', action_params=params_json['create_email_threat_submission'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.create_email_threat_submission
@pytest.mark.invalid_input
def test_create_email_threat_submission_invalid_recipientemailaddress(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Create Email Threat Submission", INVALID_PARAM_TITLE.format(param='Recipient Email Address'))
    result = run_invalid_param_test(connector_details, operation_name='create_email_threat_submission', param_name='recipientEmailAddress',
                                    param_type='text', action_params=params_json['create_email_threat_submission'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.get_email_categories
@pytest.mark.success
def test_get_email_categories_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Email Categories", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='get_email_categories',
                                   action_params=params_json['get_email_categories']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.get_email_categories
@pytest.mark.schema_validation
def test_validate_get_email_categories_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Get Email Categories", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'get_email_categories', info_json, params_json['get_email_categories'])
    

@pytest.mark.get_email_categories
@pytest.mark.invalid_input
def test_get_email_categories_invalid_message_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Email Categories", INVALID_PARAM_TITLE.format(param='Message ID'))
    result = run_invalid_param_test(connector_details, operation_name='get_email_categories', param_name='message_id',
                                    param_type='text', action_params=params_json['get_email_categories'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.get_email_categories
@pytest.mark.invalid_input
def test_get_email_categories_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Get Email Categories", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='get_email_categories', param_name='user_id',
                                    param_type='text', action_params=params_json['get_email_categories'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.add_email_category
@pytest.mark.success
def test_add_email_category_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Add Email Category", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='add_email_category',
                                   action_params=params_json['add_email_category']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.add_email_category
@pytest.mark.schema_validation
def test_validate_add_email_category_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Add Email Category", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'add_email_category', info_json, params_json['add_email_category'])
    

@pytest.mark.add_email_category
@pytest.mark.invalid_input
def test_add_email_category_invalid_message_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Add Email Category", INVALID_PARAM_TITLE.format(param='Message ID'))
    result = run_invalid_param_test(connector_details, operation_name='add_email_category', param_name='message_id',
                                    param_type='text', action_params=params_json['add_email_category'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.add_email_category
@pytest.mark.invalid_input
def test_add_email_category_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Add Email Category", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='add_email_category', param_name='user_id',
                                    param_type='text', action_params=params_json['add_email_category'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    


@pytest.mark.remove_email_category
@pytest.mark.success
def test_remove_email_category_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Remove Email Category", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='remove_email_category',
                                   action_params=params_json['remove_email_category']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))


@pytest.mark.remove_email_category
@pytest.mark.schema_validation
def test_validate_remove_email_category_output_schema(cache, valid_configuration_with_token, connector_details,
                                                 info_json, params_json):
    set_report_metadata(connector_details, "Remove Email Category", SCHEMA_VALIDATION_TITLE)
    run_output_schema_validation(cache, 'remove_email_category', info_json, params_json['remove_email_category'])
    

@pytest.mark.remove_email_category
@pytest.mark.invalid_input
def test_remove_email_category_invalid_message_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Remove Email Category", INVALID_PARAM_TITLE.format(param='Message ID'))
    result = run_invalid_param_test(connector_details, operation_name='remove_email_category', param_name='message_id',
                                    param_type='text', action_params=params_json['remove_email_category'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.remove_email_category
@pytest.mark.invalid_input
def test_remove_email_category_invalid_user_id(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Remove Email Category", INVALID_PARAM_TITLE.format(param='User ID/User Principal Name'))
    result = run_invalid_param_test(connector_details, operation_name='remove_email_category', param_name='user_id',
                                    param_type='text', action_params=params_json['remove_email_category'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    


@pytest.mark.execute_api_request
@pytest.mark.success
def test_execute_api_request_success(cache, valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Execute an API Request", VALID_INPUT_TITLE)
    for result in run_success_test(cache, connector_details, operation_name='execute_api_request',
                                   action_params=params_json['execute_api_request']):
        assert result.get('status') == "Success",\
            STATUS_MISMATCH_ERROR.format(expected='Success', result=pformat(result))



@pytest.mark.execute_api_request
@pytest.mark.invalid_input
def test_execute_api_request_invalid_endpoint(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Execute an API Request", INVALID_PARAM_TITLE.format(param='Endpoint'))
    result = run_invalid_param_test(connector_details, operation_name='execute_api_request', param_name='endpoint',
                                    param_type='text', action_params=params_json['execute_api_request'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))
    

@pytest.mark.execute_api_request
@pytest.mark.invalid_input
def test_execute_api_request_invalid_payload(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Execute an API Request", INVALID_PARAM_TITLE.format(param='Payload'))
    result = run_invalid_param_test(connector_details, operation_name='execute_api_request', param_name='payload',
                                    param_type='json', action_params=params_json['execute_api_request'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))


@pytest.mark.execute_api_request
@pytest.mark.invalid_input
def test_execute_api_request_invalid_query_parameters(valid_configuration_with_token, connector_details, params_json):
    set_report_metadata(connector_details, "Execute an API Request", INVALID_PARAM_TITLE.format(param='query_params'))
    result = run_invalid_param_test(connector_details, operation_name='execute_api_request', param_name='Query Parameters',
                                    param_type='json', action_params=params_json['execute_api_request'])
    assert result.get('status') == "failed",\
        STATUS_MISMATCH_ERROR.format(expected='failed', result=pformat(result))

