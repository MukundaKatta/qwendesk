"""Create the Tablestore table. Requires OTS_* + ALIBABA_CLOUD_* env vars."""
import os

from tablestore import CapacityUnit, OTSClient, ReservedThroughput, TableMeta, TableOptions
from tablestore.error import OTSServiceError


def main() -> None:
    client = OTSClient(
        os.environ["OTS_ENDPOINT"],
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"],
        os.environ["OTS_INSTANCE"],
    )
    table = os.environ.get("OTS_TABLE", "qwendesk_tickets")
    schema = [("pk", "STRING"), ("id", "STRING")]
    table_meta = TableMeta(table, schema)
    reserved = ReservedThroughput(CapacityUnit(0, 0))
    try:
        client.create_table(table_meta, TableOptions(), reserved)
        print(f"Created Tablestore table '{table}'.")
    except OTSServiceError as e:
        if e.get_error_code() == "OTSObjectAlreadyExist":
            print(f"Table '{table}' already exists. Nothing to do.")
        else:
            raise


if __name__ == "__main__":
    main()
