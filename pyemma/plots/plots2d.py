
# This file is part of PyEMMA.
#
# Copyright (c) 2014-2018 Computational Molecular Biology Group, Freie Universitaet Berlin (GER)
#
# PyEMMA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

import numpy as _np

__author__ = 'noe'


def _get_cmap(cmap):
    # matplotlib 2.0 deprecated 'spectral' colormap, renamed to nipy_spectral.
    from matplotlib import __version__
    version = tuple(map(int, __version__.split('.')))
    if cmap == 'spectral' and version >= (2, ):
        cmap = 'nipy_spectral'
    return cmap


def contour(
        x, y, z, ncontours=50, colorbar=True, fig=None, ax=None,
        method='linear', zlim=None, cmap=None):
    import matplotlib.pyplot as _plt
    cmap = _get_cmap(cmap)
    if cmap is None:
        cmap = 'jet'
    if ax is None:
        if fig is None:
            fig, ax = _plt.subplots()
        else:
            ax = fig.gca()
    _, ax, _ = plot_contour(
        x, y, z, ax=ax, cmap=cmap, nbins=100, ncontours=ncontours,
        method=method, cbar=colorbar, cax=None, cbar_label=None,
        zlim=None)
    return ax


def scatter_contour(
        x, y, z, ncontours=50, colorbar=True, fig=None,
        ax=None, cmap=None, outfile=None):
    """Contour plot on scattered data (x,y,z) and
    plots the positions of the points (x,y) on top.

    Parameters
    ----------
    x : ndarray(T)
        x-coordinates
    y : ndarray(T)
        y-coordinates
    z : ndarray(T)
        z-coordinates
    ncontours : int, optional, default = 50
        number of contour levels
    fig : matplotlib Figure object, optional, default = None
        the figure to plot into. When set to None the default
        Figure object will be used
    ax : matplotlib Axes object, optional, default = None
        the axes to plot to. When set to None the default Axes
        object will be used.
    cmap : matplotlib colormap, optional, default = None
        the color map to use. None will use pylab.cm.jet.
    outfile : str, optional, default = None
        output file to write the figure to. When not given,
        the plot will be displayed

    Returns
    -------
    ax : Axes object containing the plot

    """
    ax = contour(
        x, y, z, ncontours=ncontours, colorbar=colorbar,
        fig=fig, ax=ax, cmap=cmap)
    # scatter points
    ax.scatter(x , y, marker='o', c='b', s=5)
    # show or save
    if outfile is not None:
        ax.get_figure().savefig(outfile)
    return ax


def plot_free_energy(
        xall, yall, weights=None, ax=None, nbins=100,
        ncountours=100, offset=-1, avoid_zero_count=True,
        minener_zero=True, kT=1.0, vmin=0.0, vmax=None,
        cmap='spectral', cbar=True, cbar_label='Free energy (kT)'):
    """Free energy plot given 2D scattered data

    Builds a 2D-histogram of the given data points and plots -log(p)
    where p is the probability computed from the histogram count.

    Parameters
    ----------
    xall : ndarray(T)
        sample x-coordinates
    yall : ndarray(T)
        sample y-coordinates
    weights : ndarray(T), default = None
        sample weights. By default all samples have the same weight
    ax : matplotlib Axes object, default = None
        the axes to plot to. When set to None the default Axes object
        will be used.
    nbins : int, default=100
        number of histogram bins used in each dimension
    ncountours : int, default=100
        number of contours used
    offset : float, default=-1
        DEPRECATED and ineffective.
    avoid_zero_count : bool, default=True
        avoid zero counts by lifting all histogram elements to the
        minimum value before computing the free energy. If False,
        zero histogram counts will yield NaNs in the free energy
        which and thus regions that are not plotted.
    minener_zero : bool, default=True
        Shifts the energy minimum to zero. If False, will not
        shift at all.
    kT : float, default=1.0
        The value of kT in the desired energy unit. By default,
        will compute energies in kT (setting 1.0). If you want to
        measure the energy in kJ/mol at 298 K, use kT=2.479 and
        change the cbar_label accordingly.
    vmin : float or None, default=0.0
        Lowest energy that will be plotted
    vmax : float or None, default=None
        Highest energy that will be plotted
    cmap : matplotlib colormap, optional, default = None
        the color map to use. None will use pylab.cm.spectral.
    cbar : boolean, default=True
        plot a color bar
    cbar_label : str or None, default='Free energy (kT)'
        colorbar label string. Use None to suppress it.

    Returns
    -------
    fig : Figure object containing the plot

    ax : Axes object containing the plot

    """
    import warnings
    cmap = _get_cmap(cmap)
    # check input
    if offset != -1:
        warnings.warn(
            "Parameter offset is deprecated and will be ignored",
            DeprecationWarning)
    fig, ax, _ = plot_free_energy_new(
        xall, yall, weights=weights, ax=ax, cmap=cmap, nbins=nbins,
        ncontours=ncountours, avoid_zero_count=avoid_zero_count,
        cbar=cbar, cax=None, cbar_label=cbar_label,
        minener_zero=minener_zero, kt=kT)
    return fig, ax


