class Hook {

    constructor() {
        this.hooks = {};
        this._hooksMap = {};    // Kept to insure that hooks are not registered multiple times
    }

    register(operationID, funcName) {
        if (!this.hooks[operationID]) {
            this.hooks[operationID] = [];
            this._hooksMap[operationID] = new Set();
        }
        if (!this._hooksMap[operationID].has(funcName)) {
            this.hooks[operationID].push(funcName);
            this._hooksMap[operationID].add(funcName)
        }
    }

    call(operationID, ...args) {
        if (this.hooks[operationID]) {
            for (let hook of this.hooks[operationID]) {
                // console.log("Hook: ", hook, typeof hook, operationID, this.hooks);
                args = hook(...args);
            }
        }
        return args;
    }
}

exports.hook = new Hook();
