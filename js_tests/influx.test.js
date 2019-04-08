const Influx = require('influx');
const influx = require('../atlas/modules/data_provider/artillery/influx');
const settings = require('./settings');

jest.mock('influx');


test('influx db is initialized properly', () => {

    expect(Influx.InfluxDB).toBeCalledWith({
        database: settings.INFLUX.database,
        host: settings.INFLUX.host || "localhost",
        port: settings.INFLUX.port || 8086,
        username: settings.INFLUX.username,
        password: settings.INFLUX.password
    });

});
