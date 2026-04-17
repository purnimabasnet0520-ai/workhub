from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "WorkHub Admin",
    "SITE_HEADER": "WorkHub",
    "SITE_LOGO": "/media/system_image/logo1.png",
    "SITE_SYMBOL": "work",
    "COLORS": {
        "primary": {
            "50": "236 254 255",
            "100": "207 250 254",
            "200": "165 243 252",
            "300": "103 232 249",
            "400": "34 211 238",
            "500": "6 182 212",
            "600": "8 145 178", # Cyan-600
            "700": "14 116 144",
            "800": "21 94 117",
            "900": "22 78 99",
            "950": "8 47 60",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "User Management",
                "items": [
                    {
                        "title": "Internal Users",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                        "icon": "person",
                        "actions": [
                            {
                                "title": "+ User",
                                "link": reverse_lazy("admin:auth_user_add"),
                            }
                        ],
                    },
                    {
                        "title": "User Profiles",
                        "link": reverse_lazy("admin:users_profile_changelist"),
                        "icon": "account_circle",
                        "actions": [
                            {
                                "title": "+ Profile",
                                "link": reverse_lazy("admin:users_profile_add"),
                            }
                        ],
                    },
                ],
            },
            {
                "title": "Recruitment board",
                "items": [
                    {
                        "title": "Posted Jobs",
                        "link": reverse_lazy("admin:jobs_job_changelist"),
                        "icon": "work_outline",
                        "actions": [
                            {
                                "title": "+ Job",
                                "link": reverse_lazy("admin:jobs_job_add"),
                            }
                        ],
                    },
                    {
                        "title": "Companies",
                        "link": reverse_lazy("admin:companies_company_changelist"),
                        "icon": "business",
                        "actions": [
                            {
                                "title": "+ Company",
                                "link": reverse_lazy("admin:companies_company_add"),
                            }
                        ],
                    },
                    {
                        "title": "Job Applications",
                        "link": reverse_lazy("admin:applications_application_changelist"),
                        "icon": "assignment_ind",
                    },
                ],
            },
            {
                "title": "Data & Logs",
                "items": [
                    {
                        "title": "Verification Codes",
                        "link": reverse_lazy("admin:notifications_verificationcode_changelist"),
                        "icon": "password",
                        "actions": [
                            {
                                "title": "+ Code",
                                "link": reverse_lazy("admin:notifications_verificationcode_add"),
                            }
                        ],
                    },
                    {
                        "title": "System Notifications",
                        "link": reverse_lazy("admin:notifications_usernotification_changelist"),
                        "icon": "notifications",
                        "actions": [
                            {
                                "title": "+ Notification",
                                "link": reverse_lazy("admin:notifications_usernotification_add"),
                            }
                        ],
                    },
                    {
                        "title": "Skills List",
                        "link": reverse_lazy("admin:skills_skill_changelist"),
                        "icon": "psychology",
                        "actions": [
                            {
                                "title": "+ Skill",
                                "link": reverse_lazy("admin:skills_skill_add"),
                            }
                        ],
                    },
                ],
            },
        ],
    },
    "STYLES": [
        "/static/admin/css/unfold-custom.css",
    ],
}
