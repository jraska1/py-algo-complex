import click
import numpy as np
from scipy.optimize import curve_fit

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
SAMPLE_COUNT = 100

REGRESSION_FUNCTIONS = {
    'O(1)':             (lambda x, a: a,                                        "{0:6f}"),
    'O(log n)':         (lambda x, a, b: a + b * np.log2(x),                    "{0:6f} + {1:6f} * log2(x)"),
    'O(n)':             (lambda x, a, b: a + b * x,                             "{0:6f} + {1:6f} * x"),
    'O(n log n)':       (lambda x, a, b: a + b * x * np.log2(x),                "{0:6f} + {1:6f} * x * log2(x)"),
    'O(n^2)':           (lambda x, a, b: a + b * np.power(x, 2, dtype=float),   "{0:6f} + {1:6f} * x^2"),
    'O(n^2 log n)':     (lambda x, a, b: a + b * np.power(x, 2, dtype=float) * np.log2(x),   "{0:6f} + {1:6f} * x^2 * log2(x)"),
    'O(n^3)':           (lambda x, a, b: a + b * np.power(x, 3, dtype=float),   "{0:6f} + {1:6f} * x^3"),
    'O(2^n)':           (lambda x, a, b: a + b * np.power(2, x, dtype=float),   "{0:6f} + {1:6f} * 2^x"),
}


def set_verbose(ctx, param, value):
    click.get_current_context().obj['verbose'] = value


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-x', '--x-value', type=int, help="Independent variable to predict execution time")
@click.option('--sample-count', type=int, default=SAMPLE_COUNT, show_default=True, help="Number of samples used for data normalization")
@click.option('--delimiter', type=str, default=' ', show_default=True, help="Field delimiter character")
@click.option('-v', '--verbose', count=True, callback=set_verbose, expose_value=False, help='To be more verbose')
@click.argument('src', type=click.File('r'))
def cli(x_value, sample_count, delimiter, src):
    """
    Algorithm Complexity Checker - tool for estimating complexity of software, computing regression parameters and predicting execution time.

    Produced by:   DSW - Dwarf Software Workshop

    Licence:       Apache Licence, version 2.0
    """

    verbose(">>> Phase Data Acquisition <<<", level=2)

    x_values, y_values = [], []
    for line in src:
        a, b = line.split(delimiter)
        x_values.append(int(a))
        y_values.append(float(b))
    verbose(f"SOURCE DATA X: {x_values}", level=2)
    verbose(f"SOURCE DATA Y: {y_values}", level=2)

    complexity = complexity_phase(x_values, y_values, sample_count)
    verbose(f"Algorithm Complexity Estimation: {complexity}", level=0)

    popt = regression_phase(x_values, y_values, complexity)
    verbose(f"Regression Function: {REGRESSION_FUNCTIONS[complexity][1].format(*popt)}", level=0)

    if x_value is not None:
        verbose(f"Predicted Execution Time: {predict_phase(complexity, x_value, popt):6f}", level=0)


def complexity_phase(x_values, y_values, samples):
    """
    Chooses algorithm complexity, which best suites provided data sample.

    :param x_values: independent variable representing sample data count
    :param y_values: dependent variable representing execution time (usually in seconds)
    :param samples:  number of samples used for normalization
    :return:         algorithm complexity label
    """

    verbose(">>> Phase Complexity Check <<<", level=2)

    x = np.array(x_values)
    y = np.array(y_values)

    xx = np.linspace(np.min(x), np.max(x), samples, dtype=int)
    yy = np.interp(xx, x, y)

    min_y = np.min(yy)
    max_y = np.max(yy)
    norm_x = np.arange(1, samples + 1)
    norm_y = (yy - min(y)) / (max_y - min_y)
    verbose(f"Normalized X: {norm_x}", level=2)
    verbose(f"Normalized Y: {norm_y}", level=2)

    complexity = {
        'O(1)':         (lambda v: np.ones(v.shape),                2.0),
        'O(log n)':     (lambda v: np.log2(v),                      np.log2(samples)),
        'O(n)':         (lambda v: v,                               samples),
        'O(n log n)':   (lambda v: v * np.log2(v),                  samples * np.log2(samples)),
        'O(n^2)':       (lambda v: np.power(v, 2),                  np.power(samples, 2)),
        'O(n^2 log n)': (lambda v: np.power(v, 2) * np.log2(v),     np.power(samples, 2) * np.log2(samples)),
        'O(n^3)':       (lambda v: np.power(v, 3),                  np.power(samples, 3)),
        'O(2^n)':       (lambda v: np.exp2(v),                      np.exp2(samples)),
    }

    res = []
    for comp, (func, coef) in complexity.items():
        z = np.sum(np.power(norm_y - func(norm_x) / coef, 2))
        res.append((comp, z))
    verbose(f"Least Squares Results: {res}", level=1)
    return min(res, key=lambda a: a[1])[0]


def regression_phase(x_values, y_values, label):
    """
    Computes regression function parameters.

    :param x_values: independent variable representing sample data count
    :param y_values: dependent variable representing execution time (usually in seconds)
    :param label:    complexity label
    :return:         regression function parameters
    """

    verbose(">>> Phase Regression Computing <<<", level=4)

    x = np.array(x_values, dtype=float)
    y = np.array(y_values, dtype=float)

    popt, pcov = curve_fit(REGRESSION_FUNCTIONS[label][0], x, y)
    verbose(f"Regression Function Parameters: {popt}", level=1)
    verbose(f"Regression Parameters Error: {np.sqrt(np.diag(pcov))}", level=1)

    return popt


def predict_phase(label, x, popt):
    """
    Evaluates algorithm complexity function for provided variable and computed parameters.

    :param label:   complexity label
    :param x:       independent variable
    :param popt:    complexity function parameters
    :return:        function evaluation result
    """

    verbose(">>> Phase Execution Time Prediction <<<", level=2)

    return REGRESSION_FUNCTIONS[label][0](x, *popt)


def verbose(message, *, level=1):
    """
    Write a message to stdout, if the verbose flag is set on.
    :param message: message to be written
    :param level:   required level of verbosity
    """
    if click.get_current_context().obj.get('verbose', 0) >= level:
        print(message)


if __name__ == '__main__':
    cli(obj={})
