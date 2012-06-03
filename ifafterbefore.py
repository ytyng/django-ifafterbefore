# -*- coding: utf-8 -*-

"""
時間を判定して表示分岐させるテンプレートタグ
例:
{% ifbefore '2011-12-24 20:00:00' %}
    ここは 2011-12-24 20:00:00 未満に表示される
{% else %}
    ここは 2011-12-24 20:00:00 以後に表示される
{% endifbefore %}

引数は、datetimeの他、
'%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S' 形式の日付文字列が使える
"""

from django import forms, template
from django.template import NodeList
from django.template.defaulttags import TemplateIfParser

register = template.Library()

class IfAfterBeforeNode(Node):
    child_nodelists = ('nodelist_true', 'nodelist_false')
    datestr_format_list = ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S')

    def __init__(self, var_after, var_before, nodelist_true, nodelist_false=None):
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.var_after = var_after
        self.var_before = var_before
        self.now = datetime.datetime.now()

    def strptime(self, date_string):
        """
        日付文字列をパースしてdatetimeにする。
        パースできなければNone
        """
        date_string = date_string.strip("""'" """)
        for datestr_format in self.datestr_format_list:
            try:
                return datetime.datetime.strptime(date_string, datestr_format)
            except ValueError:
                pass
        return None

    def __repr__(self):
        return "<IfBeforeAfter node>"

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def arg_to_dt_or_none(self, arg, context):
        """
        引数を datetime もしくは none として取得
        self.var_after, self.var_before に使う
        """
        if not arg:
            return None
        try:
            # 引数がdatetimeの場合があるので
            dt = resolve_variable(arg, context)
        except template.VariableDoesNotExist:
            dt  = None
        if dt is None or not isinstance(dt,  datetime.datetime):
            dt = self.strptime(arg)
        return dt

    def render(self, context):
        
        dt_after  = self.arg_to_dt_or_none(self.var_after,  context)
        dt_before = self.arg_to_dt_or_none(self.var_before, context)
        
        if dt_after and dt_before:
            if dt_after <= self.now < dt_before:
                return self.nodelist_true.render(context)
            else:
                return self.nodelist_false.render(context)
        elif dt_after:
            if dt_after <= self.now:
                return self.nodelist_true.render(context)
            else:
                return self.nodelist_false.render(context)
        elif dt_before:
            if self.now < dt_before:
                return self.nodelist_true.render(context)
            else:
                return self.nodelist_false.render(context)
        else:
            return u'Parse Error. No after, before'

@register.tag
def ifbefore(parser, token):
    """
    現在日時が"YYYY-MM-DD HH:MM:SS" より前(未満)であればレンダリング
    """
    _tagname, var_before = token.split_contents()
    nodelist_true = parser.parse(('else', 'endifbefore'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifbefore',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfAfterBeforeNode(None, var_before, nodelist_true, nodelist_false)

@register.tag
def ifafter(parser, token):
    """
    現在日時が"YYYY-MM-DD HH:MM:SS" より後(以上)であればレンダリング
    """
    _tagname, var_after = token.split_contents()
    nodelist_true = parser.parse(('else', 'endifafter'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifafter',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfAfterBeforeNode(var_after, None, nodelist_true, nodelist_false)

@register.tag
def ifafterbefore(parser, token):
    """
    2つの引数をとり、現在時刻がその以上未満であればレンダリング
    """
    _tagname, var_after, var_before = token.split_contents()
    
    nodelist_true = parser.parse(('else', 'endifafterbefore'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifafterbefore',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfAfterBeforeNode(var_after, var_before, nodelist_true, nodelist_false)

