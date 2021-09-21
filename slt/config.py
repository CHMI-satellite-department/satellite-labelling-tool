import os
from pathlib import Path
import plotly.express as px

from satdl import utils

DEBUG = True

_base_path = Path(__file__).parent
_assets_path = _base_path / 'assets'

annotation_types = [
    "Overshooting top",
    "Above anvil plume",
    "Cold U/V",
    "Cold ring",
]
DEFAULT_ATYPE = annotation_types[0]

columns = ["label", "annotator", "XREF", "YREF",
           dict(id="X0", name='X0', type='numeric', format=dict(specifier='.2f')),
           dict(id="Y0", name='Y0', type='numeric', format=dict(specifier='.2f')),
           dict(id="X1", name='X1', type='numeric', format=dict(specifier='.2f')),
           dict(id="Y1", name='Y1', type='numeric', format=dict(specifier='.2f')),
           dict(id="Xcenter", name='<X>', type='numeric', format=dict(specifier='.2f')),
           dict(id="Ycenter", name='<Y>', type='numeric', format=dict(specifier='.2f')),
           dict(id="lon0", name='lon0', type='numeric', format=dict(specifier='.3f')),
           dict(id="lat0", name='lat0', type='numeric', format=dict(specifier='.3f')),
           dict(id="lon1", name='lon1', type='numeric', format=dict(specifier='.3f')),
           dict(id="lat1", name='lat1', type='numeric', format=dict(specifier='.3f')),
           dict(id="lon_center", name='<lon>', type='numeric', format=dict(specifier='.3f')),
           dict(id="lat_center", name='<lat>', type='numeric', format=dict(specifier='.3f'))]

SHAPE_PRECISION = 2  # precision for comparison of corners of two shapes

download_columns = ['annotator', 'label', 'x0', 'y0', 'x1', 'y1', 'lat0', 'lat1',
                    'lon0', 'lon1', 'x_center', 'y_center',
                    'lat_center', 'lon_center']

_data_path = _base_path / 'examples' / 'images'
_data_path = Path(os.environ.get('SLT_DATA_PATH', _data_path))
if not _data_path.exists():
    raise ValueError(f'data path {_data_path} does not exist')

_geo_path = _base_path / 'examples' / 'images' / '201911271130_MSG4_msgce_1160x800_geotiff_hrv.tif'
_geo_path = Path(os.environ.get('SLT_GEO_PATH', _geo_path))
if not _geo_path.exists():
    raise ValueError(f'data path {_data_path} does not exist')

_georef = utils.image2xr(_geo_path)
_projection = _georef.attrs.get('crs', '')

_image_file_mask = '{projection}-{resolution}.{product}.{datetime:%Y%m%d.%H%M}.0.jpg'
_image_file_mask = os.environ.get('SLT_DATA_FILENAME_MASK', _image_file_mask)

NUM_ATYPES = 15
DEFAULT_FIG_MODE = "layout"
annotation_colormap = px.colors.qualitative.Light24

# prepare bijective type<->color mapping
typ_col_pairs = [
    (t, annotation_colormap[n % len(annotation_colormap)])
    for n, t in enumerate(annotation_types)
]
# types to colors
color_dict = {}
# colors to types
type_dict = {}
for typ, col in typ_col_pairs:
    color_dict[typ] = col
    type_dict[col] = typ

options = list(color_dict.keys())
