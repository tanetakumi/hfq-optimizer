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
      directory: path.resolve(__dirname, 'public'),
    }
  },  
  // メインとなるJavaScriptファイル（エントリーポイント）
  entry: './src/app/app.tsx',
  plugins: [
    new CleanWebpackPlugin({
      cleanAfterEveryBuildPatterns: ['public/build']
    }),
    new HtmlWebpackPlugin({
      template: 'src/templates/index.html'
    }),
  ],
  // ファイルの出力設定
  output: {
    path: __dirname + '/public',
    filename: 'build/[name].[contenthash].js'
  },
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
