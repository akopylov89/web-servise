import argparse
import my_func
import my_classes
from test_data import *

functions = {'CORREL': my_func.my_func_correl,
             'AVAIL': my_func.my_func_avail}

results_of_test = {'passed': 0,
                   'failed': 0,
                   'code_errors': 0}


def argument_parser():
    parser = argparse.ArgumentParser(prog='Test #1')
    parser.add_argument('-f', '--file_name', default='data_to_test.csv',
                        help='file with test data')
    parser.add_argument('-r', '--file_name_with_rics',
                        default='rics_to_test.csv',
                        help='file with ric test data')
    parser.add_argument('-t', '--request_type', default='soap',
                        help='request type - soap or rest. default = soap')
    parser.add_argument('-s', '--server', default='server1',
                        help='server data')
    parsed_args = parser.parse_args()
    return parsed_args


def send_request_and_get_response(formula, items,
                                  identifier, request_type, server):
    data_to_calculate_func = []
    if request_type == 'soap':
        output_from_adc_portal = my_classes.\
            SoapRequestSender(formula, identifier, test_output)\
            .set_address(server_dict[server]['address'])\
            .set_uuid(test_uuid)\
            .set_template(test_template)\
            .set_product_id(test_product_id)\
            .set_headers(test_headers)\
            .set_method(test_method)\
            .set_url(server_dict[server]['url'])\
            .send_request()\
            .parse_results()
        for item in items:
            data_to_calculate_func\
                .append(my_classes.SoapRequestSender(item, identifier, test_output)
                        .set_address(server_dict[server]['address'])
                        .set_uuid(test_uuid)
                        .set_template(test_template)
                        .set_product_id(test_product_id)
                        .set_headers(test_headers)
                        .set_method(test_method)
                        .set_url(server_dict[server]['url'])
                        .send_request()
                        .parse_results())
    else:
        output_from_adc_portal = my_classes\
            .RestRequestSender(formula, identifier, test_output)\
            .set_product_id(test_product_id)\
            .set_url(server_dict[server]['url'])\
            .set_headers(test_headers)\
            .send_request()\
            .parse_results()
        for item in items:
            data_to_calculate_func\
                .append(my_classes.RestRequestSender(item, identifier, test_output)
                        .set_product_id(test_product_id)
                        .set_url(server_dict[server]['url'])
                        .set_headers(test_headers)
                        .send_request()
                        .parse_results())
    return output_from_adc_portal, data_to_calculate_func


def response_verification(func_name, func_dict, response, test_formula):
    calculated_results = func_dict[func_name](response[1])
    for key in response[0].keys():
        counter = 0
        for value in response[0][key]:
            calc_value = calculated_results[key][counter]
            result = my_func.my_func_assertion(value,
                                               calc_value,
                                               test_formula,
                                               key,
                                               CORREL_DIF)
            counter += 1
            if result:
                results_of_test['passed'] += 1
            else:
                results_of_test['failed'] += 1


if __name__ == "__main__":
    test_formula = None
    args = argument_parser()
    test_data = my_func.my_func_file_to_dict(args.file_name)
    test_identifier = ','.join(my_func.my_func_ric_reader
                               (args.file_name_with_rics))
    try:
        for func in test_data:
            for single_test_data in test_data[func]:
                test_formula = "{0}({1})".format(func, ','.join(single_test_data))
                response = send_request_and_get_response(test_formula,
                                                         single_test_data,
                                                         test_identifier,
                                                         args.request_type,
                                                         args.server)
                response_verification(func, functions, response, test_formula)

    except AssertionError:
        my_func.my_func_error_printer(test_formula, test_identifier)

    except Exception:
        my_func.my_func_any_error_printer()
        results_of_test['code_errors'] += 1

    finally:
        print '\nTotal:\n- passed: {0},\n- failed: {1},\n- fails in code: {2}'\
            .format(results_of_test['passed'],
                    results_of_test['failed'],
                    results_of_test['code_errors'])
        print '_' * 60
