import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binned_statistic
from matplotlib.colors import PowerNorm

import astropy.units as u

from cta_plots.colors import default_cmap, main_color, color_cycle
from cta_plots.coordinate_utils import calculate_distance_to_true_source_position
from cta_plots.binning import make_default_cta_binning
from . import load_angular_resolution_requirement
from .. import add_colorbar_to_figure


def plot_angular_resolution(reconstructed_events, reference, plot_e_reco, ylog=False, ylim=None, ax=None):

    df = reconstructed_events
    distance = calculate_distance_to_true_source_position(df)

    e_min, e_max = 0.01 * u.TeV, 180 * u.TeV
    bins, bin_center, _ = make_default_cta_binning(e_min=e_min, e_max=e_max)


    if plot_e_reco:
        x = df.gamma_energy_prediction_mean.values
    else:
        x = df.mc_energy.values

    y = distance

    b_68, bin_edges, _ = binned_statistic(x, y, statistic=lambda y: np.nanpercentile(y, 68), bins=bins)

    bin_centers = np.sqrt(bin_edges[1:] * bin_edges[:-1])
    # bins_y = np.logspace(np.log10(0.005), np.log10(50.8), 100)

    log_emin, log_emax = np.log10(0.007), np.log10(300)
    if not ylim:
        ylim = (0.01, 20) if ylog else (0, 1) 
    ymin, ymax = np.log10([0.01, 20]) if ylog else ylim
    
    if not ax:
        fig, ax = plt.subplots(1, 1)
    else:
        fig = plt.gcf()
    im = ax.hexbin(x, y, xscale='log', yscale='log' if ylog else None, extent=(log_emin, log_emax, ymin, ymax + 0.1), cmap=default_cmap)
    
    add_colorbar_to_figure(im, fig, ax, label='Counts')
    
    # hardcore fix for stupi step plotting artifact
    # b_68[-1] = b_68[-2]
    # ax.step(bin_edges[:-1], b_68, where='post', lw=2, color=main_color, label='68\\textsuperscript{th} Percentile')
    ax.hlines(b_68, bins[:-1], bins[1:], lw=2, color=main_color, label='68\\textsuperscript{th} Percentile')

    if reference:
        df = load_angular_resolution_requirement()
        ax.plot(df.energy, df.resolution, '--', color='#5b5b5b', label='Reference')

    ax.set_xscale('log')

    ax.set_ylabel('Distance to True Position / $\,^{\circ}$')
    if plot_e_reco:
        ax.set_xlabel('Estimated Energy / TeV')
    else:
        ax.set_xlabel('True Energy / TeV')
    ax.legend(framealpha=0)

    df = pd.DataFrame({
        'energy_prediction': bin_centers,
        'angular_resolution': b_68,
    })
    plt.tight_layout(pad=0, rect=(0, 0, 1.002, 1))
    return ax, df



def plot_angular_resolution_per_multiplicity(reconstructed_events, reference, plot_e_reco, ax=None):
    df_all = reconstructed_events

    e_min, e_max = 0.01 * u.TeV, 200 * u.TeV
    bins, bin_center, bin_width = make_default_cta_binning(e_min=e_min, e_max=e_max)

    if not ax:
        fig, ax = plt.subplots(1, 1)

    mults = [2, 4, 10]

    for m, color in zip(mults, color_cycle):
        df = df_all.query(f'num_triggered_telescopes == {m}')
        if len(df) < 5000:
            continue
        if plot_e_reco:
            x = df.gamma_energy_prediction_mean.values
        else:
            x = df.mc_energy.values

        distance = calculate_distance_to_true_source_position(df)

        b_68, _, _ = binned_statistic(x, distance, statistic=lambda y: np.nanpercentile(y, 68), bins=bins)

        # hardcore fix for stupi step plotting artifact
        ax.hlines(b_68, bins[:-1], bins[1:], lw=2, color=color, label=m)
        # b_68[-1] = b_68[-2]
        # ax.step(
        #     bins[:-1],
        #     b_68,
        #     where='post',
        #     color=color,
        #     label=m,
        # )

    if reference:
        df = load_angular_resolution_requirement()
        ax.plot(df.energy, df.resolution, '.', color='#5b5b5b', label='Prod3B Reference')

    ax.set_xscale('log')
    ax.set_ylabel('Angular Resolution (68 %) / $\,^{\circ}$')
    if plot_e_reco:
        ax.set_xlabel('Estimated Energy / TeV')
    else:
        ax.set_xlabel('True Energy / TeV')

    ax.set_xlim([0.007, 300])
    ax.legend(framealpha=0.5, title='Multiplicity')
    plt.tight_layout(pad=0, rect=(-0.011, 0, 1.006, 1))
    return ax

