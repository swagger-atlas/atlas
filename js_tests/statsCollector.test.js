const Stats = require('../atlas/modules/data_provider/artillery/statsCollector').StatsCollector;

const statsCollector = new Stats();


test('check stats Collector report after write op', () => {

    const startTime = Date.now();

    statsCollector.write({
        url: "url", method: "GET", isSuccess: 0, statusCode: 200, uid: 12345,
        startTime: startTime, responseTime: 1000
    });

    expect(statsCollector.endpointReport).toEqual({
        "GET : url": {
            success: 0, statusCode: 200, responseTime: 1000, time: startTime
        }
    });
});
