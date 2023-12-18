from typing import List
import numpy as np
from scipy.stats import chisquare, kstest, chi2


def chi_square_relaxed(
    observed_frequencies: List[float],
    verbose: bool = False,
    allowed_rel_error: float = 0.05,
):
    """
    Perform a chi-square goodness-of-fit test for uniform distribution with relaxed error.

    :param observed_frequencies: List of observed frequencies in each bin.
    :param allowed_rel_error: Allowed relative error in each bin.
    :return: Chi-square statistic and p-value.
    """
    observed = np.array(observed_frequencies)
    expected_frequency = observed.sum() / len(observed)
    if verbose:
        print(f"Expected frequency: {expected_frequency}")
    allowed_dev = allowed_rel_error * expected_frequency
    if verbose:
        print(f"Allowed deviation: {allowed_dev}")
    deviations = np.abs(observed - expected_frequency)
    if verbose:
        print(f"Deviations: {deviations}")
    deviations = np.where(deviations <= allowed_dev, 0, deviations - allowed_dev)
    if verbose:
        print(f"Deviations: {deviations}")
    chi2_statistic = np.sum(deviations**2) / expected_frequency
    if verbose:
        print(f"Chi2 statistic: {chi2_statistic}")
    p_value = chi2.sf(chi2_statistic, len(observed) - 1)
    if verbose:
        print(f"p-value: {p_value}")
    return chi2_statistic, p_value



def chi_square_test(observed_frequencies: List[float], verbose: bool = False):
    """
    Perform a chi-square goodness-of-fit test for uniform distribution.

    :param observed_frequencies: List of observed frequencies in each bin.
    :return: Chi-square statistic and p-value.
    """
    expected_frequencies = [
        sum(observed_frequencies) / len(observed_frequencies)
    ] * len(observed_frequencies)
    chi2_statistic, p_value = chisquare(
        observed_frequencies, f_exp=expected_frequencies
    )
    if verbose:
        print(f"Chi2 statistic: {chi2_statistic}, p-value: {p_value}")
    return chi2_statistic, p_value


def kolmogorov_smirnov_uniform_test(data, verbose: bool = False):
    """
    Perform a Kolmogorov-Smirnov test for uniform distribution.

    :param data: List of observed values.
    :return: KS statistic and p-value.
    """
    # Normalize the data to be between 0 and 1 as KS test compares to a standard uniform distribution
    min_val, max_val = min(data), max(data)
    normalized_data = [(x - min_val) / (max_val - min_val) for x in data]

    ks_statistic, p_value = kstest(normalized_data, "uniform")
    if verbose:
        print(f"KS statistic: {ks_statistic}, p-value: {p_value}")
    return ks_statistic, p_value
