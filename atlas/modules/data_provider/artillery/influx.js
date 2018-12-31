const Influx = require('influx');
settings = require('./settings');


exports.client = new Influx.InfluxDB({
  database: settings.INFLUX.database,
  host: settings.INFLUX.host || "localhost",
  port: settings.INFLUX.port || 8086,
  username: settings.INFLUX.username,
  password: settings.INFLUX.password
});
