require 'yaml'
require 'sinatra'
require 'rack/csrf'

use Rack::Session::Cookie, secret: "sessionsecret"
use Rack::Csrf, raise: true

post '/submit' do
  data = params[:data]
  parsed = YAML.load(data)
  "Received object: #{parsed.inspect}"
end

get '/' do
  %Q{
    <form method="POST" action="/submit">
      <textarea name="data">{foo: bar}</textarea>
      <input type="submit" />
    </form>
  }
end
