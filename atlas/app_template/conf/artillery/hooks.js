// Refer to https://code.jtg.tools/jtg/atlas/tree/master/docs/hooks.md for details on how to write and use the hooks

async function addHeaders(profile) {
    profile.auth = {
        "headers": {'Authorization': 'Token ' + profile.token}
    };
    return profile;
}

exports.hookRegister = [
    // $profileSetup requires at least once hook.
    ["$profileSetup", addHeaders]
];
