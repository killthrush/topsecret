import webpack from 'webpack'
import path from 'path'

export default {
  context: __dirname,
  entry: {
    app: [path.join(__dirname, './src/index.jsx')],
    vendor: [
      'axios',
      'es6-promise',
      'react',
      'react-dom'
    ]
  },
  output: {
    filename: "[name].bundle.[chunkhash].js",
    path: __dirname + "/dist"
  },
  module: {
    loaders: [{
      test: /\.js$/,
      exclude: /node_modules/,
      loader: 'babel-loader'
    },
    {
      test: /\.jsx$/,
      loader: 'babel-loader'
    }]   
  },
  plugins: [
    new webpack.optimize.CommonsChunkPlugin('manifest')
  ],
  resolve: {
    extensions: ['.js', '.jsx']
  }
}
