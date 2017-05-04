import numpy
import types
import csv
import sys
import traceback


def my_func_correl(input_list):
    cor_coef = {}
    types_for_correl = (types.ComplexType, types.LongType,
                        types.IntType, types.FloatType)
    for data in input_list:
        for key, value in data.items():
            cor_coef[key] = []
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
            cor_coef[key].append(coef)
    return cor_coef


def my_func_regcorrel(reg_list):
    dep_vector = []
    indep_vector = []
    types_for_correl = (types.ComplexType, types.LongType,
                        types.IntType, types.FloatType)
    for single_list in reg_list:
        for value in single_list:
            if isinstance(value, types_for_correl):
                if value in reg_list[0]:
                    dep_vector.append(value)
                else:
                    indep_vector.append(value)
    if len(dep_vector) > 1 and len(dep_vector) == len(indep_vector):
        result = numpy.corrcoef(dep_vector, indep_vector)
        cor_coef = result[0][1]
    else:
        cor_coef = "NaN"
    return cor_coef


def my_func_csv_reader(csv_file, name='all'):
    output_list = []
    with open(csv_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace='"')
        for row in reader:
            if name != 'all':
                if name in str(row):
                    output_list.append(row)
            elif name == 'all' and row:
                output_list.append(row)
    return output_list


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
    output_dict = {}
    data_from_csv_file = my_func_reader_as_generator(csv_file)
    for row in data_from_csv_file:
        if row[0] not in output_dict.keys():
            output_dict[row[0]] = [row[1:]]
        else:
            output_dict.get(row[0]).append(row[1:])
    return output_dict


def my_func_ric_reader(csv_file):
    output_list = []
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, quotechar="'", delimiter=',',
                            quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            output_list.extend(row)
    return output_list


def my_func_ric_reader_as_gen(csv_file):
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
                yield row


def my_func_assertion(output_value, calc_value, formula, identifier,
                      difference_value):
    types_for_correl = (types.ComplexType, types.LongType,
                        types.IntType, types.FloatType)
    if isinstance(output_value, types_for_correl) \
            and isinstance(calc_value, types_for_correl):
        assert abs(output_value - calc_value) < difference_value
        result = (abs(output_value - calc_value) < difference_value)
    else:
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
    output_dict = {}
    for key, value in input_list[0].items():
        output_dict[key] = []
        counter = 0
        for i in value:
            if i:
                output_dict[key].append(i)
                counter += 1
            else:
                if input_list[1][key][counter]:
                    output_dict[key].append(input_list[1][key][counter])
                    counter += 1
                else:
                    if input_list[2][key][counter]:
                        output_dict[key].append(input_list[2][key][counter])
                    else:
                        output_dict[key].append(None)
    return output_dict
