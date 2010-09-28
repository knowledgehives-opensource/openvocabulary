import re

from django import template
from django.utils.safestring import mark_safe
from ov_django.ov.models import *
from ov_django.rdf import NAMESPACES, INV_NAMESPACE
from ov_django.settings import BASE_OV_PATH, BASE_URL_PATH

register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    "Removes all values of arg from the given string"
    return value.replace(arg, '')

@register.filter(name='get_short_name')
def get_short_name(value):
	"""
	Returns local name of given URI - the last after # or /
	"""
	name = re.sub("^.+[/#]([^/#]+)", "\\1", value)
	ns = re.sub("^(.+[/#])[^/#]+", "\\1", value)
	return INV_NAMESPACE[ns]+":"+name if (ns in INV_NAMESPACE) else name
	
@register.filter(name='get_label')
def get_label(predicate):
	if hasattr(predicate, 'label') and predicate.label:
		return predicate.label
	if hasattr(predicate, 'uri'):
		return get_short_name(predicate.uri)
	return str(predicate)
    
@register.filter
def expand_dict(value, arg):
    """
    Expands given value (=key) by retrieving new value from the dictionary of a given name (<- arg)
    """
    return eval(arg+"['"+value+"']")
    
@register.filter
def list(value):
    """
    Returns a list from a query set
    """
    if hasattr(value, 'all') and callable(value.all):
        return value.all()
    else:
        return []
    
RE_CUT_EMAIL =  re.compile("^(?P<name>[^@]+)[@](?P<host>[^@]+)$")
EMAIL_ENC_TEMPLATE = u"<script type='text/javascript'>\n/*<![CDATA[*/\n\tdocument.write('%s');\n\tdocument.write('@');\n\tdocument.write('%s');\n/*]]>*/\n</script>\n"    
        
@register.filter        
def hide_email(value):
    """
    replaces an email with encoded characters
    """
    dic = RE_CUT_EMAIL.match(value).groupdict()
    return EMAIL_ENC_TEMPLATE % (dic['name'], dic['host'])
    

NAMESPACE_RENDER_ENTRY = '\n\txmlns:%s="%s"'    
    
@register.filter    
def render_namespaces(value):
    """
    Renders given dictionary of namespaces into an HTML code
    """
    result = ""
    if hasattr(value, 'items') and callable(value.items):
        for ns, uri in value.items():
            result += NAMESPACE_RENDER_ENTRY % (ns, uri) 
    return result

@register.filter           
def get_rdfa(value, attr):
    """
    Renders RDFa attribute value for given property (=attr)
    """
    if attr=="_uri" and hasattr(value, 'get_uri') and callable(value.get_uri):
        result = value.get_uri()
    elif attr=="_type" and hasattr(value, 'get_rdf_types') and callable(value.get_rdf_types):
        rdf_types = value.get_rdf_types()
        result = " ".join(type_to_string(type) for type in rdf_types )
    elif hasattr(value, 'get_property_uris') and callable(value.get_property_uris):
        property_uris, rval = value.get_property_uris(attr)
        result = " ".join( type_to_string(type) for type in property_uris )
    return result

@register.filter
def get_literal_types(value, property):
    """
    Renders RDFa literal datatype/xml:lang attribute based on given property
    """
    if hasattr(value, "get_literal_type") and callable(value.get_literal_type):
        xsd = value.get_literal_type(property)
        if xsd:
            return "datatype=\"%s\"" % xsd
        
    if hasattr(value, "get_literal_lang") and callable(value.get_literal_lang):
        lang = value.get_literal_lang(property)
        if lang: 
            return "xml:lang='%s'" % lang
    
    return ""
    
@register.filter
def expand_to_ontology(value, dict):
    """
    Expands given object into an ontology URI
    """
    id = eval(dict+"['"+value+"']")
    return NAMESPACES["ov"]+"#"+re.sub('\s+', '', id)

@register.filter
def check_if_selected(value, current):
    return "current" if value == current else "id_"+current

@register.simple_tag
def count_by_type(value):
    """
    Counts contexts of given type
    """
    return str(len(Context.objects.filter(type=value)))

@register.simple_tag
def count_by_lang(value):
    """
    Counts contexts of given lang
    """
    return str(len(Context.objects.get_langs()))

@register.simple_tag
def count_by_tag(value):
    """
    Counts contexts of given tag
    """
    return str(len(Context.objects.filter(tags__label__exact=value)))

@register.filter
def expand_context_type(value):
    """
    Expands given short version of 
    """
    if value in DICT_CONTEXT_TYPE:
        return DICT_CONTEXT_TYPE[value]
    else:
        return ''

@register.filter
def is_native_ov(value):
    """
    Checks if given entry is from native OV 
    """
    return value.uri.startswith(BASE_URL_PATH)

@register.filter
def list_entry_relations(entry):
    """
    Lists all EntryRelation objects with given entry as subject
    """
    return EntryReference.objects.filter(subject=entry).order_by("relation")

@register.filter
def list_entry_triples(entry):
    """
    Lists all Triples with given entry as subject
    """
    return Triple.objects.filter(subject=entry).order_by("predicate")

@register.filter
def get_entry(uri):
    """
    Checks if given URI can be mapped to Entry object. Returns this object
    """    
    try:
        return Entry.objects.get(uri=uri.uri)
    except Entry.DoesNotExist, e:
        return None
    

@register.filter
def create_entry_anchor(entry, title):
    """
    Short hand for creating anchor for given referenced entry with given title 
    <a href="/vocabularies/lookup?uri={{ ref.object.uri }}" title="Show {{ ref.relation }}">{{ ref.object.get_label }}</a>
    """
    if is_native_ov(entry):
        template = "<a href='%s' title='%s'>%s</a>"
    else:
        template = "<a href='/vocabularies/lookup?uri=%s' title='%s'>%s</a>"
    return mark_safe(template % (_escape_apostrophe(entry.uri), title, _escape_apostrophe(entry.get_label())))

    
"""
shorthand function for replacing ' by \'
"""
def _escape_apostrophe(text):
    return text.replace("'", "\'")

    
    
"""
Shortcut function
"""
def type_to_string(type):
    return type.get_uri() if hasattr(type, 'get_uri') else type
           
          
                    
"""
@register.inclusion_tag('books_creator_template.html')    
def books_for_creator(creator):
    Filters books for given cretor
    return {'books': creator.get_manifestations()}    

@register.inclusion_tag('books_publisher_template.html')    
def books_for_publisher(publisher):
    Filters books for given publisher
    return {'books': publisher.get_manifestations()}    

@register.inclusion_tag('books_expression_template.html')    
def books_for_expression(expression):
    Filters books for given expression
    return {'books': expression.get_manifestations()}    
"""
    