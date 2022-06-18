const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');

const isProd = process.env.NODE_ENV === 'production'

module.exports = {
  mode: 'development', 
  devServer: {
    port : 3003,
    hot: true,
    static: {
      directory: path.join(__dirname, 'public'),
    }
  },  
  // メインとなるJavaScriptファイル（エントリーポイント）
  entry: path.join(__dirname, 'src', 'index.tsx'),
  // ファイルの出力設定
  output: {
    path: path.join(__dirname, 'public'),
    filename: 'build.js'
  },
  plugins: [
  ],
  resolve: {
    extensions: ['.ts', '.tsx', '.js']
  },
  module: {
    rules: [
      { 
        test: /\.tsx?$/,
        loader: 'ts-loader'
      }
    ]
  }
};
