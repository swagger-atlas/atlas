const hook = require('../atlas/modules/data_provider/artillery/hooks').hook;


describe('hooks class', () => {

    beforeEach(() => {
        hook.hooks = {};
        hook._hooksMap = {};
    });

    describe('register function', () => {

        test('first time op_id', () => {
            hook.register("op_id", "func");
            expect(hook.hooks).toEqual({"op_id": ["func"]})
        })

    });
});
