import argparse
import numpy
import Queue
from threading import Thread
import socket
import collections
from datetime import date, datetime
import my_func
import my_classes
from test_data import *
from threadsafe_print import threadsafe_print

functions = {'CORREL': my_func.my_func_correl,
             'AVAIL': my_func.my_func_avail,
             'REGCORREL': my_func.my_func_regcorrel}


results_of_test = {'successful_comparison': 0,
                   'failed_comparison': 0,
                   'code_errors': 0,
                   'non_null_comparison': 0}

faults = {}
timedout_messages = collections.deque()


def argument_parser():
    parser = argparse.ArgumentParser(prog='test_file1.py')
    parser.add_argument('-f', '--file_name', default='data_to_test.csv',
                        help='file with test data')
    parser.add_argument('-r', '--file_name_with_rics',
                        default='rics_to_test.csv',
                        help='file with ric test data')
    parser.add_argument('-t', '--request_type', default='soap',
                        help='request type - soap or rest. default = soap')
    parser.add_argument('-s', '--server', default='server1',
                        help='server data')
    parser.add_argument('-p', '--precision', default='1e-14',
                        help='precision for comparisons')
    parsed_args = parser.parse_args()
    return parsed_args


def check_if_faults_occured(input_dict):
    global faults
    if input_dict:
        for key, value in input_dict.items():
            faults[key] = value


