# -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (c) 2025 tmistones.com
#
###################################################################################

{
    "name": "Import CV PDF file",
    "summary": """Easy import CV PDF file to Odoo""",
    "version": "18.0.1.0.0",
    'category': 'Human Resources/Recruitment',
    "website": "https://tmistones.com",
    'live_test_url': 'https://cv-import.tmistones.com',
    "author": "TMI Teamwork",
    "contributors": [
        u"Nguyen Quoc Khanh <https://github.com/KhanhNguyen82>",

    ],
    "depends": [
        "hr_recruitment",
    ],
    "data": [
        "security/ir.model.access.csv",
        'views/candidate_import_wizard_view.xml',
        'views/hr_candidate.xml',
        'views/cronjob.xml',
        #"views/res_config_setting.xml",
        #"data/data.xml",
        #"views/assets.xml",
    ],
    'assets': {
        "web.assets_common": [
                "import_pdf_cv/static/src/js/promise_polyfill.js",
                "import_pdf_cv/static/src/js/directory_uploader.js",
                "import_pdf_cv/static/src/js/multi_file_upload_2.js",
                "import_pdf_cv/static/src/js/upload_notif.js",
                "import_pdf_cv/static/src/xml/directory_uploader.xml",
                "import_pdf_cv/static/src/xml/multi_file_upload.xml",
                #"import_pdf_cv/static/src/js/file_uploader_patch.js",
                #"import_pdf_cv/static/src/js/multi_upload_file_pdf.js",
                #"import_pdf_cv/static/src/xml/multi_file_upload_2.xml",
            ],
        'web.assets_backend': [
                "import_pdf_cv/static/src/js/promise_polyfill.js",
                "import_pdf_cv/static/src/js/directory_uploader.js",
                "import_pdf_cv/static/src/js/multi_file_upload_2.js",
                "import_pdf_cv/static/src/js/upload_notif.js",
                "import_pdf_cv/static/src/xml/directory_uploader.xml",
                "import_pdf_cv/static/src/xml/multi_file_upload.xml",
                #"import_pdf_cv/static/src/js/file_uploader_patch.js",
                #"import_pdf_cv/static/src/js/multi_file_upload.js",
                #"import_pdf_cv/static/src/js/multi_upload_file_pdf.js",
                #"import_pdf_cv/static/src/xml/multi_file_upload.xml",
                #"import_pdf_cv/static/src/xml/multi_file_upload_2.xml",
        ],
    },
    'demo': [
    ],

    "images": [],
    "external_dependencies": {},
    "application": True,
    "installable": True,
    
}

