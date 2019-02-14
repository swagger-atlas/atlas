fs = require('fs');
path = require('path');

settings = require('./settings');


class File {

    constructor() {
        this.basePath = path.join(settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER);
    }

    getFile(fileType) {
        return fs.createReadStream(path.join(this.basePath, `dummy.${fileType}`));
    }

    getImageFile() {
        return this.getFile('jpg');
    }

    getCSVFile() {
        return this.getFile('csv');
    }

    getExcelFile() {
        return this.getFile('xls');
    }

    getTextFile() {
        return this.getFile('txt');
    }

    static getFileByPath(filePath) {
        return fs.createReadStream(filePath);
    }
}

exports.file = new File();
