import os
import boto3
from botocore.exceptions import ClientError

BUCKET = "gbrj-simulator-oltp-datalake"

def main():
    # 1) Cria o client S3 usando as credenciais do ambiente
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )

    prefix = "bronze/"

    try:
        # 2) Lista objetos no prefixo (pode estar vazio — tudo bem)
        print(f"🔎 Listando objetos em s3://{BUCKET}/{prefix}")
        resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix, MaxKeys=5)
        for obj in resp.get("Contents", []):
            print(" -", obj["Key"])

        # 3) Escreve um arquivo de teste
        test_key = f"{prefix}_test_access/hello.txt"
        print(f"✍️ Gravando objeto de teste: {test_key}")
        s3.put_object(
            Bucket=BUCKET,
            Key=test_key,
            Body=b"hello from simulator-oltp-datalake"
        )

        # 4) Lê o arquivo de volta
        print("📖 Lendo objeto de teste")
        out = s3.get_object(Bucket=BUCKET, Key=test_key)
        content = out["Body"].read().decode("utf-8")
        print("Conteúdo:", content)

        print("✅ TESTE S3 OK")

    except ClientError as e:
        print("❌ ERRO NO TESTE S3")
        print(e)

if __name__ == "__main__":
    main()
