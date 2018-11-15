SETUP_FUNCTION = """
function setUp(context, event, done) {
    const profile = Hook.selectProfile();
    const profileName = Object.keys(profile)[0];
    context.vars["provider"] = new Provider(profileName);
    context.vars["respDataParser"] = new ResponseDataParser(profileName);
    context.vars["profile"] = profile[profileName];
    defaultHeaders = profile[profileName].auth.headers;
    return done();
}"""


DYNAMIC_TEMPLATE_FUNCTION = """
function dynamicTemplate(string, vars) {
    _.forIn(vars, function (value, key) {
        string = string.replace(new RegExp('({' + key + '})', 'gi'), value);
    });
    return string;
}"""


FORMAT_URL_FUNCTION = """
function formatURL(url, queryConfig, pathConfig, provider) {
    const pathParams = provider.resolveObject(pathConfig);
    url = dynamicTemplate(url, pathParams);
    const queryParams = provider.resolveObject(queryConfig);
    const queryString = Object.keys(queryParams).map(key => key + '=' + queryParams[key]).join('&');
    url = queryString? url + '?' + queryString : url;
    return [url, _.assign(pathParams, queryParams)];
}"""

EXTRACT_BODY_FUNCTION = """
function extractBody(response, requestParams, context) {
    let body = response.body;
    if (!(body)) { body = {}; }
    return typeof body === 'object' ? body : JSON.parse(body);
}"""


GLOBAL_STATEMENTS = """
const hook = Hook.hook;
const Provider = utils.Provider, ResponseDataParser = utils.ResponseDataParser;
let provider, respDataParser, defaultHeaders;
"""
