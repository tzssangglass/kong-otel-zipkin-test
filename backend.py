from flask import Flask, request
from opentelemetry import trace, propagate
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up the resource with the service name
resource = Resource(attributes={
    "service.name": "my-upstream-app",
    "service.version": "1.0.0"
})

# Set up the tracer provider with the resource
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Set up the OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:55681/v1/traces",
)

# Set up the batch span processor
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument the Flask app with OpenTelemetry
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def index():
    # Log the request headers
    logger.info("Request Headers: %s", request.headers)
    
    with tracer.start_as_current_span("index-span"):
        return "Hello, World!"

@app.route("/external-trace")
def external_trace():
    # Log the request headers
    logger.info("Request Headers: %s", request.headers)

    # Extract the context from the incoming request headers, including "Traceparent"
    context = propagate.extract(request.headers)

    # Start a new span that is linked to the external trace's context
    with tracer.start_as_current_span("external-trace-span", context=context):
        # Simulate some processing
        return "External Trace Processed"

if __name__ == "__main__":
    app.run(debug=True)
