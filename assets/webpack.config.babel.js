import webpack from 'webpack'

export default {
  context: process.cwd(),
  entry: {
    app: './src/index',
    vendor: './src/vendor'
  },
  output: {
    filename: "[name].bundle.[chunkhash].js",
    path: __dirname + "/dist"
  },
  module: {
    loaders: [{
      test: /\.js$/,
      exclude: /node_modules/,
      loader: 'babel'
    },
    {
      test: /\.jsx$/,
      loader: 'babel'
    }]   
  },
  plugins: [
    new webpack.optimize.CommonsChunkPlugin("vendor", "[name].bundle.[chunkhash].js")
  ],
  resolve: {
    extensions: ['', '.js', '.jsx']
  }
}
