_ = require('lodash');


class StatsRow {
    constructor(row) {
        this.url = row.url;
        this.method = row.method;
        this._isSuccess = row.isSuccess;
        this.statusCode = row.statusCode;

        this.startTime = row.startTime;
        this.responseTime = row.responseTime;
    }

    get isSuccess() {
        return this._isSuccess;
    }

    get rowKey() {
        return this.method + " : " + this.url;
    }

    get time() {
        return this.startTime;
    }
}


exports.StatsCollector = class Stats {
    constructor() {
        this.endpointReport = {};
        this.reset();
    }

    reset() {
    }

    write(row) {
        let rowStats = new StatsRow(row);
        this.processRowStats(rowStats);
    }

    static processStats(row) {
        return {
            "success": row.isSuccess, "statusCode": row.statusCode, "responseTime": row.responseTime,
            "time": row.time
        };
    }

    processRowStats(rowStats) {
        this.endpointReport[rowStats.rowKey] = Stats.processStats(rowStats);
    }
};
