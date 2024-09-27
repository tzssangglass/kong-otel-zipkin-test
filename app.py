import requests
from opentelemetry import trace, propagate
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Initialize tracer provider
resource = Resource(attributes={
    SERVICE_NAME: "my-frontend-service"  # Name of this service
})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Set up OTLP exporter (same as the first app)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:55681/v1/traces",
)


# Add span processor
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument the requests library to automatically add trace headers
RequestsInstrumentor().instrument()

def send_request():
    # Start a new trace and span
    with tracer.start_as_current_span("client-span") as span:
        # The trace context will be automatically injected into the headers by the Requests instrumentation
        response = requests.get("http://localhost:8000/flask")
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")

if __name__ == "__main__":
    send_request()
