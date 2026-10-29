"""Distributed Tracing - AFTER (OpenTelemetry)

- Trace : perjalanan satu request dari awal sampai akhir, punya trace_id
- Span  : satu langkah di dalam trace (cek stok, simpan, publish), punya waktu mulai dan durasi
Setiap langkah dibungkus tracer.start_as_current_span(...). Span di dalam span lain menjadi anaknya.

Supaya trace tersambung ke proses consumer, konteks trace ikut dikirim di header pesan:
    inject(headers)   di producer : tulis traceparent ke header
    extract(headers)  di consumer : baca traceparent, span consumer jadi bagian trace yang sama
Di production, span dikirim ke Jaeger atau Grafana Tempo. Di sini span dicetak sebagai pohon.

Jalankan: python after.py
"""
import json
import time

from opentelemetry import trace
from opentelemetry.propagate import extract, inject
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter)

exporter = InMemorySpanExporter()    # anggap: Jaeger
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("order-api")

QUEUE = []                           # anggap: queue RabbitMQ


def check_stock():
    with tracer.start_as_current_span("check_stock"):
        time.sleep(0.02)


def save_order():
    with tracer.start_as_current_span("db.save_order"):
        time.sleep(0.05)


def publish_event(event: dict):
    with tracer.start_as_current_span("rabbitmq.publish"):
        headers = {}
        inject(headers)              # traceparent ikut di header
        time.sleep(0.4)              # broker sedang lambat
        QUEUE.append({"headers": headers, "body": json.dumps(event)})


def place_order():
    with tracer.start_as_current_span("POST /orders"):
        check_stock()
        save_order()
        publish_event({"type": "order.placed", "order_id": 7})


def consume():                       # anggap: proses consumer
    message = QUEUE.pop(0)
    context = extract(message["headers"])   # sambung ke trace API
    with tracer.start_as_current_span("consumer.send_email",
                                      context=context):
        time.sleep(0.1)


def print_trace():
    children = {}                    # span_id parent -> span anak
    for span in exporter.get_finished_spans():
        parent = span.parent.span_id if span.parent else None
        children.setdefault(parent, []).append(span)

    def show(span, depth):
        ms = (span.end_time - span.start_time) / 1e6
        name = "  " * depth + span.name
        trace_id = f"{span.context.trace_id:032x}"
        print(f"  {name:<26} {ms:4.0f} ms  trace_id {trace_id[:10]}")
        for child in children.get(span.context.span_id, []):
            show(child, depth + 1)

    show(children[None][0], 0)       # mulai dari span tanpa parent


if __name__ == "__main__":
    place_order()
    consume()
    print_trace()
