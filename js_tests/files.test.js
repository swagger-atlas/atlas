const fs = require('fs');
path = require('path');

settings = require('./settings');
const file = require('../atlas/modules/data_provider/artillery/files').file;


describe('file test cases', () => {

    afterEach(() => {
        fs.createReadStream.mockReset();
    });

    test('getFile test cases', () => {
        fs.createReadStream = jest.fn(() => 'abc');

        expect(file.getFile('ext')).toEqual('abc');

        expect(fs.createReadStream).toBeCalledWith(
            path.join(settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER, 'dummy.ext')
        );
    });

    test('getImageFile test cases', () => {
        fs.createReadStream = jest.fn(() => 'abc');

        expect(file.getImageFile()).toEqual('abc');

        expect(fs.createReadStream).toBeCalledWith(
            path.join(settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER, 'dummy.jpg')
        );
    });

    test('getCSVFile test cases', () => {
        fs.createReadStream = jest.fn(() => 'abc');

        expect(file.getCSVFile()).toEqual('abc');

        expect(fs.createReadStream).toBeCalledWith(
            path.join(settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER, 'dummy.csv')
        );
    });

    test('getExcelFile test cases', () => {
        fs.createReadStream = jest.fn(() => 'abc');

        expect(file.getExcelFile()).toEqual('abc');

        expect(fs.createReadStream).toBeCalledWith(
            path.join(settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER, 'dummy.xls')
        );
    });

    test('getTextFile test cases', () => {
        fs.createReadStream = jest.fn(() => 'abc');

        expect(file.getTextFile()).toEqual('abc');

        expect(fs.createReadStream).toBeCalledWith(
            path.join(settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER, 'dummy.txt')
        );
    });

    test('getFileByPath test cases', () => {
        fs.createReadStream = jest.fn(() => 'abc');

        expect(file.getFileByPath('some_path')).toEqual('abc');

        expect(fs.createReadStream).toBeCalledWith('some_path');
    });

});
