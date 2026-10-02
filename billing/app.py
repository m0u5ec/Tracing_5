
from flask import Flask
import requests
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(
   TracerProvider(
       resource=Resource.create({SERVICE_NAME: "billing"})
   )
)
jaeger_exporter = OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces")
trace.get_tracer_provider().add_span_processor(
   BatchSpanProcessor(jaeger_exporter)
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def pay():
    with trace.get_tracer(__name__).start_as_current_span("pay"):
        res = requests.get("http://order:8003")
        return "Payed"+" "+res.text