class Hook {
    /*
        This class implements the hook registration and execution mechanism
        As hooks are registered, they are saved in this class, and when called, they are executed one by one.

        Data structures:
            hooks:
                An object containing "ID" of hook, with the payload being an array of associated hook

                Example:
                    hooks = {
                        "test": [
                            "func1", "func2"
                        ],
                        "another": [
                            "abc", "xyz"
                        ]
                    }

            _hooksMap:
                An object containing "ID" of hook, and the set of all associated hooks. This makes sure that no
                hook is registered twice to same ID.
     */

    constructor() {
        this.hooks = {};
        this._hooksMap = {};    // Kept to insure that hooks are not registered multiple times
    }

    /*
        Hook Registration Method.

        Example usage:
            function func1(...args) {}
            hook.register("id", func1);
     */
    register(operationID, funcName) {

        // Create new entry in Data structures if this is first time this OP ID is encountered
        if (!this.hooks[operationID]) {
            this.hooks[operationID] = [];
            this._hooksMap[operationID] = new Set();
        }

        // Only associate this hook with this ID if we have not done it before
        if (!this._hooksMap[operationID].has(funcName)) {
            this.hooks[operationID].push(funcName);
            this._hooksMap[operationID].add(funcName)
        }
    }

    /*
        Hook Call Method. Call all the registered methods associated with hooks, and return the accumulation

        Example:
            hook.call("id", args) -> would call all hooks associated with ID one after another
     */
    call(operationID, ...args) {
        if (this.hooks[operationID]) {
            for (let hook of this.hooks[operationID]) {
                args = hook(...args);
            }
        }
        return args;
    }
}

exports.hook = new Hook();
