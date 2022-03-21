from chalice import Chalice, Response
from chalice import BadRequestError

from chalicelib import generate_transactions, transactions_as_csv

app = Chalice(app_name="data-integration-transaction-generator")


@app.route("/")
def index():
    count = 5
    if app.current_request.query_params is not None:
        count = int(app.current_request.query_params.get("count", count))

    if count < 1 or count > 10000:
        raise BadRequestError("Invalid value for transaction count")
    return Response(body=transactions_as_csv(generate_transactions(count)),
                    status_code=200,
                    headers={"Content-Type": "text/plain"})
