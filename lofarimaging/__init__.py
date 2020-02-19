"""Functions for working with LOFAR single station data"""

__all__ = ["sb_from_freq", "freq_from_sb", "find_caltable", "read_caltable",
           "rcus_in_station", "read_acm_cube", "get_background_image",
           "sky_imager", "ground_imager"]

__version__ = "1.5.0"

# Configurations for HBA observations with a single dipole activated per tile.
GENERIC_INT_201512 = [0, 5, 3, 1, 8, 3, 12, 15, 10, 13, 11, 5, 12, 12, 5, 2, 10, 8, 0, 3, 5, 1, 4, 0, 11, 6, 2, 4, 9, 14, 15, 3, 7, 5, 13, 15, 5, 6, 5, 12, 15, 7, 1, 1, 14, 9, 4, 9, 3, 9, 3,
                      13, 7, 14, 7, 14, 2, 8, 8, 0, 1, 4, 2, 2, 12, 15, 5, 7, 6, 10, 12, 3, 3, 12, 7, 4, 6, 0, 5, 9, 1, 10, 10, 11, 5, 11, 7, 9, 7, 6, 4, 4, 15, 4, 1, 15]
GENERIC_CORE_201512 = [0, 10, 4, 3, 14, 0, 5, 5, 3, 13, 10, 3, 12, 2, 7, 15, 6, 14, 7, 5, 7, 9, 0, 15, 0, 10, 4, 3, 14, 0, 5, 5, 3, 13, 10, 3, 12, 2, 7, 15, 6, 14, 7, 5, 7, 9, 0, 15];
GENERIC_REMOTE_201512 = [0, 13, 12, 4, 11, 11, 7, 8, 2, 7, 11, 2, 10, 2, 6, 3, 8, 3, 1, 7, 1, 15, 13, 1, 11, 1, 12, 7, 10, 15, 8, 2, 12, 13, 9, 13, 4, 5, 5, 12, 5, 5, 9, 11, 15, 12, 2, 15];

import numpy as np
import os
from matplotlib.pyplot import imread
import folium
import datetime
import lofargeotiff

from scipy import ndimage

from lofarantpos.db import LofarAntennaDatabase

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib import cm
from matplotlib.colors import ListedColormap
import warnings
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.axes as maxes

from astropy.coordinates import SkyCoord, ICRS, EarthLocation, AltAz, SkyOffsetFrame, CartesianRepresentation, get_sun, get_moon
import astropy.units as u
from astropy.time import Time

import lofarantpos
from packaging import version
assert(version.parse(lofarantpos.__version__) >= version.parse("0.4.0"))


def sb_from_freq(freq: float, rcu_mode='1', clock=200.e6):
    """
    Convert subband number to central frequency
    
    Args:
        rcu_mode: rcu mode
        freq: frequency in Hz
        clock: clock speed in Hz

    Returns:
        int: subband number
    """
    chan = 0.5 * clock / 512.
    freq_offset = 0
    if str(rcu_mode) in ['5', '6']:
        freq_offset = 100e6
    sb = round((freq - freq_offset) / chan)
    return int(sb)


def freq_from_sb(sb: int, rcu_mode='1', clock=200e6):
    """
    Convert central frequency to subband number

    Args:
        rcu_mode: rcu mode
        sb: subband number
        clock: clock speed in Hz

    Returns:
        float: frequency in Hz
    """
    chan = 0.5 * clock / 512.
    freq = (sb * chan)
    if str(rcu_mode) in ['5', '6']:
        freq += 100e6
    return freq


