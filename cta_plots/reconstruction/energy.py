import numpy as np
import pandas as pd
import astropy.units as u
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic
from . import load_energy_resolution_reference
from ..binning import make_default_cta_binning
from matplotlib.colors import PowerNorm
from cta_plots.colors import default_cmap, main_color, main_color_complement

from .. import add_colorbar_to_figure


def plot_resolution(e_true, e_reco, color='#5f218c', reference=False, method='cta', plot_e_reco=False, plot_bias=False, ax=None):

    if not ax:
        fig, ax = plt.subplots(1, 1)

    e_min, e_max = 0.01 * u.TeV, 180 * u.TeV
    bins, bin_center, _ = make_default_cta_binning(e_min=e_min, e_max=e_max)

    if plot_e_reco:
        e_x = e_reco
    else:
        e_x = e_true

    resolution = (e_reco - e_true) / e_true
    if method == 'relative':
        iqr, _, _ = binned_statistic(e_x, resolution, statistic=lambda y: ((np.nanpercentile(y, 84) - np.nanpercentile(y, 16)) / 2), bins=bins)
    elif method in ['absolute', 'cta']:
        iqr, _, _ = binned_statistic(e_x, resolution, statistic=lambda y: np.nanpercentile(np.abs(y), 68), bins=bins)



    median, _, _ = binned_statistic(e_x, resolution, statistic=np.nanmedian, bins=bins)

    max_y = 1.
    min_y = -0.5  # if method == 'relative' else 0
    bins_y = np.linspace(min_y, max_y, 40)

    log_emin, log_emax = np.log10(0.007), np.log10(300)
    # if method == 'relative':
    im = ax.hexbin(e_x, resolution, xscale='log', extent=(log_emin, log_emax, -1, max_y), cmap=default_cmap,)
    # else:
        # im = ax.hexbin(e_x, np.abs(resolution), xscale='log', extent=(log_emin, log_emax, -1, max_y), cmap=default_cmap,)
    
    add_colorbar_to_figure(im, fig, ax, label='Counts')

    ax.hlines(iqr, bins[:-1], bins[1:], lw=2, color=color, label='Resolution')
    
    if plot_bias:
        ax.hlines(median, bins[:-1], bins[1:], lw=1, color=color, label='Bias', alpha=0.8)

    if reference:
        df = load_energy_resolution_reference()
        ax.plot(df.energy, df.resolution, '--', color='#5b5b5b', label='Reference')

    ax.set_xscale('log')


    ax.set_ylabel('$E_\\text{Est} / E_\\text{T}  -  1$')
    if plot_e_reco:
        ax.set_xlabel('Estimated Energy / TeV')
    else:
        ax.set_xlabel('True Energy / TeV')
    
    ax.set_ylim([bins_y.min(), bins_y.max()])
    ax.set_xlim([0.007, 300])
    ax.legend(framealpha=0)

    df = pd.DataFrame({
        'energy_prediction': bin_center,
        'resolution': iqr,
        'median': median,
        'bias': median,
    })
    plt.tight_layout(pad=0, rect=(-0.02, 0, 1.002, 1))
    return ax, df


