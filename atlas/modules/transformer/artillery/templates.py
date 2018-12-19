SELECT_PROFILE_FUNCTION = """
function selectProfile(profiles) {
    const profileName = _.sample(Object.keys(profiles));
    let profile = profiles[profileName];
    return {[profileName]: profile};
}"""


REGISTER_HOOKS_FUNCTION = """
function registerHooks() {
    _.forEach(hookRegister, function (_hook) {
        hook.register(..._hook);
    });
}"""


SETUP_FUNCTION = """
function setUp(context, event, done) {

    registerHooks();

    let _profiles = hook.call("$profileSelection", profiles);
    let profileMap = selectProfile(_profiles);
    const profileName = Object.keys(profileMap)[0];
    let profile = profileMap[profileName];
    profile = hook.call("$profileSetup", profile);

    context.vars["provider"] = new Provider(profileName);
    context.vars["respDataParser"] = new ResponseDataParser(profileName);
    context.vars["profile"] = profile;
    context.vars["stats"] = new StatsCollector();
    defaultHeaders = profile.auth.headers;

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
const Provider = utils.Provider, ResponseDataParser = utils.ResponseDataParser;
let respDataParser, defaultHeaders;
"""


STATS_WRITER = """
function statsWrite(response, context) {
    let stats = {url: response.request.path, method: response.request.method};
    stats.isSuccess = (response.statusCode >= 200 && response.statusCode < 300);
    stats.statusCode = response.statusCode;
    context.vars["stats"].write(stats);
}"""


AFTER_RESPONSE_FUNCTION = """
function statsEndResponse(context, event, done) {
    let statusCodeCounter = {};
    _.forEach(context.vars.stats.endpointReport, function (value) {
        const statusCode = value.statusCode;
        const val = statusCodeCounter[statusCode];
        statusCodeCounter[statusCode] = _.isUndefined(val) ? 1: val + 1;
    });

    if (statusCodeCounter["400"]) {
        console.log("HINT: Some APIs returned Bad Request (400). You may be able to fix them in hooks.js file");
    }

    if (statusCodeCounter["401"]) {
        console.log("HINT: Some APIs were not authenticated (401). You can authenticate your APIs through Profiles." +
            "See https://code.jtg.tools/jtg/atlas/docs/use_cases.md for Authentication guide");
    }

    done();
}"""
