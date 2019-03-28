const hook = require('../atlas/modules/data_provider/artillery/hooks').hook;


describe('hooks class', () => {

    beforeEach(() => {
        hook.hooks = {};
        hook._hooksMap = {};
    });

    describe('register function', () => {

        test('first time op_id', () => {
            hook.register("op_id", "func");
            expect(hook.hooks).toEqual({"op_id": ["func"]});
        });

        test('op_id exists with new function', () => {
            hook.register("op_id", "func");
            hook.register("op_id", "new_func");
            expect(hook.hooks).toEqual({"op_id": ["func", "new_func"]});
        });

        test('op_id exists with same function', () => {
            hook.register("op_id", "func");
            hook.register("op_id", "func");
            expect(hook.hooks).toEqual({"op_id": ["func"]});
        });

    });

    describe("call function", () => {

        function addOne(...args) {
            return args.map(num => num + 1);
        }

        function double(...args) {
            return args.map(num => num * 2);
        }


        test("no hooks exist for operation id", () => {
            expect(hook.call("op_id", 1, 2)).toEqual([1, 2]);
        });

        test("single hook is associated with op_id", () => {
            hook.register("op_id", addOne);
            expect(hook.call("op_id", 1, 2)).toEqual([2, 3]);
        });

        test("multiple hooks are associated, run after each other in chained fashion", () => {
            hook.register("op_id", addOne);
            hook.register("op_id", double);
            expect(hook.call("op_id", 1, 2)).toEqual([4, 6]);
        });
    })
});
