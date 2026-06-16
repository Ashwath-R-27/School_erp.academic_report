DASHBOARD_CONFIGS = {
    "main": {
        "title": "Quick Navigation",
        "type": "cards",
        "notice": "<ul><li>Examination Results Portal will be opened shortly.</li> <li>Please share the forms to students and ask them to fill it.</li></ul>",
        "cards": [
            {"href": "/home", "icon": "🎓", "title": "Examination Results 2026", "desc": "Examination result portal."},
            {"href": "/dashboard/HSC/StudentForm", "icon": "👨‍🎓", "title": "HSC Student Form", "desc": "Collect HSC student roll nos."},
            {"href": "/dashboard/SSLC/StudentForm", "icon": "👩‍🎓", "title": "SSLC Student Form", "desc": "Collect SSLC student roll nos."},
            {"href": "/dashboard/Services", "icon": "⚙️", "title": "Services", "desc": "Ask for Services."},
        ]
    },
    "HSC/StudentForm": {
        "title": "HSC Student Form",
        "type": "cards",
        "cards": [
            {"href": "/dashboard/HSC_2026/StudForm/Responses", "icon": "📑", "title": "Form Responses", "desc": "Student roll nos. and details"},
            {"href": "/HSC_2026/StudForm", "icon": "📝", "title": "Student Form", "desc": "Share the link to students."}
        ]
    },
    "SSLC/StudentForm": {
        "title": "SSLC Student Form",
        "type": "cards",
        "cards": [
            {"href": "/dashboard/SSLC_2026/StudForm/Responses", "icon": "📑", "title": "Form Responses", "desc": "Student roll nos. and details"},
            {"href": "/SSLC_2026/StudForm", "icon": "📝", "title": "Student Form", "desc": "Share the link to students."}
        ]
    },
    "Services":{
        "title": "Services",
        "type": "custom_div",
        "content": "<div class='error-notice'>No Services at this moment.</div>"
    },
    "HSC_2026/StudForm/Responses":{
        "title": "HSC Student Details",
        "notice": "This page is still being devloped by the team.",
        "type": "custom_div",
        "content": ""
    },
    "SSLC_2026/StudForm/Responses":{
        "title": "SSLC Student Details",
        "notice": "This page is still being devloped by the team.",
        "type": "custom_div",
        "content": ""
    }
}