"""WMM declination calculation and map figure generation."""

from __future__ import annotations


def utm2lonlat(Easting, Northing, utm_zone=18, northern_hemisphere=False):
    from pyproj import CRS, Transformer

    if northern_hemisphere:
        utm_crs = CRS(f"EPSG:326{utm_zone}")
    else:
        utm_crs = CRS(f"EPSG:327{utm_zone}")
    wgs84_crs = CRS("EPSG:4326")
    transformer = Transformer.from_crs(utm_crs, wgs84_crs, always_xy=True)
    lon, lat = transformer.transform(Easting, Northing)
    return lon, lat


def lonlat2utm(lon, lat):
    """Convert WGS84 latitude/longitude to UTM coordinates."""
    from pyproj import CRS, Transformer

    utm_zone = int((float(lon) + 180) / 6) + 1
    northern_hemisphere = float(lat) >= 0
    if northern_hemisphere:
        utm_crs = CRS(f"EPSG:326{utm_zone}")
    else:
        utm_crs = CRS(f"EPSG:327{utm_zone}")
    wgs84_crs = CRS("EPSG:4326")
    transformer = Transformer.from_crs(wgs84_crs, utm_crs, always_xy=True)
    easting, northing = transformer.transform(float(lon), float(lat))
    return easting, northing, utm_zone, northern_hemisphere


def _resolve_location(
    Easting=None,
    Northing=None,
    utm_zone=18,
    northern_hemisphere=False,
    lat=None,
    lon=None,
):
    if lat is not None and lon is not None:
        easting, northing, utm_zone, northern_hemisphere = lonlat2utm(lon, lat)
        return float(lon), float(lat), easting, northing, utm_zone, northern_hemisphere
    if Easting is None or Northing is None:
        raise ValueError("Provide UTM Easting/Northing or latitude and longitude.")
    lon, lat = utm2lonlat(
        Easting, Northing, utm_zone=utm_zone, northern_hemisphere=northern_hemisphere,
    )
    return lon, lat, Easting, Northing, utm_zone, northern_hemisphere


def calculate_declination(
    timestamp,
    Easting=None,
    Northing=None,
    utm_zone=18,
    northern_hemisphere=False,
    lat=None,
    lon=None,
):
    """
    Calculate magnetic declination for a datetime and location.
    Coordinates may be UTM or latitude/longitude.
    Returns lon, lat, declination, error, fig.
    """
    from pygeomag import GeoMag
    import pandas as pd

    lon, lat, Easting, Northing, utm_zone, northern_hemisphere = _resolve_location(
        Easting=Easting,
        Northing=Northing,
        utm_zone=utm_zone,
        northern_hemisphere=northern_hemisphere,
        lat=lat,
        lon=lon,
    )

    t = pd.Timestamp(timestamp)

    if t.year % 4 == 0:
        days_in_year = 366
    else:
        days_in_year = 365

    time = (
        t.year
        + (t.month - 1) / 12
        + (t.day - 1) / days_in_year
        + t.hour / (days_in_year * 24)
        + t.minute / (days_in_year * 24 * 60)
    )

    if time < 2025:
        geo_mag = GeoMag(coefficients_file="wmm/WMM_2020.COF")
        model = "WMM-2020"
    else:
        geo_mag = GeoMag(coefficients_file="wmm/WMM_2025.COF")
        model = "WMM-2025"

    result = geo_mag.calculate(glat=lat, glon=lon, alt=0, time=time)
    uncertainty = result.calculate_uncertainty()
    declination = result.d
    error = uncertainty.d

    fig = declination_image(
        t, declination, error, model, Easting, Northing, utm_zone, northern_hemisphere,
    )
    return lon, lat, declination, error, fig


