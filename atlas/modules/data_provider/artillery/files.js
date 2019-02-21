fs = require('fs');
path = require('path');

settings = require('./settings');


class File {
    /*
        This is used to provide files to request bodies which needs them
    */

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

    getFileByPath(filePath) {
        // This is most generic method for this class.
        // It takes a file path, and return the readable stream for the file
        return fs.createReadStream(filePath);
    }
}

// By only exporting an object, and not class, we ensure this is a singleton
exports.file = new File();
