expect.extend({
    inBetween(num, low, high) {
        const pass = num >= low && num <= high;
        return {
            pass: pass,
            message: () => `${num} is not between ${low} and ${high}`
        };
    },
    in(key, iterable) {
        const set_iter = new Set(iterable);
        const pass = set_iter.has(key);
        return {
            pass: pass,
            message: () => `${key} is not in ${iterable}`
        }
    }
});
