export class K6Hook {

    constructor() {
        this.profile = "<your code>";
        this.auth = "<your code>";
        this.tags = "[<your tags>]";
        this.hooks = {};
    }

    defaultHeaders() {
        // Overwrite this if you need to change default Headers
        return {'Authorization': 'Token ' + this.auth}
    }

    register(operationID, funcName) {
        if (!this.hooks[operationID]) {
            this.hooks[operationID] = [];
        }
        this.hooks[operationID].push(funcName);
    }

    call(operationID, ...args) {
        if (this.hooks[operationID]) {
            for (let hook of this.hooks[operationID]) {
                args = hook(...args);
            }
        }
        return args;
    }
}

export const hook = new K6Hook();
export const defaultHeaders = hook.defaultHeaders();

/*
Define your functions and register them in hooks here.
For example:
function testHook(...args) {
    console.log("I am a test hook");
    return args;
}

hook.register("operationId", testHook);

Each hook thus defined must take ...args and must return args.
Number and order of arguments in return must not change
 */
