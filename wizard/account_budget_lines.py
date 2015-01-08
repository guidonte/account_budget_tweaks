# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _

from collections import defaultdict
import time


class account_budget_lines_wizard (osv.osv_memory):

    _name = 'account.budget.tweaks.lines'
    _description = 'Add budget lines'
    _columns = {
        'date_from': fields.date ('Start Date', required=True),
        'date_to': fields.date ('End Date', required=True),
        'analytic_account_ids': fields.many2many ('account.analytic.account',
            'wizard_analytic_account_rel', 'wizard_id', 'analytic_account_id', 'Analytic Accounts',
            domain=[
                ('type', 'in', ['normal', 'contract']),
                ('state', 'not in', ['close', 'cancelled']),
            ],
        ),
        'general_budget_ids': fields.many2many ('account.budget.post',
            'wizard_general_budget_rel', 'wizard_id', 'general_budget_id', 'Budgetary positions'),
    }
    _defaults= {
        'date_from': lambda *a: time.strftime ('%Y-01-01'),
        'date_to': lambda *a: time.strftime ('%Y-12-31'),
        'analytic_account_ids': lambda *a: [], # FIXME
        'general_budget_ids': lambda *a: [], # FIXME
    }

    def add_lines (self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = self.read (cr, uid, ids, context=context)[0]

        active_budget = self.pool.get (context['active_model']).browse (cr, uid, context['active_id'])

        def tree (): return defaultdict (tree)

        existing_lines = tree ()
        for line in active_budget.crossovered_budget_line:
            analytic_account_id = line.analytic_account_id.id if line.analytic_account_id else None
            existing_lines[line.general_budget_id.id][analytic_account_id] = line

        for general_budget_id in data['general_budget_ids']:
            for analytic_account_id in data['analytic_account_ids']:
                if existing_lines[general_budget_id][analytic_account_id]:
                    continue

                line = self.pool.get ('crossovered.budget.lines').create (cr, uid, {
                    'crossovered_budget_id': active_budget.id,
                    'company_id': active_budget.company_id.id,
                    'general_budget_id': general_budget_id,
                    'analytic_account_id': analytic_account_id,
                    'date_from': data['date_from'],
                    'date_to': data['date_to'],
                    'planned_amount': 0,
                }, context)

        return {'type': 'ir.actions.act_window_close'}

