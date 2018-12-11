_ = require('lodash');
createCsvWriter = require('csv-writer').createObjectCsvWriter;


class StatsRow {
    constructor(row) {
        this.url = row.url;
        this.method = row.method;
        this._isSuccess = row.isSuccess;
    }

    get isSuccess() {
        return this._isSuccess;
    }

    get rowKey() {
        return this.method + " : " + this.url;
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

    processRowStats(rowStats) {
        this.endpointReport[rowStats.rowKey] = {"success": rowStats.isSuccess};
        this.publisher.publishRow({id: rowStats.rowKey, isSuccess: rowStats.isSuccess});
    }
};


class CSVStatsPublisher {
    constructor() {
        this.csvWriter = createCsvWriter({
            path: 'report.csv',
            header: [
                {id: "id", title: "KEY"},
                {id: "isSuccess", title: "Is Success?"}
            ]
        });
    }

    publishRow(row) {
        this.csvWriter.writeRecords([row]);
    }
}
