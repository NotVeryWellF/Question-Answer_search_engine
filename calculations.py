from math import floor
from math import pi, exp, sqrt


def distance(query_time_scope, document_publication_date, time_span):
    delta_start = abs(query_time_scope["start"] - document_publication_date.date())
    delta_end = abs(query_time_scope["end"] - document_publication_date.date())
    delta_sum = delta_start + delta_end
    months = floor(delta_sum.total_seconds()/(60*60*24*30) + 0.5)
    return 1.0 - months/(2*time_span)


def probability_of_time(number_of_temporal_expressions, time, temporal_data, h):
    if number_of_temporal_expressions == 0:
        return 0
    else:
        return (1/number_of_temporal_expressions)*sum([gaussian_kernel(h, time - tmp) for tmp in temporal_data])


def gaussian_kernel(h, x) -> float:
    x = floor(x.total_seconds()/(60*60*24*30) + 0.5)
    return (1/(sqrt(2*pi) * h))*exp(-(x**2)/(2*h))


