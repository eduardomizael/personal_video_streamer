from django import template
from django.template.loader import get_template

register = template.Library()


@register.simple_tag
def component(template_path):
    template = get_template(template_path)
    return template.render()


@register.tag
def subblock(parser, token):
    nodelist = parser.parse(('endsubblock',))
    # print(token)
    parser.delete_first_token()
    # print(nodelist)
    # print(token)
    # print(SubBlockNode(nodelist))
    return SubBlockNode(nodelist)


@register.tag
def endsubblock(parser, token):
    parser.delete_first_token()
    return None


class SubBlockNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return self.nodelist.render(context)