# ######################################################################
#
# auxiliary functions to help constructing custom plots
#
# ######################################################################


def get_histogram(
        xall, yall, nbins=100,
        weights=None, avoid_zero_count=False):
    """Compute a two-dimensional histogram.

    Parameters
    ----------
    xall : ndarray(T)
        Sample x-coordinates.
    yall : ndarray(T)
        Sample y-coordinates.
    nbins : int, default=100
        Number of histogram bins used in each dimension.
    weights : ndarray(T), default=None
        Sample weights; by default all samples have the same weight.
    avoid_zero_count : bool, default=True
        Avoid zero counts by lifting all histogram elements to the
        minimum value before computing the free energy. If False,
        zero histogram counts would yield infinity in the free energy.

    Returns
    -------
    x : ndarray(nbins, nbins)
        The bins' x-coordinates in meshgrid format.
    y : ndarray(nbins, nbins)
        The bins' y-coordinates in meshgrid format.
    z : ndarray(nbins, nbins)
        Histogram counts in meshgrid format.

    """
    z, xedge, yedge = _np.histogram2d(
        xall, yall, bins=nbins, weights=weights)
    x = 0.5 * (xedge[:-1] + xedge[1:])
    y = 0.5 * (yedge[:-1] + yedge[1:])
    if avoid_zero_count:
        z = _np.maximum(z, _np.min(z[z.nonzero()]))
    return x, y, z


def get_grid_data(xall, yall, zall, nbins=100, method='nearest'):
    """Interpolate unstructured two-dimensional data.

    Parameters
    ----------
    xall : ndarray(T)
        Sample x-coordinates.
    yall : ndarray(T)
        Sample y-coordinates.
    zall : ndarray(T)
        Sample z-coordinates.
    nbins : int, optional, default=100
        Number of histogram bins used in x/y-dimensions.
    method : str, optional, default='nearest'
        Assignment method; scipy.interpolate.griddata supports the
        methods 'nearest', 'linear', and 'cubic'.

    Returns
    -------
    x : ndarray(nbins, nbins)
        The bins' x-coordinates in meshgrid format.
    y : ndarray(nbins, nbins)
        The bins' y-coordinates in meshgrid format.
    z : ndarray(nbins, nbins)
        Interpolated z-data in meshgrid format.

    """
    from scipy.interpolate import griddata
    x, y = _np.meshgrid(
        _np.linspace(xall.min(), xall.max(), nbins),
        _np.linspace(yall.min(), yall.max(), nbins),
        indexing='ij')
    z = griddata(
        _np.hstack([xall[:,None], yall[:,None]]),
        zall, (x, y), method=method)
    return x, y, z


def _to_density(z):
    """Normalize histogram counts.

    Parameters
    ----------
    z : ndarray(T)
        Histogram counts.

    """
    return z / float(z.sum())


def _to_free_energy(z, minener_zero=False):
    """Compute free energies from histogram counts.

    Parameters
    ----------
    z : ndarray(T)
        Histogram counts.
    minener_zero : boolean, optional, default=False
        Shifts the energy minimum to zero.

    Returns
    -------
    free_energy : ndarray(T)
        The free energy values in units of kT.

    """
    pi = _to_density(z)
    free_energy = _np.inf * _np.ones(shape=z.shape)
    nonzero = pi.nonzero()
    free_energy[nonzero] = -_np.log(pi[nonzero])
    if minener_zero:
        free_energy[nonzero] -= _np.min(free_energy[nonzero])
    return free_energy


