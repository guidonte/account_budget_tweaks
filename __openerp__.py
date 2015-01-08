{
    'name': 'Account Budget Tweaks - Goodora',
    'description': 'Tweaks for budgets by Goodora s.r.l.',
    'author': 'Goodora s.r.l.',
    'version': '0.1',
    'category': 'Hidden',
    'depends': [
        'account',
        'account_budget',
    ],
    'data': [
        'wizard/account_budget_lines_view.xml',
        'account_budget_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}

