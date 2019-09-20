_ = require('lodash');
stream = require('stream');
const hookRegister = require('./hooks.js').hookRegister;
hook = require('./libs/hooks').hook;
utils = require('./libs/providers');
settings = require('./libs/settings');
StatsCollector = require('./libs/statsCollector').StatsCollector;
profiles = require('./libs/profiles').profiles;
influx = require('./libs/influx').client;


const Provider = utils.Provider, ResponseDataParser = utils.ResponseDataParser;
let respDataParser, defaultHeaders;


module.exports = {
    setUp: setUp,
    defaultSetProfiles: defaultSetProfiles,
    apiCreatePreReq: apiCreatePreReq,
    apiCreatePostRes: apiCreatePostRes,
    apiCreateCondition: apiCreateCondition,
    apiReadPreReq: apiReadPreReq,
    apiReadPostRes: apiReadPostRes,
    apiReadCondition: apiReadCondition,
    endResponse: statsEndResponse
};

function selectProfile(profiles) {
    const profileName = _.sample(Object.keys(profiles));
    let profile = profiles[profileName];
    return {[profileName]: profile};
}

function registerHooks() {
    _.forEach(hookRegister, function (_hook) {
        hook.register(..._hook);
    });
}

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
}

function dynamicTemplate(string, vars) {
    _.forIn(vars, function (value, key) {
        string = string.replace(new RegExp('({' + key + '})', 'gi'), value);
    });
    return string;
}

function formatURL(url, queryConfig, pathConfig, provider) {
    const pathParams = provider.resolveObject(pathConfig);
    url = dynamicTemplate(url, pathParams);
    const queryParams = provider.resolveObject(queryConfig);
    const queryString = Object.keys(queryParams).map(key => key + '=' + queryParams[key]).join('&');
    url = queryString? url + '?' + queryString : url;
    return [url, _.assign(pathParams, queryParams)];
}

function extractBody(response, requestParams, context) {
    let body = response.body;
    if (!(body)) { body = {}; }
    return typeof body === 'object' ? body : JSON.parse(body);
}

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
}

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
}


function defaultSetProfiles(context, event, done) {
    context.vars.profiles = _.pick(profiles, ['profile_1']);
    return done();
}

function apiCreatePreReq(requestParams, context, ee, next) {
    const provider = context.vars['provider'];
    const bodyConfig = {"id": {"resource": "pet"}, "category": {"type": "object", "properties": {"id": {"resource": "category"}, "name": {"type": "string"}}}, "name": {"type": "string", "example": "doggie"}, "photoUrls": {"type": "array", "xml": {"wrapped": true}, "items": {"type": "string"}}, "status": {"type": "string", "enum": ["available", "pending", "sold"]}};
    let url = '/pet';
    context.vars._rawURL = url;
    let headers = _.cloneDeep(defaultHeaders);
    let reqParams = {'headers': headers};
    let body = {};
    try {
        body = provider.resolveObject(bodyConfig);
    } catch (ex) {
        console.error(ex.message + ' failed for "POST /pet"');
        ee.emit('error', 'Provider Check Failed');
        return next();
    }
    let reqArgs = hook.call('POST /pet', ...[url, body, reqParams]);
    reqArgs[2].headers['Content-Type'] = 'application/json';
    requestParams.json = reqArgs[1];
    requestParams.url = reqArgs[0];
    requestParams.headers = reqArgs[2].headers;
    context.vars._startTime = Date.now();
    return next();
}

function apiCreatePostRes(requestParams, response, context, ee, next) {
    statsWrite(response, context, ee);
    const provider = context.vars['provider'];
    const status = response.statusCode;
    if (!status || status < 200 || status > 300) {
        if (context.vars._delete_resource) {
            const rollback = context.vars._delete_resource;
            provider.rollBackDelete(rollback.resource, rollback.value);
        }
        ee.emit('error', 'Non 2xx Response');
    } else {
        context.vars['respDataParser'].resolve({"id": {"resource": "pet"}, "category": {"type": "object", "properties": {"id": {"resource": "category"}, "name": {"type": "string"}}}, "name": {"type": "string", "example": "doggie"}, "photoUrls": {"type": "array", "xml": {"wrapped": true}, "items": {"type": "string"}}, "status": {"type": "string", "enum": ["available", "pending", "sold"]}}, extractBody(response, requestParams, context), provider.configResourceMap);
    }
    provider.reset();
    return next();
}

function apiCreateCondition(contextVars) {
    const tags = ['pet'];
    return (contextVars['profile'] && !_.isEmpty(_.intersection(tags, contextVars['profile'].tags || [])));
}

function apiReadPreReq(requestParams, context, ee, next) {
    const provider = context.vars['provider'];
    let url = '/pet/{petId}';
    context.vars._rawURL = url;
    let urlConfig = [];
    const queryConfig = {};
    const pathConfig = {'petId': {'resource': 'pet'}};
    try {
        urlConfig = formatURL(url, queryConfig, pathConfig, provider);
        url = urlConfig[0];
    } catch (ex) {
        console.error(ex.message + ' failed for "GET /pet/{petId}"');
        ee.emit('error', 'Provider Check Failed');
        return next();
    }
    let headers = _.cloneDeep(defaultHeaders);
    let reqParams = {'headers': headers};
    let reqArgs = hook.call('GET /pet/{petId}', ...[url, reqParams]);
    requestParams.url = reqArgs[0];
    requestParams.headers = reqArgs[1].headers;
    context.vars._startTime = Date.now();
    return next();
}

function apiReadPostRes(requestParams, response, context, ee, next) {
    statsWrite(response, context, ee);
    const provider = context.vars['provider'];
    const status = response.statusCode;
    if (!status || status < 200 || status > 300) {
        if (context.vars._delete_resource) {
            const rollback = context.vars._delete_resource;
            provider.rollBackDelete(rollback.resource, rollback.value);
        }
        ee.emit('error', 'Non 2xx Response');
    } else {
        context.vars['respDataParser'].resolve({"id": {"resource": "pet"}, "category": {"type": "object", "properties": {"id": {"resource": "category"}, "name": {"type": "string"}}}, "name": {"type": "string", "example": "doggie"}, "photoUrls": {"type": "array", "xml": {"wrapped": true}, "items": {"type": "string"}}, "status": {"type": "string", "enum": ["available", "pending", "sold"]}}, extractBody(response, requestParams, context), provider.configResourceMap);
    }
    provider.reset();
    return next();
}

function apiReadCondition(contextVars) {
    const tags = ['pet'];
    return (contextVars['profile'] && !_.isEmpty(_.intersection(tags, contextVars['profile'].tags || [])));
}
