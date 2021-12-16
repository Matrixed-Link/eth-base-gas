import argparse
import flask
from datetime import datetime
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from waitress import serve
app = flask.Flask(__name__)
app.config["DEBUG"] = True

CLI=argparse.ArgumentParser()
CLI.add_argument(
  "--rpc",  # name on the CLI - drop the `--` for positional/required parameters
  nargs="*",  # 0 or more values expected => creates a list
  type=str,
  default=[],  # default if nothing is provided
)

args = CLI.parse_args()
RPCURLS = args.rpc
RPC=dict(enumerate(RPCURLS, start=1))


def runApp():
    while True:
        try:
            serve(app, host="0.0.0.0", port=5000)
        except:
            print("Flask app errored.")

def getGas():
    selected = selectRPC()
    # Get Gas Data.
    web3 = Web3(HTTPProvider(selected))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    block_number = web3.eth.blockNumber
    gas = web3.eth.get_block(block_number).baseFeePerGas
    return block_number,gas

def makeRequest():
    try:
        block_number,gas = getGas()
        output = {"block": "" + str(block_number) + "", "baseFeePerGas": "" + str(gas) + ""}
        print(datetime.now().strftime("%H:%M:%S"), '|', flask.request.remote_addr, '| ', output)
    except:
        print(datetime.now().strftime("%H:%M:%S"), '|', flask.request.remote_addr, '| Failed to retrieve data. Retrying')
        output = 'NULL'
    return output

def selectRPC():
    # Get block data.
    x = 0
    block = 0
    selected = 0
    while x <= len(RPC):
        try:
            RPC_URL = RPC[x]
            web3 = Web3(HTTPProvider(RPC_URL))
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            block_number = web3.eth.blockNumber
            if block_number > block:
                selected = RPC[x]
                block = block_number
        except:
            pass
        x += 1
    return selected

@app.route('/', methods=['GET'])
def gasBase_ETH():
    output = 'NULL'
    trycount = 1
    while output == 'NULL' and trycount <= 5:
        if trycount >= 2:
            print('Retrying ('+str(trycount)+'/5)')
        trycount += 1
        try:
            output = makeRequest()
        except:
            pass
    return output

if __name__ == "__main__":
        try:
            print(datetime.now().strftime("%H:%M:%S"),'| Starting flask server.')
            runApp()
        except Exception as e:
            print("Running app errored.")
            print(e)
