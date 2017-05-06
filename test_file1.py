import argparse
import my_func
import my_classes
from test_data import *
from threadsafe_print import threadsafe_print

functions = {'CORREL': my_func.my_func_correl,
             'AVAIL': my_func.my_func_avail,
             'REGCORREL': my_func.my_func_regcorrel}


results_of_test = {'passed': 0,
                   'failed': 0,
                   'code_errors': 0,
                   'failed_comparison': 0}


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


def send_full_request(formula, identifier, request_type, server):
    if request_type == 'soap':
        output_from_adc_portal = my_classes. \
            SoapRequestSender(formula, identifier, test_output) \
            .set_address(server_dict[server]['address']) \
            .set_uuid(test_uuid) \
            .set_template(test_template) \
            .set_product_id(test_product_id) \
            .set_headers(test_headers) \
            .set_method(test_method) \
            .set_url(server_dict[server]['url']) \
            .send_request() \
            .parse_results()
    else:
        output_from_adc_portal = my_classes \
            .RestRequestSender(formula, identifier, test_output) \
            .set_product_id(test_product_id) \
            .set_url(server_dict[server]['url']) \
            .set_headers(test_headers) \
            .send_request() \
            .parse_results()
    return output_from_adc_portal


def send_separate_items(items, identifier, request_type, server):
    data_to_calculate_func = []
    for item in items:
        if request_type == 'soap':
            data_to_calculate_func.append(
                my_classes.SoapRequestSender(item, identifier, test_output)
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
            data_to_calculate_func.append(
                my_classes.RestRequestSender(item, identifier, test_output)
                .set_product_id(test_product_id)
                .set_url(server_dict[server]['url'])
                .set_headers(test_headers)
                .send_request()
                .parse_results())
    return data_to_calculate_func


def record_failed_comparison(key, calc_value, adc_value):
    global results_of_test
    threadsafe_print('%s %s %s' % (key, calc_value, adc_value))
    results_of_test['failed_comparison'] += 1


# def response_verification(func_name, func_dict, adc_full_response,
#                           adc_separate_response, test_formula):
#     calculated_results = func_dict[func_name](adc_separate_response)
#     for key in adc_full_response.keys():
#         counter = 0
#         for adc_value in adc_full_response[key]:
#             calc_value = calculated_results[key][counter]
#             result = my_func.my_func_assertion(adc_value,
#                                                calc_value,
#                                                test_formula,
#                                                key,
#                                                CORREL_DIF)
#             counter += 1
#             if result:
#                 results_of_test['passed'] += 1
#             else:
#                 results_of_test['failed'] += 1


def response_verification(func_name, func_dict, adc_full_response,
                          adc_separate_response, formula):
    calculated_results = func_dict[func_name](adc_separate_response)
    for key in adc_full_response.keys():
        counter = 0
        for adc_value in adc_full_response[key]:
            calc_value = calculated_results[key][counter]



if __name__ == "__main__":
    test_formula = None
    args = argument_parser()
    test_data = my_func.my_func_file_to_dict(args.file_name)
    test_identifier = ','.join(my_func.my_func_ric_reader
                               (args.file_name_with_rics))
    try:
        for func in test_data:
            for single_test_data in test_data[func]:
                test_formula = "{0}({1})".format(func, ','
                                                 .join(single_test_data))
                full_response = send_full_request(test_formula,
                                                  test_identifier,
                                                  args.request_type,
                                                  args.server)
                separate_response = send_separate_items(single_test_data,
                                                        test_identifier,
                                                        args.request_type,
                                                        args.server)
                response_verification(func,
                                      functions,
                                      full_response,
                                      separate_response,
                                      test_formula)

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
