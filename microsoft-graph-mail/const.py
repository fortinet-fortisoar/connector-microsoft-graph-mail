"""
Copyright start
Copyright (C) 2008 - 2025 FortinetInc.
All rights reserved.
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
Copyright end
"""

WELL_KNOWN_FOLDERS = {
    'archive': 'archive',
    'conversation history': 'conversationhistory',
    'deleted items': 'deleteditems',
    'drafts': 'drafts',
    'inbox': 'inbox',
    'junk email': 'junkemail',
    'outbox': 'outbox',
    'recover deleted items': 'recoverableitemsdeletions',
    'sent items': 'sentitems',
}

FLAG_STATUS = {
    "Not Flagged": "notFlagged",
    "Flagged": "flagged",
    "Complete": "complete"
}

IMPORTANCE = {
    "Low": "low",
    "Normal": "normal",
    "High": "high"
}

CATEGORY = {
    "Not Junk": "notJunk",
    "Spam": "spam",
    "Phishing": "phishing",
    "Malware": "malware",
    "Unknown Future Value": "unknownFutureValue"
}

DEFAULT_MESSAGE_LIMIT = 20
DEFAULT_FOLDER_LIMIT = 100
TMP_FILE_ROOT = '/tmp/'
DEFAULT_FOLDER = 'Inbox'
FILE_ATTACHMENT = '#microsoft.graph.fileAttachment'
INLINE_ATTACHMENT = '#microsoft.graph.outlookItem'
ITEM_ATTACHMENT = '#microsoft.graph.itemAttachment'

# access token constant

SCOPE = ['Mail.Read', 'Mail.ReadWrite']
# authorization types
AUTH_BEHALF_OF_USER = "On behalf of User - Delegated Permission"
AUTH_USING_APP = "Without a User - Application Permission"

# redirect url
DEFAULT_REDIRECT_URL = 'https://localhost/myapp'
REFRESH_TOKEN_FLAG = False