{
    "name": "Open PDF Reports and PDF Attachments in Browser",
    "version": "16.0.1.0.3",
    "summary": """
    Preview reports and pdf attachments in browser instead of downloading them.
    Open Report or PDF Attachment in new tab instead of downloading.""",
    "author": "Snine",
    "category": "Productivity",
    "license": "LGPL-3",
    "website": "https://snine.vn",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "s_attachment_preview/static/src/js/tools.esm.js",
            "s_attachment_preview/static/src/js/report.esm.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
