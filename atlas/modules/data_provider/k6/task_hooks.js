export function foo(...reqArgs) {
    reqArgs[1] = {"jack": "something"};
    return reqArgs;
}


export const QUEUE = {
    calendarAuthRevokeCreate: foo
};