def skycoord_to_lmn(pos: SkyCoord, phasecentre: SkyCoord):
    """
    Convert astropy sky coordinates into the l,m,n coordinate system
    relative to a phase centre.

    The l,m,n is a RHS coordinate system with
    * its origin on the sky sphere
    * m,n and the celestial north on the same plane
    * l,m a tangential plane of the sky sphere

    Note that this means that l increases east-wards
    """

    # Determine relative sky position
    todc = pos.transform_to(SkyOffsetFrame(origin=phasecentre))
    dc = todc.represent_as(CartesianRepresentation)
    dc /= dc.norm()

    # Do coordinate transformation - astropy's relative coordinates do
    # not quite follow imaging conventions
    return dc.y.value, dc.z.value, dc.x.value - 1


def find_caltable(field_name: str, rcu_mode: str, config_dir='caltables'):
    """
    Find the file of a caltable.

    Args:
        field_name: Name of the antenna field, e.g. 'DE602LBA'
        rcu_mode: Receiver mode for which the calibration table is requested.
            Probably should be  'inner' or 'outer'
        config_dir: Root directory under which station information is stored in
            subdirectories DE602C/etc/, RS106/etc/, ...

    Returns:
        str: filename if it exists, None if nothing found
    """
    station, field = field_name[0:5].upper(), field_name[5:].upper()
    station_number = station[2:5]

    # Map to the correct file depending on the RCU mode
    if rcu_mode == 'outer' and 'LBA' in field_name:
        filename = os.path.join(config_dir, f"CalTable-{station_number}-LBA_OUTER-10_90.dat")
    elif rcu_mode == 'inner' and 'LBA' in field_name:
        filename = os.path.join(config_dir, f"CalTable-{station_number}-LBA_INNER-10_90.dat")
    else:
        filename = os.path.join(config_dir, f"CalTable_{station_number}_mode{rcu_mode}.dat")

    if os.path.exists(filename):
        return filename

    # If the original folder structure is kept
    if rcu_mode == 'outer' and 'LBA' in field_name:
        filename = os.path.join(config_dir, f"{station}/CalTable-{station_number}-LBA_OUTER-10_90.dat")
    elif rcu_mode == 'inner' and 'LBA' in field_name:
        filename = os.path.join(config_dir, f"{station}/CalTable-{station_number}-LBA_INNER-10_90.dat")
    else:
        filename = os.path.join(config_dir, f"{station}/CalTable_{station_number}_mode{rcu_mode}.dat")

    if os.path.exists(filename):
        return filename
    else:
        return None


def read_caltable(filename: str, num_subbands=512):
    """
    Read a station's calibration table.

    Args:
        filename: Filename with the caltable
        num_subbands: Number of subbands

    Returns:
        Tuple(List[str], np.array): A tuple containing a list of strings with
            the header lines, and a 2D numpy.array of complex numbers
            representing the station gain coefficients.
    """
    infile = open(filename, 'rb')

    header_lines = []

    try:
        while True:
            header_lines.append(infile.readline().decode('utf8'))
            if 'HeaderStop' in header_lines[-1]:
                break
    except UnicodeDecodeError:
        # No header; close and open again
        infile.close()
        infile = open(filename, 'rb')

    caldata = np.fromfile(infile, dtype=np.complex128)
    num_rcus = len(caldata) // num_subbands

    infile.close()

    return header_lines, caldata.reshape((num_subbands, num_rcus))


def rcus_in_station(station_type: str):
    """
    Give the number of RCUs in a station, given its type.

    Args:
        station_type: Kind of station that produced the correlation. One of
            'core', 'remote', 'intl'.
    """
    return {'core': 96, 'remote': 96, 'intl': 192}[station_type]


def read_acm_cube(filename: str, station_type: str):
    """
    Read an ACM binary data cube (function from Michiel)

    Args:
        filename: File containing the array correlation matrix.
        station_type: Kind of station that produced the correlation. One of
            'core', 'remote', 'intl'.

    Returns:
        np.array: 3D cube of complex numbers, with indices [time slots, rcu, rcu].

    Examples:
    >>> cube = read_acm_cube('20170720_095816_xst.dat', 'intl')
    >>> cube.shape
    (29, 192, 192)
    """
    num_rcu = rcus_in_station(station_type)
    data = np.fromfile(filename, dtype=np.complex128)
    time_slots = int(len(data) / num_rcu / num_rcu)
    return data.reshape((time_slots, num_rcu, num_rcu))


