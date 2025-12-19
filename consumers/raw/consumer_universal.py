import json
import os
from datetime import datetime
import boto3
from confluent_kafka import Consumer

# =========================
# CONFIGURAÇÕES
# =========================
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "alimentador_kafka:29092")
PREFIXO_TOPICO = "oltp.public."
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "200"))

S3_BUCKET = os.getenv("S3_BUCKET")
if not S3_BUCKET:
    raise RuntimeError(
        "S3_BUCKET não definido. "
        "Configure a variável de ambiente antes de iniciar o consumer."
    )

S3_BASE_PREFIX = os.getenv("S3_BASE_PREFIX")
if not S3_BASE_PREFIX:
    raise RuntimeError(
        "S3_BASE_PREFIX não definido. "
        "Configure a região antes de iniciar o consumer."
    )

AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
if not AWS_REGION:
    raise RuntimeError(
        "AWS_DEFAULT_REGION não definido. "
        "Configure a região antes de iniciar o consumer."
    )

# =========================
# CLIENTE S3
# =========================
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
)

# =========================
# FUNÇÃO DE GRAVAÇÃO RAW
# =========================
def salvar_lote_raw_s3(tabela, eventos):
    if not eventos:
        return

    agora = datetime.utcnow()
    ano = agora.strftime("%Y")
    mes = agora.strftime("%m")
    dia = agora.strftime("%d")

    s3_key = (
        f"{S3_BASE_PREFIX}/{tabela}/"
        f"ano={ano}/mes={mes}/dia={dia}/"
        f"batch-{agora.strftime('%H%M%S%f')}.json"
    )

    body = json.dumps(eventos, ensure_ascii=False)

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
    )

    print(
        f"[RAW][S3] {tabela}: {len(eventos)} eventos → "
        f"s3://{S3_BUCKET}/{s3_key}"
    )

# =========================
# MAIN
# =========================
def main():
    print("🚀 Iniciando Consumer RAW UNIVERSAL → S3")

    consumer = Consumer({
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "raw-universal",
        "auto.offset.reset": "earliest",
    })

    # Descobrir tópicos Debezium automaticamente
    metadata = consumer.list_topics(timeout=10)
    todos_topicos = metadata.topics.keys()

    topicos_debezium = [
        t for t in todos_topicos if t.startswith(PREFIXO_TOPICO)
    ]

    if not topicos_debezium:
        print("❌ Nenhum tópico Debezium encontrado.")
        return

    print("🔎 Tópicos detectados:")
    for t in topicos_debezium:
        print(" -", t)

    consumer.subscribe(topicos_debezium)

    # Buffers por tabela
    buffers = {}

    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print("[ERRO] Kafka:", msg.error())
            continue

        payload = json.loads(msg.value().decode("utf-8"))

        topico = msg.topic()
        tabela = topico.split(".")[2]  # oltp.public.<tabela>

        if tabela not in buffers:
            buffers[tabela] = []

        evento = {
            "topic": topico,
            "partition": msg.partition(),
            "offset": msg.offset(),
            "ingestion_ts": datetime.utcnow().isoformat(),
            "payload": payload,  # CDC cru
        }

        buffers[tabela].append(evento)

        # Flush por tabela
        if len(buffers[tabela]) >= BATCH_SIZE:
            salvar_lote_raw_s3(tabela, buffers[tabela])
            buffers[tabela] = []

# =========================
if __name__ == "__main__":
    main()
