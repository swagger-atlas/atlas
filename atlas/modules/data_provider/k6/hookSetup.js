export class K6Hook {

    constructor() {
        this.hooks = {};
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
