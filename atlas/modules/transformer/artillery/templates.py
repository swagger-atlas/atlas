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


# Function is formatted, so use double braces
SCENARIO_PROFILE_FUNCTION = """function {name}SetProfiles(context, event, done) {{
    context.vars.profiles = _.pick(profiles, [{profiles}]);
    return done();
}}"""


SETUP_FUNCTION = """
function setUp(context, event, done) {

    registerHooks();

    let _profiles = hook.call("$profileSelection", context.vars.profiles)[0];
    let profileMap = selectProfile(_profiles);
    const profileName = Object.keys(profileMap)[0];
    let profile = profileMap[profileName];

    context.vars["provider"] = new Provider(profileName);
    context.vars["respDataParser"] = new ResponseDataParser(profileName);
    context.vars["stats"] = new StatsCollector();

    influx.writeMeasurement("virtualUsers", [{fields: {id: context._uid}}]);

    hook.call("$profileSetup", profile).then(
        (profile) => {
            context.vars["profile"] = profile;
            defaultHeaders = profile.auth.headers;
            return done();
        }
    )
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
function statsWrite(response, context, ee) {
    let stats = {url: context.vars._rawURL, method: response.request.method};
    if (context.vars._startTime) {
        let responseTime = Date.now() - context.vars._startTime;
        stats.startTime = context.vars._startTime;
        stats.responseTime = responseTime;
    }
    stats.isSuccess = (response.statusCode >= 200 && response.statusCode < 300) ? 1: 0;
    stats.statusCode = response.statusCode;
    stats.uid = context._uid;
    context.vars["stats"].write(stats);
}"""


FINAL_FLOW_FUNCTION = """
function statsEndResponse(context, event, done) {
    let statusCodeCounter = {};
    let influxReport = [];

    _.forEach(context.vars.stats.endpointReport, function (value, key) {
        const statusCode = value.statusCode;
        const val = statusCodeCounter[statusCode];
        statusCodeCounter[statusCode] = _.isUndefined(val) ? 1: val + 1;

        let fields = {...value, uid: context._uid};
        influxReport.push({tags: {requestName: key}, fields: fields, timestamp: value.time});
    });

    influx.writeMeasurement('requestsRaw', influxReport, {precision: 'ms'});

    if (statusCodeCounter["400"]) {
        console.log("HINT: Some APIs returned Bad Request (400). You may be able to fix them in hooks.js file");
    }

    if (statusCodeCounter["401"]) {
        console.log("HINT: Some APIs were not authenticated (401). You can authenticate your APIs through Profiles." +
            "See https://github.com/swagger-atlas/atlas/blob/master/docs/use_cases.md for Authentication guide");
    }

    done();
}"""


# Function would be formatted, so use double braces
API_AFTER_RESPONSE_FUNCTION = """function {after_func_name}(requestParams, response, context, ee, next) {{
    statsWrite(response, context, ee);
    const provider = context.vars['provider'];
    const status = response.statusCode;
    if (!status || status < 200 || status > 300) {{
        if (context.vars._delete_resource) {{
            const rollback = context.vars._delete_resource;
            provider.rollBackDelete(rollback.resource, rollback.value);
        }}
        ee.emit('error', 'Non 2xx Response');{else_body}
    }}
    provider.reset();
    return next();
}}"""


# Function would be formatted, so use double braces
IF_TRUE_FUNCTION = """function {if_true_name}(contextVars) {{
    const tags = [{tags}];
    return (contextVars['profile'] && !_.isEmpty(_.intersection(tags, contextVars['profile'].tags || [])));
}}"""