def get_background_image(lon_min, lon_max, lat_min, lat_max, zoom=19):
    """
    Get an ESRI World Imagery map of the selected region
    Args:
        lon_min: Minimum longitude (degrees)
        lon_max: Maximum longitude (degrees)
        lat_min: Minimum latitude (degrees)
        lat_max: Maximum latitude (degrees)
        zoom: Zoom level

    Returns:
        np.array: Numpy array which can be plotted with plt.imshow
    """
    from owslib.wmts import WebMapTileService
    import mercantile

    wmts = WebMapTileService("http://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/WMTS/1.0.0/WMTSCapabilities.xml")

    upperleft_tile = mercantile.tile(lon_min, lat_max, zoom)
    xmin, ymin = upperleft_tile.x, upperleft_tile.y
    lowerright_tile = mercantile.tile(lon_max, lat_min, zoom)
    xmax, ymax = lowerright_tile.x, lowerright_tile.y

    total_image = np.zeros([256 * (ymax - ymin + 1), 256 * (xmax - xmin + 1), 3], dtype='uint8')

    tile_min = mercantile.tile(lon_min, lat_min, zoom)
    tile_max = mercantile.tile(lon_max, lat_max, zoom)

    for x in range(tile_min.x, tile_max.x + 1):
        for y in range(tile_max.y, tile_min.y + 1):
            tile = wmts.gettile(layer="World_Imagery", tilematrix=str(zoom), row=y, column=x)
            out = open("tmp.jpg", "wb")
            out.write(tile.read())
            out.close()
            tile_image = imread("tmp.jpg")
            total_image[(y - ymin) * 256: (y - ymin + 1) * 256,
                        (x - xmin) * 256: (x - xmin + 1) * 256] = tile_image

    total_lonlatmin = {'lon': mercantile.bounds(xmin, ymax, zoom).west, 'lat': mercantile.bounds(xmin, ymax, zoom).south}
    total_lonlatmax = {'lon': mercantile.bounds(xmax, ymin, zoom).east, 'lat': mercantile.bounds(xmax, ymin, zoom).north}

    pix_xmin = int(round(np.interp(lon_min, [total_lonlatmin['lon'], total_lonlatmax['lon']], [0, total_image.shape[1]])))
    pix_ymin = int(round(np.interp(lat_min, [total_lonlatmin['lat'], total_lonlatmax['lat']], [0, total_image.shape[0]])))
    pix_xmax = int(round(np.interp(lon_max, [total_lonlatmin['lon'], total_lonlatmax['lon']], [0, total_image.shape[1]])))
    pix_ymax = int(round(np.interp(lat_max, [total_lonlatmin['lat'], total_lonlatmax['lat']], [0, total_image.shape[0]])))
    return total_image[total_image.shape[0]-pix_ymax: total_image.shape[0]-pix_ymin, pix_xmin: pix_xmax]


SPEED_OF_LIGHT = 299792458.0


def sky_imager(visibilities, baselines, freq, npix_l, npix_m):
    """Do a Fourier transform for sky imaging"""
    img = np.zeros([npix_m, npix_l], dtype=np.float32)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Casting complex values to real discards the imaginary part")
        for m_ix, m in enumerate(np.linspace(-1, 1, npix_l)):
            for l_ix, l in enumerate(np.linspace(1, -1, npix_m)):
                img[m_ix, l_ix] = np.mean(visibilities *
                                          np.exp(-2j * np.pi * freq *
                                                 (baselines[:, :, 0] * l + baselines[:, :, 1] * m) / SPEED_OF_LIGHT))
    return img


