require "webrick"

env_file = File.join(__dir__, ".env.local")
if File.file?(env_file)
  File.readlines(env_file, chomp: true).each do |line|
    next if line.strip.empty? || line.lstrip.start_with?("#")
    key, value = line.split("=", 2)
    ENV[key] ||= value.to_s.strip if key && !key.empty?
  end
end

require_relative "api/index"

class LocalRequest
  attr_reader :path, :request_method, :body

  def initialize(request)
    @request = request
    @path = request.path
    @request_method = request.request_method
    @body = request.body
  end

  def header(name)
    @request.header[name.downcase]
  end
end

class LocalResponse
  attr_accessor :status, :body

  def initialize
    @headers = {}
    @status = 200
    @body = ""
  end

  def []=(name, value)
    @headers[name] = value
  end

  def apply_to(response)
    response.status = @status
    @headers.each { |name, value| response[name] = value }
    response.body = @body
  end
end

server = WEBrick::HTTPServer.new(Port: Integer(ENV.fetch("PORT", "3000")), AccessLog: [], Logger: WEBrick::Log.new($stderr, WEBrick::Log::WARN))
server.mount_proc("/") do |request, response|
  local_response = LocalResponse.new
  Handler.call(LocalRequest.new(request), local_response)
  local_response.apply_to(response)
end

trap("INT") { server.shutdown }
puts "Ruby portfolio running at http://localhost:#{server.config[:Port]}"
server.start
