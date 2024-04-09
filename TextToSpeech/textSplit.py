def split_string(input_string):
    max_length = 2500
    output_list = []
    start_index = 0

    while start_index < len(input_string):
        # Find the index of the closest period after the max length
        end_index = min(start_index + max_length, len(input_string))
        period_index = input_string[start_index:end_index].rfind('.')
        if period_index != -1:
            end_index = start_index + period_index + 1

        output_list.append(input_string[start_index:end_index].strip())
        start_index = end_index

    return output_list