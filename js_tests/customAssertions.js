function isSuperSet(set, subSet) {
    for (let elem of subSet) {
        if (!set.has(elem)) {
            return false;
        }
    }
    return true;
}

function isSubSet(set, superSet) {
    return isSuperSet(superSet, set);
}


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
    },
    isInstance(key, type) {
        const pass = key instanceof type;
        return {
            pass: pass,
            message: () => `${key} is not an instance of ${type}`
        }
    },
    isSuperSet(set, subSet) {
        const pass = isSuperSet(set, subSet);
        return {
            pass: pass,
            message: () => `${set} is not superSet of ${subSet}`
        }
    },
    isSubSet(set, superSet) {
        const pass = isSubSet(set, superSet);
        return {
            pass: pass,
            message: () => `${set} is not sub-set of ${superSet}`
        }
    },
});
