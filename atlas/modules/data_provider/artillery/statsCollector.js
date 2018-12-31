_ = require('lodash');
createCsvWriter = require('csv-writer').createObjectCsvWriter;


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
        this.publisher = new CSVStatsPublisher();
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
        this.publisher.publishRow({id: rowStats.rowKey, ...Stats.processStats(rowStats)});
    }
};


class CSVStatsPublisher {
    constructor() {
        this.csvWriter = createCsvWriter({
            path: 'report.csv',
            header: [
                {id: "id", title: "KEY"},
                {id: "success", title: "Is Success?"},
                {id: "statusCode", title: "Status Code"}
            ]
        });
    }

    publishRow(row) {
        this.csvWriter.writeRecords([row]);
    }
}
