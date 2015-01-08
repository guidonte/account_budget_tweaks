# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _


class crossovered_budget (osv.osv):

    _inherit = 'crossovered.budget'
    _columns = {
        'summary_line_ids': fields.one2many ('account_budget_tweaks.summary_line', 'crossovered_budget_id', 'Summary lines',
                                             readonly=True),
    }

    def write (self, cr, uid, ids, vals, context=None):
        result = super (crossovered_budget, self).write (cr, uid, ids, vals, context=context)

        for budget in self.pool.get ('crossovered.budget').browse (cr, uid, ids):
            posts = set ([l.general_budget_id for l in budget.crossovered_budget_line])

            for post in posts:
                summary_id = self.pool.get ('account_budget_tweaks.summary_line').search (cr, uid, [
                    ('crossovered_budget_id', '=', budget.id),
                    ('general_budget_id', '=', post.id),
                ])

                if summary_id:
                    continue

                self.pool.get ('account_budget_tweaks.summary_line').create (cr, uid, {
                    'crossovered_budget_id': budget.id,
                    'general_budget_id': post.id,
                    'planned_amount': 0,
                    'practical_amount': 0,
                    'theoritical_amount': 0,
                }, context)

        return result

    def init (self, cr):
        Obj = self.pool.get ('crossovered.budget')

        for obj in Obj.browse (cr, 1, Obj.search (cr, 1, [])):
            obj.write ({})


class account_budget_summary_line (osv.osv):

    def _get_budget_lines (self, cr, uid, ids, context=None):
        budget_lines = self.pool.get ('crossovered.budget.lines').browse (cr, uid, ids)

        return self.pool.get ('account_budget_tweaks.summary_line').search (cr, uid, [
            ('crossovered_budget_id', 'in', [l.crossovered_budget_id.id for l in budget_lines]),
        ])

    def _get_amount (self, cr, uid, ids, names, args, context=None):
        res = {}

        summary_ids = self.pool.get ('account_budget_tweaks.summary_line').search (cr, uid, [])
        for summary_line in self.pool.get ('account_budget_tweaks.summary_line').browse (cr, uid, summary_ids):
            res[summary_line.id] = {
                'planned_amount': 0,
                'practical_amount': 0,
                'theoritical_amount': 0,
            }

            for line in summary_line.crossovered_budget_id.crossovered_budget_line:
                if line.general_budget_id != summary_line.general_budget_id:
                    continue

                res[summary_line.id]['planned_amount'] += line.planned_amount
                res[summary_line.id]['practical_amount'] += line.practical_amount
                res[summary_line.id]['theoritical_amount'] += line.theoritical_amount

        return res

    _name = 'account_budget_tweaks.summary_line'
    _description = 'Budget summary line'
    _columns = {
        'crossovered_budget_id': fields.many2one ('crossovered.budget', 'Budget', ondelete='cascade', required=True),
        'general_budget_id': fields.many2one ('account.budget.post', 'Budgetary Position', required=True),
        'planned_amount': fields.function (_get_amount,
            string='Planned Amount', type='float', multi="amount", store={
                'crossovered.budget.lines': (_get_budget_lines,
                    ['planned_amount', 'practical_amount', 'theoritical_amount'], 10),
                'account_budget_tweaks.summary_line': (lambda self, cr, uid, ids, context=None: ids,
                    [], 10),
            }),
        'practical_amount': fields.function (_get_amount,
            string='Practical Amount', type='float', multi="amount", store={
                'crossovered.budget.lines': (_get_budget_lines,
                    ['planned_amount', 'practical_amount', 'theoritical_amount'], 10),
                'account_budget_tweaks.summary_line': (lambda self, cr, uid, ids, context=None: ids,
                    [], 10),
            }),
        'theoritical_amount': fields.function (_get_amount,
            string='Theoretical Amount', type='float', multi="amount", store={
                'crossovered.budget.lines': (_get_budget_lines,
                    ['planned_amount', 'practical_amount', 'theoritical_amount'], 10),
                'account_budget_tweaks.summary_line': (lambda self, cr, uid, ids, context=None: ids,
                    [], 10),
            }),
    }

    def init (self, cr):
        Obj = self.pool.get ('account_budget_tweaks.summary_line')

        for obj in Obj.browse (cr, 1, Obj.search (cr, 1, [])):
            obj.write ({})

