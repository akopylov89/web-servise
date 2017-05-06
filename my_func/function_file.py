import numpy
import types
import csv
import sys
import traceback
import decimal

types_for_correl = (types.ComplexType, types.LongType,
                    types.IntType, types.FloatType, decimal.Decimal)


def my_func_correl(input_list):
    output = {}
    for data in input_list:
        for key, value in data.items():
            output[key] = []
            value_vector = []
            time_vector = []
            for x, y in enumerate(value):
                if isinstance(y, types_for_correl):
                    value_vector.append(y)
                    time_vector.append(-x)
            if len(value_vector) > 1:
                result = numpy.corrcoef(time_vector, value_vector)
                coef = result[0][1]
            else:
                coef = 'NaN'
            output[key].append(coef)
    return output


# def my_func_regcorrel(reg_list):
#     output = {}
#     dep_vector = {}
#     indep_vector = {}
#     for key, value in reg_list[0].items():
#         indep_vector[key] = [x for x in value if isinstance(x, types_for_correl)]
#         dep_vector[key] = [y for y in reg_list[1][key] if isinstance(y, types_for_correl)]
#         if len(dep_vector[key]) > 1 and len(dep_vector[key]) == len(indep_vector[key]):
#             result = numpy.corrcoef(dep_vector[key], indep_vector[key])
#             output[key] = result[0][1]
#         else:
#             output[key] = "NaN"
#     return output


def my_func_regcorrel(vector):
    output = {}
    value_vector = {}
    rel_vector = {}
    for key, value in vector[1].items():
        value_vector[key] = [x for x in value if isinstance(x, types_for_correl)]
        rel_vector[key] = [y for y in vector[0][key] if isinstance(y, types_for_correl)]
    temp1 = {}
    temp2 = {}
    for key in value_vector:
        if len(value_vector[key]) > 1 and len(rel_vector[key]) > 1:
            temp1[key] = []
            temp2[key] = []
            for x, y in map(None, value_vector[key], rel_vector[key]):
                if x is None or y is None:
                    pass
                else:
                    temp1[key].append(x)
                    temp2[key].append(y)
            if len(value_vector[key]) > 1:
                corr = numpy.corrcoef(temp1[key], temp2[key])[0,1]
                if numpy.isnan(corr):
                    output[key] = [float('NaN')]
                else:
                    output[key] = [corr]
            else:
                output[key] = [None]
    return output


def my_func_csv_reader(csv_file, name='all'):
    output = []
    with open(csv_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace='"')
        for row in reader:
            if name != 'all':
                if name in str(row):
                    output.append(row)
            elif name == 'all' and row:
                output.append(row)
    return output


def my_func_reader_as_generator(csv_file, name='all'):
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, quotechar="'", delimiter=',',
                            quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            if name != 'all':
                if name in str(row):
                    yield row
            elif name == 'all' and row:
                yield row


def my_func_file_to_dict(csv_file):
    output = {}
    data_from_csv_file = my_func_reader_as_generator(csv_file)
    for row in data_from_csv_file:
        if row[0] not in output.keys():
            output[row[0]] = [row[1:]]
        else:
            output.get(row[0]).append(row[1:])
    return output


def my_func_ric_reader(csv_file):
    output = []
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, quotechar="'", delimiter=',',
                            quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            output.extend(row)
    return output


def my_func_ric_reader_as_gen(csv_file):
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
                yield row


def my_func_assertion(output_value, calc_value, formula, identifier,
                      difference_value):
    if isinstance(output_value, types_for_correl) \
            and isinstance(calc_value, types_for_correl):
        assert abs(output_value - calc_value) < difference_value
        result = (abs(output_value - calc_value) < difference_value)
    else:
        print output_value
        print calc_value
        assert output_value == calc_value
        result = (output_value == calc_value)
    print("{}{}{}".format("=" * 25, " Test Passed ", "=" * 25))
    print("Assertion {} for {}:\n".format(formula, identifier))
    print("-output:     {}\n-calculated: {}"
          .format(output_value, output_value))
    print("_"*60)
    return result


def my_func_error_printer(formula, identifier):
    print("{}{}{}".format("=" * 25, " !!!TEST FAILED!!! ", "=" * 25))
    _, _, tb = sys.exc_info()
    traceback.print_tb(tb)
    tb_info = traceback.extract_tb(tb)
    filename, line, func_err, text = tb_info[-1]
    print('Assertion error!')
    print('An error occurred on line {} in statement {}'
          .format(line, text))
    print('Input data:\n -formula: {}\n -identifier: {}\n'
          .format(formula, identifier))


def my_func_any_error_printer():
    print("{}{}{}".format("=" * 25, " !!!Test code error!!! ", "=" * 25))
    _, _, tb = sys.exc_info()
    traceback.print_tb(tb)
    tb_info = traceback.extract_tb(tb)
    filename, line, func_err, text = tb_info[-1]
    print('An error occurred on line {} in statement {}'
          .format(line, text))


def my_func_avail(input_list):
    output = {}
    for key, value in input_list[0].items():
        output[key] = []
        counter = 0
        for i in value:
            if i:
                output[key].append(i)
                counter += 1
            else:
                if input_list[1][key][counter]:
                    output[key].append(input_list[1][key][counter])
                    counter += 1
                else:
                    if input_list[2][key][counter]:
                        output[key].append(input_list[2][key][counter])
                    else:
                        output[key].append(None)
    return output
