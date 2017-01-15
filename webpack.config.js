const webpack = require('webpack');
const path = require('path');
const buildPath = path.resolve(__dirname, 'static/build');
const nodeModulesPath = path.resolve(__dirname, 'node_modules');

const config = {
  // Entry points to the project
  entry: {
    app: path.join(__dirname, '/static/app/app.js'),
    admin: path.join(__dirname, '/static/admin/admin.js')
  },
  output: {
    path: buildPath, // Path of output file
    filename: '[name].bundle.js',
    publicPath: '/dev-bundle/',
  },
  module: {
    loaders: [
      {
        // React-hot loader and
        test: /\.js$/, // All .js files
        loaders: ['babel-loader'], // react-hot is like browser sync and babel loads jsx and es6-7
        exclude: [nodeModulesPath],
      },
      {
        test: /\.css$/,
        loaders: ['style', 'css'],
        exclude: [nodeModulesPath],
      }
    ],
  },
};

module.exports = config;