def declination_image(
    t,
    declination,
    error,
    model,
    Easting,
    Northing,
    utm_zone=18,
    northern_hemisphere=False,
    H=5000,
    W=200,
    kilometers_covered=18,
):
    """Generate the declination map figure with compass overlay."""
    import math

    import cartopy.crs as ccrs
    import cartopy.io.img_tiles as cimgt
    import matplotlib.lines as mlines
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from pyproj import CRS, Proj, Transformer

    if northern_hemisphere:
        utm_crs = CRS(f"EPSG:326{utm_zone}")
        hemisphere = "north"
        southern_hemisphere = False
    else:
        utm_crs = CRS(f"EPSG:327{utm_zone}")
        hemisphere = "south"
        southern_hemisphere = True

    wgs84_crs = CRS("EPSG:4326")
    transformer = Transformer.from_crs(utm_crs, wgs84_crs, always_xy=True)
    lon, lat = transformer.transform(Easting, Northing)

    p = Proj(f"+proj=utm +zone={utm_zone} +{hemisphere} +datum=WGS84 +units=m")
    lon, lat = p(Easting, Northing, inverse=True)
    lonN, latN = p(Easting, Northing + H, inverse=True)
    EastingN, NorthingN = p(lon, latN)
    lonS, latS = p(Easting, Northing - H, inverse=True)
    EastingS, NorthingS = p(lon, latS)
    lonE, latE = p(Easting + H, Northing, inverse=True)
    EastingE, NorthingE = p(lonE, lat)
    lonW, latW = p(Easting - H, Northing, inverse=True)
    EastingW, NorthingW = p(lonW, lat)

    p = Proj(proj="utm", zone=utm_zone, ellps="WGS84")
    Easting, Northing = p(lon, lat)
    extent = kilometers_covered * 1000 / 2
    minE, maxE, minN, maxN = (
        Easting - extent * 0.8,
        Easting + extent * 0.8,
        Northing - extent,
        Northing + extent,
    )
    URL = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}.jpg"
    )
    request = cimgt.GoogleTiles(desired_tile_form="RGB", style="terrain", url=URL)
    proj = ccrs.UTM(utm_zone)
    proj2 = ccrs.UTM(utm_zone, southern_hemisphere)

    fig = plt.figure(figsize=(2.6, 3.5), facecolor="whitesmoke", layout="constrained")
    ax = plt.axes(projection=request.crs)
    ax.set_extent([minE, maxE, minN, maxN], crs=proj)
    ax.add_image(request, 13)

    props = dict(boxstyle="square", facecolor="lemonchiffon", ec="white", alpha=0.8)
    textstr = "\n".join((
        f"Model: {model}",
        r"Longitude: %2.4f" % lon,
        r"Latitude: %2.4f" % lat,
        f'Date: {pd.Timestamp(t).strftime("%Y-%m-%d")}',
        r"Declination: %2.2f" % declination,
        r"Uncertainty: ±%0.2f" % error,
    ))
    ax.text(
        0.03, 0.98, textstr, transform=ax.transAxes,
        fontsize="xx-small", va="top", bbox=props,
    )

    x_sign = [[-1, -1], [-1, -1], [1, -1], [1, -1]]
    y_sign = [[1, -1], [1, -1], [1, 1], [1, 1]]
    Xrotation = [
        W * math.cos(declination * (math.pi / 180)),
        H * math.sin(declination * (math.pi / 180)),
    ]
    Yrotation = [
        W * math.sin(declination * (math.pi / 180)),
        H * math.cos(declination * (math.pi / 180)),
    ]
    DX = np.multiply(x_sign, Xrotation)
    DY = np.multiply(y_sign, Yrotation)

    x1 = [Easting - DX[0, 0], Easting, Easting - DX[0, 1]]
    y1 = [Northing - DY[0, 0], Northing, Northing - DY[0, 1]]
    x2 = [Easting + DX[1, 0], Easting, Easting + DX[1, 1]]
    y2 = [Northing + DY[1, 0], Northing, Northing + DY[1, 1]]
    x3 = [Easting + DX[2, 0], Easting, Easting + DX[2, 1]]
    y3 = [Northing + DY[2, 0], Northing, Northing + DY[2, 1]]
    x4 = [Easting - DX[3, 0], Easting, Easting - DX[3, 1]]
    y4 = [Northing - DY[3, 0], Northing, Northing - DY[3, 1]]

    ax.add_line(mlines.Line2D(
        [EastingE, EastingW], [NorthingE, NorthingW],
        lw=1, color="k", alpha=0.5, transform=proj2, zorder=1,
    ))
    ax.add_line(mlines.Line2D(
        [EastingN, EastingS], np.column_stack([NorthingN, NorthingS]),
        lw=1, color="k", alpha=0.5, transform=proj2, zorder=1,
    ))
    ax.add_patch(mpatches.Wedge(
        [Easting, Northing], H, 0, 360, width=100, alpha=0.6,
        color="gainsboro", ec="k", transform=proj,
    ))
    ax.text(Easting - 300, Northing + H + 200, fontsize=14, s="N", color="k", transform=proj)
    ax.add_patch(mpatches.Polygon(
        np.column_stack([x2, y2]), color="gainsboro", ec="lightgray", transform=proj,
    ))
    ax.add_patch(mpatches.Polygon(
        np.column_stack([x3, y4]), color="silver", ec="darkgray", transform=proj,
    ))
    ax.add_patch(mpatches.Polygon(
        np.column_stack([x4, y3]), color="lightsalmon", ec="salmon", transform=proj,
    ))
    ax.add_patch(mpatches.Polygon(
        np.column_stack([x1, y1]), color="r", ec="crimson", transform=proj,
    ))
    ax.add_patch(mpatches.Circle(
        (Easting, Northing), 100, color="darkgray", ec="dimgray", transform=proj,
    ))

    return fig