def plot_map(
        x, y, z, ncontours=100, ax=None,
        cmap='Blues', vmin=None, vmax=None,
        cbar=True, cax=None, cbar_label=None,
        logscale=False, levels=None):
    """Plot a two-dimensional map.

    Parameters
    ----------
    x : ndarray(T)
        Binned x-coordinates.
    y : ndarray(T)
        Binned y-coordinates.
    z : ndarray(T)
        Binned z-coordinates.
    ncontours : int, optional, default=100
        Number of contour levels.
    ax : matplotlib.Axes object, optional, default=None
        The ax to plot to; if ax=None, a new ax (and fig) is created.
    cmap : matplotlib colormap, optional, default='Blues'
        The color map to use.
    vmin : float, optional, default=None
        Lowest z-value to be plotted.
    vmax : float, optional, default=None
        Highest z-value to be plotted.
    cbar : boolean, optional, default=True
        Plot a color bar.
    cax : matplotlib.Axes object, optional, default=None
        Plot the colorbar into a custom axes object instead of
        stealing space from ax.
    cbar_label : str, optional, default=None
        Colorbar label string; use None to suppress it.
    logscale : boolean, optional, default=False
        Plot the z-values in logscale.
    levels : iterable of float, optional, default=None
        Contour levels to plot.

    Returns
    -------
    fig : matplotlib.Figure object
        The figure in which the used ax resides.
    ax : matplotlib.Axes object
        The ax in which the map was plotted.
    cbar : matplotlib.Colorbar object
        The corresponding colorbar object; None if no colorbar
        was requested.

    """
    import matplotlib.pyplot as _plt
    if ax is None:
        fig, ax = _plt.subplots()
    else:
        fig = ax.get_figure()
    if logscale:
        from matplotlib.colors import LogNorm
        norm = LogNorm()
        z = _np.ma.masked_where(z <= 0, z)
    else:
        norm = None
        if vmin is None:
            vmin = _np.min(z)
        if vmax is None:
            vmax = _np.max(z)
    cs = ax.contourf(
        x, y, z, ncontours, norm=norm,
        vmin=vmin, vmax=vmax, cmap=cmap,
        levels=levels)
    if cbar:
        if cax is None:
            cbar = fig.colorbar(cs, ax=ax)
        else:
            cbar = fig.colorbar(cs, cax=cax)
        if cbar_label is not None:
            cbar.set_label(cbar_label)
    else:
        cbar = None
    return fig, ax, cbar


# ######################################################################
#
# new plotting functions
#
# ######################################################################
    

def plot_density(
        xall, yall, weights=None, ax=None, cmap='Blues',
        nbins=100, ncontours=100, avoid_zero_count=False,
        cbar=True, cax=None, cbar_label='density',
        logscale=False):
    """Plot a two-dimensional density map.

    Parameters
    ----------
    xall : ndarray(T)
        Sample x-coordinates.
    yall : ndarray(T)
        Sample y-coordinates.
    weights : ndarray(T), default=None
        Sample weights; by default all samples have the same weight.
    ax : matplotlib.Axes object, optional, default=None
        The ax to plot to; if ax=None, a new ax (and fig) is created.
        Number of contour levels.
    cmap : matplotlib colormap, optional, default='Blues'
        The color map to use.
    nbins : int, default=100
        Number of histogram bins used in each dimension.
    ncontours : int, optional, default=100
    avoid_zero_count : bool, default=False
        Avoid zero counts by lifting all histogram elements to the
        minimum value before computing the free energy. If False,
        zero histogram counts would yield infinity in the free energy.
    vmin : float, optional, default=None
    cbar : boolean, optional, default=True
        Plot a color bar.
    cax : matplotlib.Axes object, optional, default=None
        Plot the colorbar into a custom axes object instead of
        stealing space from ax.
    cbar_label : str, optional, default='density'
        Colorbar label string; use None to suppress it.
    logscale : boolean, optional, default=False
        Plot the density values in logscale.

    Returns
    -------
    fig : matplotlib.Figure object
        The figure in which the used ax resides.
    ax : matplotlib.Axes object
        The ax in which the map was plotted.
    cbar : matplotlib.Colorbar object
        The corresponding colorbar object; None if no colorbar
        was requested.

    """
    x, y, z = get_histogram(
        xall, yall, nbins=nbins,weights=weights,
        avoid_zero_count=avoid_zero_count)
    return plot_map(
        x, y, _to_density(z).T, ncontours=ncontours, ax=ax,
        cmap=cmap, cbar=cbar, cax=cax, cbar_label=cbar_label,
        logscale=logscale)
    