def ground_imager(visibilities, baselines, freq, npix_p, npix_q, dims, station_pqr, height=1.5):
    """Do a Fourier transform for ground imaging"""
    img = np.zeros([npix_q, npix_p], dtype=np.float32)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Casting complex values to real discards the imaginary part")
        for q_ix, q in enumerate(np.linspace(dims[2], dims[3], npix_q)):
            for p_ix, p in enumerate(np.linspace(dims[0], dims[1], npix_p)):
                r = height
                pqr = np.array([p, q, r], dtype=np.float32)
                antdist = np.linalg.norm(station_pqr - pqr[np.newaxis, :], axis=1)
                groundbase = antdist[:, np.newaxis] - antdist[np.newaxis, :]
                # Note: this is RFI integration second - normal second, to take out interference
                img[q_ix, p_ix] = np.mean(visibilities * np.exp(-2j * np.pi * freq * (-groundbase) / SPEED_OF_LIGHT))
    return img


def make_ground_image(xst_filename,
                      station_name,
                      caltable_dir,
                      extent=None,
                      pixels_per_metre=0.5,
                      sky_vmin=None,
                      sky_vmax=None,
                      ground_vmin=None,
                      ground_vmax=None,
                      height=1.5,
                      map_zoom=19):
    """Make a ground image"""
    cubename = os.path.basename(xst_filename)

    if extent is None:
        extent = [-150, 150, -150, 150]

    if station_name[0] == "C":
        station_type = "core"
    elif station_name[0] == "R" or station_name[:5] == "PL611":
        station_type = "remote"
    else:
        station_type = "intl"

    try:
        os.mkdir('results')
    except FileExistsError:
        pass

    # Distill metadata from filename
    obsdatestr, obstimestr, _, rcu_mode, _, subbandname = cubename.rstrip(".dat").split("_")
    subband = int(subbandname[2:])

    # Needed for NL stations: inner (rcu_mode 3/4), outer (rcu_mode 1/2), (sparse tbd)
    # Should be set to 'inner' if station type = 'intl'
    array_type = None
    if rcu_mode in ('1', '2'):
        array_type = 'outer'
    elif rcu_mode in ('3', '4'):
        array_type = 'inner'
    elif rcu_mode in ('5', '6', '7'):
        array_type = rcu_mode
    else:
        raise Exception("Unexpected rcu_mode: ", rcu_mode)

    # Get the data
    fname = f"{obsdatestr}_{obstimestr}_{station_name}_SB{subband}"

    npix_l, npix_m = 101, 101
    freq = freq_from_sb(subband, rcu_mode=rcu_mode)

    # Which slice in time to visualise
    timestep = 0

    # For ground imaging
    ground_resolution = pixels_per_metre  # pixels per metre for ground_imaging, default is 0.5 pixel/metre

    obstime = datetime.datetime.strptime(obsdatestr + ":" + obstimestr, '%Y%m%d:%H%M%S')

    cube = read_acm_cube(xst_filename, station_type)

    # Apply calibration

    caltable_filename = find_caltable(station_name, rcu_mode=array_type,
                                      config_dir=caltable_dir)

    if caltable_filename is None:
        print('No calibration table found... cube remains uncalibrated!')
    else:
        cal_header, cal_data = read_caltable(caltable_filename)

        rcu_gains = cal_data[subband, :]
        rcu_gains = np.array(rcu_gains, dtype=np.complex64)
        gain_matrix = rcu_gains[np.newaxis, :] * np.conj(rcu_gains[:, np.newaxis])
        cube = cube / gain_matrix

    # Split into the XX and YY polarisations (RCUs)
    # This needs to be modified in future for LBA sparse
    cube_xx = cube[:, 0::2, 0::2]
    cube_yy = cube[:, 1::2, 1::2]
    visibilities_all = cube_xx + cube_yy

    # Stokes I for specified timestep
    visibilities = visibilities_all[timestep]

    # Setup the database
    db = LofarAntennaDatabase()

    station_pqr = None
    if 'LBA' in station_name:
        # Get the PQR positions for an individual station
        station_pqr = db.antenna_pqr(station_name)

        # Exception: for Dutch stations (sparse not yet accommodated)
        if (station_type == 'core' or station_type == 'remote') and array_type == 'inner':
            station_pqr = station_pqr[0:48, :]
        elif (station_type == 'core' or station_type == 'remote') and array_type == 'outer':
            station_pqr = station_pqr[48:, :]
    elif 'HBA' in station_name:
        selected_dipole_config = {
            'intl': GENERIC_INT_201512, 'remote': GENERIC_REMOTE_201512, 'core': GENERIC_CORE_201512
        }
        selected_dipoles = selected_dipole_config[station_type] + np.arange(96) * 16
        station_pqr = db.hba_dipole_pqr(station_name)[selected_dipoles]
    else:
        raise RuntimeError("Station name did not contain LBA or HBA, could not load antenna positions")

    station_pqr = station_pqr.astype('float32')

    baselines = station_pqr[:, np.newaxis, :] - station_pqr[np.newaxis, :, :]

    rotation = np.rad2deg(db.rotation_from_north(station_name))

    # Make a sky image, by numerically Fourier-transforming from visibilities to image plane
    from matplotlib.patches import Circle

    # Fourier transform, and account for the rotation (rotation is positive in this space)
    # visibilities = cube_xx[2,:,:]
    img = sky_imager(visibilities, baselines, freq, npix_l, npix_m)
    img = ndimage.interpolation.rotate(img, -rotation, reshape=False, mode='nearest')

    # Determine positions of Cas A and Cyg A
    station_earthlocation = EarthLocation.from_geocentric(*(db.phase_centres[station_name] * u.m))
    zenith = AltAz(az=0 * u.deg, alt=90 * u.deg, obstime=obstime,
                   location=station_earthlocation).transform_to(ICRS)
    marked_bodies = {
        'Cas A': SkyCoord(ra=350.85*u.deg, dec=58.815*u.deg),
        'Cyg A': SkyCoord(ra=299.868*u.deg, dec=40.734*u.deg),
        'Per A': SkyCoord.from_name("Perseus A"),
        'Her A': SkyCoord.from_name("Hercules A"),
        'Cen A': SkyCoord.from_name("Centaurus A"),
        '3C295': SkyCoord.from_name("3C295"),
        'Moon': get_moon(Time(obstime), location=station_earthlocation).transform_to(ICRS),
        '3C196': SkyCoord.from_name("3C196")
    }

    marked_bodies_lmn = {}
    for body_name, body_coord in marked_bodies.items():
        #print(body_name, body_coord.separation(zenith), body_coord.separation(zenith))
        if body_coord.separation(zenith) > 0:
            marked_bodies_lmn[body_name] = skycoord_to_lmn(marked_bodies[body_name], zenith)

    # Plot the resulting sky image
    fig, ax = plt.subplots(1)

    circle1 = Circle((0, 0), 1.0, edgecolor='k', fill=False, facecolor='none', alpha=0.3)
    ax.add_artist(circle1)

    cimg = ax.imshow(img, origin='lower', cmap=cm.Spectral_r, extent=(-1, 1, -1, 1),
                     clip_path=circle1, clip_on=True, vmin=sky_vmin, vmax=sky_vmax)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.2, axes_class=maxes.Axes)
    fig.colorbar(cimg, cax=cax, orientation="vertical", format="%.1e")

    ax.set_xticks(np.arange(-1, 1.1, 0.5))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.set_yticks(np.arange(-1, 1.1, 0.5))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    # Labels
    ax.set_xlabel('$ℓ$', fontsize=14)
    ax.set_ylabel('$m$', fontsize=14)

    for body_name, lmn in marked_bodies_lmn.items():
        ax.annotate(body_name, (-lmn[0], lmn[1]))

    ax.set_title(f"Sky image for {station_name}\nSB {subband} ({freq / 1e6:.1f} MHz), {str(obstime)[:16]}", fontsize=16)

    # Plot the compass directions
    ax.text(0.9, 0, 'W', horizontalalignment='center', verticalalignment='center', color='w', fontsize=17)
    ax.text(-0.9, 0, 'E', horizontalalignment='center', verticalalignment='center', color='w', fontsize=17)
    ax.text(0, 0.9, 'N', horizontalalignment='center', verticalalignment='center', color='w', fontsize=17)
    ax.text(0, -0.9, 'S', horizontalalignment='center', verticalalignment='center', color='w', fontsize=17)

    plt.savefig(f'results/{fname}_sky_calibrated.png', bbox_inches='tight', dpi=200)
    plt.close(fig)

    from shapely import affinity, geometry

    def extent_from_shapely(minx, miny, maxx, maxy):
        return minx, maxx, miny, maxy

    def extent_to_shapely(minx, maxx, miny, maxy):
        return minx, miny, maxx, maxy

    to_plot_xyz = affinity.rotate(
            affinity.rotate(
                    geometry.box(*extent_to_shapely(*extent)),
                    rotation, origin=(0, 0)).envelope,
            -rotation, origin=(0, 0))

    to_plot_pqr = db.pqr_to_localnorth(station_name)[:2, :2].T @ (np.asarray(to_plot_xyz.exterior.coords[:4])).T
    extent_pqr = (np.min(to_plot_pqr[0, :]), np.max(to_plot_pqr[0, :]), np.min(to_plot_pqr[1, :]), np.max(to_plot_pqr[1, :]))

    npix_p, npix_q = int(ground_resolution * (extent[1] - extent[0])), int(ground_resolution * (extent[3] - extent[2]))

    img = ground_imager(visibilities, baselines, freq, npix_p, npix_q, extent_pqr, station_pqr, height=height)
    img_rotated = ndimage.interpolation.rotate(img, rotation, mode='constant', cval=np.nan)

    outer_extent_xyz = extent_from_shapely(*(to_plot_xyz.envelope.bounds))  # Extent in xyz coordinates of the rotated image.

    # Convert bottom left and upper right to PQR just for lofargeo
    pmin, qmin, _ = db.pqr_to_localnorth(station_name).T @ (np.array([extent[0], extent[2], 0]))
    pmax, qmax, _ = db.pqr_to_localnorth(station_name).T @ (np.array([extent[1], extent[3], 0]))
    lon_center, lat_center, _ = lofargeotiff.pqr_to_longlatheight([0, 0, 0], station_name)
    lon_min, lat_min, _ = lofargeotiff.pqr_to_longlatheight([pmin, qmin, 0], station_name)
    lon_max, lat_max, _ = lofargeotiff.pqr_to_longlatheight([pmax, qmax, 0], station_name)

    # Convert bottom left and upper right to PQR just for lofargeo
    outer_pmin, outer_qmin, _ = db.pqr_to_localnorth(station_name).T @ (np.array([outer_extent_xyz[0], outer_extent_xyz[2], 0]))
    outer_pmax, outer_qmax, _ = db.pqr_to_localnorth(station_name).T @ (np.array([outer_extent_xyz[1], outer_extent_xyz[3], 0]))
    outer_lon_min, outer_lat_min, _ = lofargeotiff.pqr_to_longlatheight([outer_pmin, outer_qmin, 0], station_name)
    outer_lon_max, outer_lat_max, _ = lofargeotiff.pqr_to_longlatheight([outer_pmax, outer_qmax, 0], station_name)

    background_image = get_background_image(lon_min, lon_max, lat_min, lat_max, zoom=map_zoom)

    # Make colors semi-transparent in the lower 3/4 of the scale
    cmap = cm.Spectral_r
    cmap_with_alpha = cmap(np.arange(cmap.N))
    cmap_with_alpha[:, -1] = np.clip(np.linspace(0, 1.5, cmap.N), 0., 1.)
    cmap_with_alpha = ListedColormap(cmap_with_alpha)

    # Plot the resulting image
    fig = plt.figure(figsize=(10, 10), constrained_layout=True)
    ax = fig.add_subplot(111, ymargin=-0.4)
    ax.imshow(background_image, extent=extent)
    cimg = ax.imshow(img_rotated, origin='lower', cmap=cmap_with_alpha, extent=outer_extent_xyz,
                     alpha=0.7, vmin=ground_vmin, vmax=ground_vmax)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.2, axes_class=maxes.Axes)
    cbar = fig.colorbar(cimg, cax=cax, orientation="vertical", format="%.1e")
    cbar.set_alpha(1.0)
    cbar.draw_all()
    # cbar.set_ticks([])

    ax.set_xlabel('$W-E$ (metres)', fontsize=14)
    ax.set_ylabel('$S-N$ (metres)', fontsize=14)

    ax.set_title(f"Near field image for {station_name}\nSB {subband} ({freq / 1e6:.1f} MHz), {str(obstime)[:16]}", fontsize=16)

    # Change limits to match the original specified extent in the localnorth frame
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.tick_params(axis='both', which='both', length=0)

    # Place the NSEW coordinate directions
    ax.text(0.95, 0.5, 'E', color='w', fontsize=18, transform=ax.transAxes, horizontalalignment='center', verticalalignment='center')
    ax.text(0.05, 0.5, 'W', color='w', fontsize=18, transform=ax.transAxes, horizontalalignment='center', verticalalignment='center')
    ax.text(0.5, 0.95, 'N', color='w', fontsize=18, transform=ax.transAxes, horizontalalignment='center', verticalalignment='center')
    ax.text(0.5, 0.05, 'S', color='w', fontsize=18, transform=ax.transAxes, horizontalalignment='center', verticalalignment='center')

    ground_vmin_img, ground_vmax_img = cimg.get_clim()
    ax.contour(img_rotated, np.linspace(ground_vmin_img, ground_vmax_img, 15), origin='lower', cmap=cm.Greys,
               extent=outer_extent_xyz, linewidths=0.5, alpha=0.7)
    ax.grid(True, alpha=0.3)
    plt.savefig(f"results/{fname}_nearfield_calibrated.png", bbox_inches='tight', dpi=200)
    plt.close(fig)

    plt.imsave(f"results/tmp.png", img_rotated,
               cmap=cmap_with_alpha, origin='lower', vmin=ground_vmin, vmax=ground_vmax)

    obstime = datetime.datetime.strptime(obsdatestr + ":" + obstimestr, '%Y%m%d:%H%M%S')

    tags = {"datafile": xst_filename,
            "generated_with": f"lofarimaging v{__version__}",
            "caltable": caltable_filename,
            "subband": subband,
            "frequency": freq,
            "extent_xyz": extent,
            "height": height,
            "outer_extent_xyz": list(outer_extent_xyz)}
    lofargeotiff.write_geotiff(img_rotated, f"results/{fname}_nearfield_calibrated.tiff",
                               (outer_pmin, outer_qmin), (outer_pmax, outer_qmax), stationname=station_name,
                               obsdate=obstime, tags=tags)

    m = folium.Map(location=[lat_center, lon_center], zoom_start=19,
                   tiles='http://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/MapServer/tile/{z}/{y}/{x}',
                   attr='ESRI')
    folium.TileLayer(tiles="OpenStreetMap").add_to(m)

    folium.raster_layers.ImageOverlay(
            name='Near field image',
            image=f"results/tmp.png",
            bounds=[[outer_lat_min, outer_lon_min], [outer_lat_max, outer_lon_max]],
            opacity=0.6,
            interactive=True,
            cross_origin=False,
            zindex=1
    ).add_to(m)

    folium.LayerControl().add_to(m)

    return m