def send_full_request(formula, identifier, request_type, server):
    print 'send full adc'
    if request_type == 'soap':
        output_object = my_classes. \
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
        check_if_faults_occured(output_object.faults_dict)
        output_from_adc_portal = output_object.output_dict
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
    print 'send separate'
    for item in items:
        if request_type == 'soap':
            output_object = (
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
            check_if_faults_occured(output_object.faults_dict)
            data_to_calculate_func.append(output_object.output_dict)
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


def start_request_in_threads(formula, items, identifier, request_type, server):
    print formula
    adc_thread = Thread(name='adc_thread', target=send_full_request,
                        args=(formula, identifier, request_type, server, ))
    item_thread = Thread(name='item_thread', target=send_separate_items,
                         args=(items, identifier, request_type, server,))
    adc_thread.start()
    print "ADC START"
    item_thread.start()
    print "ITEMS START"
    adc_thread.join()
    return adc_thread, item_thread


def response_verification(func_name, func_dict, adc_response,
                          adc_separate_response):
    global results_of_test
    calc_results = func_dict[func_name](adc_separate_response)
    for key in adc_response.keys():
        k = 0
        for adc_value in adc_response[key]:
            if adc_value is not None and not (isinstance(adc_value, float) and adc_value == float('NaN')):
                k += 1
        j = 0
        for calc_value in calc_results[key]:
            if calc_value is not None and not (isinstance(calc_value, float) and calc_value == float('NaN')):
                j += 1
        if len(adc_response[key][:k]) != len(calc_results[key][:j]) and k != 0 and j != 0:
            record_failed_comparison(key, calc_results[key], adc_response[key])
            return False
        if k == 0 and j != 0:
            record_failed_comparison(key, calc_results[key], adc_response[key])
            return False
        for i in range(0, k):
            adc_value = adc_response[key][i]
            calc_value = calc_results[key][i]
            if calc_value is not None or adc_value is not None:
                results_of_test['non_null_comparison'] += 1
            if calc_value is None and adc_value is None:
                pass
            elif calc_value is None and isinstance(adc_value, float) and numpy.isnan(adc_value):
                pass
            elif isinstance(calc_value, float) and numpy.isnan(calc_value) and adc_value is None:
                pass
            elif isinstance(calc_value, float) and isinstance(adc_value, float) and numpy.isnan(calc_value) and numpy.isnan(adc_value):
                pass
            elif calc_value == True and adc_value == 'True' or calc_value == 'True' and adc_value == True:
                pass
            elif calc_value == False and adc_value == 'False' or calc_value == 'False' and adc_value == False:
                pass
            elif calc_value == 0 and adc_value == 'False' or calc_value == 'False' and adc_value == 0:
                pass
            elif calc_value == 1 and adc_value == 'True' or calc_value == 'True' and adc_value == 1:
                pass
            elif calc_value == 0 and adc_value == False or calc_value == False and adc_value == 0:
                pass
            elif calc_value == 1 and adc_value == True or calc_value == True and adc_value == 1:
                pass
            elif calc_value == '0' and adc_value == 'False' or calc_value == 'False' and adc_value == '0':
                pass
            elif calc_value == '1' and adc_value == 'True' or calc_value == 'True' and adc_value == '1':
                pass
            elif calc_value == '0' and adc_value == False or calc_value == False and adc_value == '0':
                pass
            elif calc_value == '1' and adc_value == True or calc_value == True and adc_value == '1':
                pass
            elif calc_value == adc_value:
                pass
            elif isinstance(calc_value, basestring) and isinstance(calc_value, basestring) and calc_value != adc_value:
                try:
                    if abs((float(calc_value) - float(calc_value)) / float(adc_value)) > float(args.precision):
                        record_failed_comparison(key, calc_value, adc_value)
                        threadsafe_print('%s' % (abs((float(calc_value) - float(adc_value)) / float(adc_value))))
                        return False
                    else:
                        pass
                except:
                    record_failed_comparison(key, calc_value, adc_value)
                    return False
            elif isinstance(calc_value, basestring) ^ isinstance(calc_value, basestring):
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif calc_value is None and adc_value is not None:
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif calc_value is not None and adc_value is None:
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif adc_value == 0 and calc_value != 0 and abs(calc_value) > 2 ** -23:
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif calc_value == float('inf') and adc_value == float('inf'):
                pass
            elif calc_value == float('inf') and adc_value != float('inf'):
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif calc_value != float('inf') and adc_value == float('inf'):
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif calc_value == -float('inf') and adc_value == -float('inf'):
                pass
            elif calc_value == -float('inf') and adc_value != -float('inf'):
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif calc_value != -float('inf') and adc_value == -float('inf'):
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif adc_value == 0 and (calc_value == 0 or abs(calc_value) < 2 ** -23):
                pass
            elif isinstance(calc_value, str) and calc_value != adc_value:
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif isinstance(calc_value, str) and calc_value == adc_value:
                pass
            elif isinstance(calc_value, unicode) and calc_value == unicode(adc_value, 'UTF-8'):
                pass
            elif isinstance(calc_value, bool) and (calc_value != adc_value if not isinstance(adc_value, str) else calc_value != bool(adc_value)):
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif isinstance(calc_value, bool) and (calc_value == adc_value if not isinstance(adc_value, str) else calc_value == bool(adc_value)):
                pass
            elif isinstance(calc_value, date) and (calc_value != adc_value if not isinstance(adc_value, str) else calc_value != my_func.my_str_float_to_date(adc_value)):
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif isinstance(calc_value, date) and (calc_value == adc_value if not isinstance(adc_value, str) else calc_value == my_func.my_str_float_to_date(adc_value)):
                pass
            elif isinstance(calc_value, datetime) and calc_value != adc_value:
                record_failed_comparison(key, calc_value, adc_value)
                return False
            elif isinstance(calc_value, datetime) and calc_value == adc_value:
                pass
            elif abs(calc_value) < 1e-4 and abs(float(adc_value)) < 1e-4:
                pass
            elif abs((calc_value - float(adc_value)) / float(adc_value)) > float(args.precision):
                record_failed_comparison(key, calc_value, adc_value)
                threadsafe_print('%s' % (abs((calc_value - float(adc_value)) / float(adc_value))))
                return False
            elif abs((calc_value - float(adc_value)) / float(adc_value)) <= float(args.precision):
                pass

            else:
                record_failed_comparison(key, calc_value, adc_value)
                threadsafe_print('%s' % (abs((calc_value - float(adc_value)) / float(adc_value))))
                return False
        results_of_test['successful_comparison'] += 1
        return True


# if __name__ == "__main__":
#     test_formula = None
#     my_test_queue = Queue.Queue(100)
#     args = argument_parser()
#     test_data = my_func.my_func_file_to_dict(args.file_name)
#     test_identifier = ','.join(my_func.my_func_ric_reader
#                                (args.file_name_with_rics))
#     try:
#         for func in test_data:
#             for single_test_data in test_data[func]:
#                 test_formula = "{0}({1})".format(func, ','
#                                                  .join(single_test_data))
#                 full_response = send_full_request(test_formula,
#                                                   test_identifier,
#                                                   args.request_type,
#                                                   args.server)
#                 separate_response = send_separate_items(single_test_data,
#                                                         test_identifier,
#                                                         args.request_type,
#                                                         args.server)
#                 result = response_verification(func,
#                                                functions,
#                                                full_response,
#                                                separate_response)
#                 if result:
#                     my_func.my_func_result_print(test_formula, test_identifier)
#                 else:
#                     my_func.my_func_error_printer(test_formula, test_identifier)
#
#     except AssertionError:
#         my_func.my_func_error_printer(test_formula, test_identifier)
#
#     except Exception:
#         my_func.my_func_any_error_printer()
#         results_of_test['code_errors'] += 1
#
#     except socket.timeout:
#         threadsafe_print('#####request timeout!##### ' + str(test_formula))
#
#     finally:
#         print '\nTotal:\n- passed: {0},\n- failed: {1},\n- fails in code: {2}'\
#             .format(results_of_test['successful_comparison'],
#                     results_of_test['failed_comparison'],
#                     results_of_test['code_errors'])
#         print '_' * 60
#         print "non_null ",results_of_test['non_null_comparison']
#         print "faults: ", faults


if __name__ == "__main__":
    test_formula = None
    my_test_queue = Queue.Queue(100)
    args = argument_parser()
    test_data = my_func.my_func_file_to_dict(args.file_name)
    test_identifier = ','.join(my_func.my_func_ric_reader
                               (args.file_name_with_rics))
    counter = 0
    for func in test_data:
        for single_items in test_data[func]:
            my_test_queue.put({'function': func, 'items': single_items})
            counter += 1
    print my_test_queue
    for i in range(counter):
        q = my_test_queue.get()
        test_formula = "{0}({1})".format(q['function'], ','.join(q['items']))
        try:
            a = start_request_in_threads(test_formula, q['items'], test_identifier,
                                     args.request_type, args.server)
        finally:
            my_test_queue.task_done()
            print a


    # try:
    #     for func in test_data:
    #         for single_test_data in test_data[func]:
    #             test_formula = "{0}({1})".format(func, ','
    #                                              .join(single_test_data))
    #             full_response = send_full_request(test_formula,
    #                                               test_identifier,
    #                                               args.request_type,
    #                                               args.server)
    #             separate_response = send_separate_items(single_test_data,
    #                                                     test_identifier,
    #                                                     args.request_type,
    #                                                     args.server)
    #             result = response_verification(func,
    #                                            functions,
    #                                            full_response,
    #                                            separate_response)
    #             if result:
    #                 my_func.my_func_result_print(test_formula, test_identifier)
    #             else:
    #                 my_func.my_func_error_printer(test_formula, test_identifier)
    #
    # except AssertionError:
    #     my_func.my_func_error_printer(test_formula, test_identifier)
    #
    # except Exception:
    #     my_func.my_func_any_error_printer()
    #     results_of_test['code_errors'] += 1
    #
    # except socket.timeout:
    #     threadsafe_print('#####request timeout!##### ' + str(test_formula))
    #
    # finally:
    #     print '\nTotal:\n- passed: {0},\n- failed: {1},\n- fails in code: {2}'\
    #         .format(results_of_test['successful_comparison'],
    #                 results_of_test['failed_comparison'],
    #                 results_of_test['code_errors'])
    #     print '_' * 60
    #     print "non_null ",results_of_test['non_null_comparison']
    #     print "faults: ", faults