def plot_free_energy_new(
        xall, yall, weights=None, ax=None, cmap='nipy_spectral',
        nbins=100, ncontours=100, avoid_zero_count=False,
        cbar=True, cax=None, cbar_label='free energy / kT',
        minener_zero=True, kt=1.0):
    """Plot a two-dimensional free energy map.

    Parameters
    ----------
    xall : ndarray(T)
        Sample x-coordinates.
    yall : ndarray(T)
        Sample y-coordinates.
    weights : ndarray(T), default=None
        Sample weights; by default all samples have the same weight.
    ax : matplotlib.Axes object, optional, default=None
        The ax to plot to; if ax=None, a new ax (and fig) is created.
        Number of contour levels.
    cmap : matplotlib colormap, optional, default='nipy_spectral'
        The color map to use.
    nbins : int, default=100
        Number of histogram bins used in each dimension.
    ncontours : int, optional, default=100
    avoid_zero_count : bool, default=False
        Avoid zero counts by lifting all histogram elements to the
        minimum value before computing the free energy. If False,
        zero histogram counts would yield infinity in the free energy.
    vmin : float, optional, default=None
    cbar : boolean, optional, default=True
        Plot a color bar.
    cax : matplotlib.Axes object, optional, default=None
        Plot the colorbar into a custom axes object instead of
        stealing space from ax.
    cbar_label : str, optional, default='free energy / kT'
        Colorbar label string; use None to suppress it.
    minener_zero : boolean, optional, default=True
        Shifts the energy minimum to zero.
    kt : float, optional, default=1.0
        The value of kT in the desired energy unit. By default,
        energies are computed in kT (setting 1.0). If you want to
        measure the energy in kJ/mol at 298 K, use kt=2.479 and
        change the cbar_label accordingly.

    Returns
    -------
    fig : matplotlib.Figure object
        The figure in which the used ax resides.
    ax : matplotlib.Axes object
        The ax in which the map was plotted.
    cbar : matplotlib.Colorbar object
        The corresponding colorbar object; None if no colorbar
        was requested.

    """
    x, y, z = get_histogram(
        xall, yall, nbins=nbins, weights=weights,
        avoid_zero_count=avoid_zero_count)
    f = _to_free_energy(z, minener_zero=minener_zero) * kt
    return plot_map(
        x, y, f.T, ncontours=ncontours, ax=ax,
        cmap=cmap, cbar=cbar, cax=cax, cbar_label=cbar_label)


def plot_contour(
        xall, yall, zall, ax=None, cmap='viridis',
        nbins=100, ncontours=100, method='nearest',
        cbar=True, cax=None, cbar_label=None, zlim=None):
    """Plot a two-dimensional free energy map.

    Parameters
    ----------
    xall : ndarray(T)
        Sample x-coordinates.
    yall : ndarray(T)
        Sample y-coordinates.
    zall : ndarray(T)
        Sample z-coordinates.
    ax : matplotlib.Axes object, optional, default=None
        The ax to plot to; if ax=None, a new ax (and fig) is created.
        Number of contour levels.
    cmap : matplotlib colormap, optional, default='viridis'
        The color map to use.
    nbins : int, default=100
        Number of histogram bins used in each dimension.
    ncontours : int, optional, default=100
    method : str, optional, default='nearest'
        Assignment method; scipy.interpolate.griddata supports the
        methods 'nearest', 'linear', and 'cubic'.
    cbar : boolean, optional, default=True
        Plot a color bar.
    cax : matplotlib.Axes object, optional, default=None
        Plot the colorbar into a custom axes object instead of
        stealing space from ax.
    cbar_label : str, optional, default=None
        Colorbar label string; use None to suppress it.
    zlim : tuple of float, optional, default=None
        If None, zlim is set to (vmin, vmax); this parameter is only
        present for compatibility reasons.

    Returns
    -------
    fig : matplotlib.Figure object
        The figure in which the used ax resides.
    ax : matplotlib.Axes object
        The ax in which the map was plotted.
    cbar : matplotlib.Colorbar object
        The corresponding colorbar object; None if no colorbar
        was requested.

    """
    x, y, z = get_grid_data(
        xall, yall, zall, nbins=nbins, method='nearest')
    if zlim is None:
        zlim = (z.min(), z.max())
    eps = (zlim[1] - zlim[0]) / float(ncontours)
    levels = _np.linspace(zlim[0] - eps, zlim[1] + eps)
    return plot_map(
        x, y, z, ncontours=ncontours, ax=ax, cmap=cmap,
        cbar=cbar, cax=cax, cbar_label=cbar_label, levels=levels)
