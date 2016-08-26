# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from IPython.core.display import display, HTML, Javascript
from IPython.utils.py3compat import str_to_bytes, bytes_to_str
import pandas
import pyspark
import base64

unique_explore_id = 0

def stringify_property(property_key, property_value):
    if type(property_value) == bool:
        if property_value:
            return property_key
    else:
        return '{}="{}"'.format(property_key, str(property_value))

def stringify_properties(properties):
    return ' '.join(filter(None, map(lambda x: stringify_property(x, properties[x]), properties)))

def stringify_bindings(bindings):
    return ' '.join(map(lambda x: '{}="{{{{{}}}}}"'.format(x, bindings[x]), bindings))

def create_code_cell(code='', where='below'):
    encoded_code = bytes_to_str(base64.b64encode(str_to_bytes(code)))
    display(Javascript("""
        var code = IPython.notebook.insert_cell_{0}('code');
        code.set_text(atob("{1}"));
    """.format(where, encoded_code)))

def explore(df, channel='default', properties={}, bindings={}, display_code=False):
    """
    Renders the urth-viz-explorer widget to the user output
    If pandas.DataFrame assign with unique name to user namespace else use what was passed in the string

    Parameters
    ----------
    df                  The dataframe itself or the string representation of the variable
    channel             The channel to bind to defaulted to default
    properties          The properties e.g. {'selection-as-object': False, 'foo': 5}
    bindings            The bindings e.g. {'selection': 'sel'}
    """

    global unique_explore_id
    unique_explore_id += 1
    explore_df = "unique_explore_df_name_" + str(unique_explore_id)
    if isinstance(df, pandas.DataFrame) or isinstance(df, pyspark.sql.DataFrame):
        get_ipython().user_ns[explore_df] = df
    else:
        explore_df = df

    generated_html = """<link rel='import' href='urth_components/declarativewidgets-explorer/urth-viz-explorer.html'
                           is='urth-core-import' package='jupyter-incubator/declarativewidgets_explorer'>
                       <template is="urth-core-bind" channel="{channel}">
                           <urth-viz-explorer ref='{ref}' {props} {binds}></urth-viz-explorer>
                       </template>""".format(ref=explore_df, channel=channel,
                        props=stringify_properties(properties), binds=stringify_bindings(bindings))

    display(HTML(generated_html))
    if display_code:
        create_code_cell("%%html\n" + generated_html)
