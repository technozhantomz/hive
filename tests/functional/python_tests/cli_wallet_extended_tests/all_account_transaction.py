import json

from concurrent.futures import ThreadPoolExecutor
from test_tools.communication import request
from typing import Dict, List

json_server_request_test = '/home/dev/Desktop/server_request_data/server_request_test/server_request_test.json'

develop_url = 'http://localhost:28091'
server_develop_url = 'http://hive-2:8091'
json_server_develop_data_stored = '/home/dev/Desktop/server_request_data/server_request_develop_data/blocktrades_server_request_develop_data.json'


server_master_url = 'http://hive-2:18091'
json_server_master_data_stored = '/home/dev/Desktop/server_request_data/server_request_master_data/blocktrades_server_request_master_data.json'


def get_last_transaction_number(account_name: str, url: str) -> int:
    last_transaction = request(url,
                {"id": 9, "jsonrpc": "2.0", "method": "account_history_api.get_account_history",
                 "params": {"account": account_name, "start": -1, "limit": 1}})
    return last_transaction['result']['history'][0][0]


def json_to_variable_opener(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def get_all_account_transactions(account_name: str, start_transaction_number, last_transaction_number, url) -> List[Dict]:
    all_account_transaction = []
    for e, i in enumerate(range(last_transaction_number, start_transaction_number-1, -1000)):
        if start_transaction_number == 0 and i == 1:
            request_data = request(url,
                                   {"id": 9, "jsonrpc": "2.0", "method": "account_history_api.get_account_history",
                                    "params": {"account": account_name, "start": 0, "limit": 1}})
            all_account_transaction.append(request_data)
        elif last_transaction_number - start_transaction_number < 1000:
            request_data = request(url,
                                   {"id": 9, "jsonrpc": "2.0", "method": "account_history_api.get_account_history",
                                    "params": {"account": account_name, "start": i, "limit": last_transaction_number - start_transaction_number + 1}})
            all_account_transaction.append(request_data)
        else:
            request_data = request(url,
                                   {"id": 9, "jsonrpc": "2.0", "method": "account_history_api.get_account_history",
                                    "params": {"account": account_name, "start": i, "limit": 1000}})
            all_account_transaction.append(request_data)
            last_transaction_number -= 1000

        if e % 100 == 0:
            print('Downloaded 1000 packs of transactions', flush=True)
    return all_account_transaction


def save_transaction_to_json(data_stored, account_name, start_transaction_number, last_transaction_number, url):
    single_saver_data = get_all_account_transactions(account_name, start_transaction_number, last_transaction_number, url)
    to_single_save = [list(reversed(item['result']['history'])) for item in single_saver_data]
    print()
    with open(data_stored, 'w') as file:
        json.dump(to_single_save, file)
    # multi_saver_datas = multi_saver(account_name, start_transaction_number, last_transaction_number, url)
    # to_save_multi = [list(reversed(item['result']['history'])) for item in multi_saver_datas]
    # print()
    # with open(data_stored, 'w') as file:
    #     json.dump(to_save_multi, file)


def multi_saver(account_name: str, start_transaction_number, last_transaction_number, url):
    tasks_list = []
    datas = []
    executor = ThreadPoolExecutor(max_workers=4)
    for i in range(last_transaction_number, start_transaction_number, -1000):
        if i - start_transaction_number < 1000:
            tasks_list.append(executor.submit(get_all_account_transactions, account_name, start_transaction_number, i, url))
        else:
            tasks_list.append(executor.submit(get_all_account_transactions, account_name, i - 1000, i, url))
    for thread_number in tasks_list:
        datas.extend(thread_number.result())
    return datas


def assign_transactions_keys(data):
    sorted_data = {}
    ignore_keys = ('virtual_op', 'op_in_trx')
    for all_transactions in data:
        for one_in_thousand_transaction in all_transactions:
            sorted_data_key = (one_in_thousand_transaction[1]['block'], one_in_thousand_transaction[1]['timestamp'])
            if sorted_data_key not in sorted_data:
                sorted_data[sorted_data_key] = []
            no_vop_transaction = {k: v for k, v in one_in_thousand_transaction[1].items() if k not in ignore_keys}
            sorted_data[sorted_data_key].append(no_vop_transaction)
            # sorted_data[sorted_data_key].append(one_in_thousand_transaction[1])
    return sorted_data


def compare_transaction(account_name: str, transaction_from, key_value_data):
    wrong_transactions = []
    ignore_keys = ('virtual_op', 'op_in_trx')
    for all_transactions in transaction_from:
        for one_in_thousand_transaction in all_transactions:
            data_key = (one_in_thousand_transaction[1]['block'], one_in_thousand_transaction[1]['timestamp'])
            no_vop_transaction = {k: v for k, v in one_in_thousand_transaction[1].items() if k not in ignore_keys}
            if one_in_thousand_transaction[1]['block'] < 62303034:
                if no_vop_transaction not in key_value_data[data_key]:
                    wrong_transactions.append(one_in_thousand_transaction)
    with open(f'/home/dev/Desktop/server_request_data/wrong_transaction/{account_name}_master_to_dev_wrong_transaction.json', 'w') as f:
        json.dump(wrong_transactions, f)
    return wrong_transactions


# dev last block    = 62245215
# master last block = 62246376
# deevelop to master
# compare_transaction(json_to_variable_opener(json_server_develop_data_stored), assign_transactions_keys(json_to_variable_opener(json_server_master_data_stored)))

# master do deva ~ KeyError: (62246376, '2022-03-01T16:08:09')
# compare_transaction(
#   json_to_variable_opener(json_server_master_data_stored),
#   assign_transactions_keys(json_to_variable_opener(json_server_develop_data_stored))
#   )

# json_to_variable_opener(json_server_develop_data_stored)
# assign_transactions_keys(json_to_variable_opener(json_server_master_data_stored))



#############################################BLOCKTRADES############################################
# blocktrades develop last 'block': 62303034
# blocktrades master last  'block': 62304998
# save_transaction_to_json(json_server_develop_data_stored, 'blocktrades', 0, get_last_transaction_number('blocktrades', server_develop_url), server_develop_url)
# save_transaction_to_json(json_server_master_data_stored, 'blocktrades', 0, get_last_transaction_number('blocktrades', server_master_url), server_master_url)

# json_to_variable_opener(json_server_master_data_stored)

# blocktrades develop to master
# compare_transaction(
#   'blocktrades',
#   json_to_variable_opener(json_server_develop_data_stored),
#   assign_transactions_keys(json_to_variable_opener(json_server_master_data_stored)))

# blocktrades master to develop ~ KeyError: (62246376, '2022-03-01T16:08:09')
compare_transaction(
    'blocktrades',
    json_to_variable_opener(json_server_master_data_stored),
    assign_transactions_keys(json_to_variable_opener(json_server_develop_data_stored))
)
