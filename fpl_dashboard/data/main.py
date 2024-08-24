
import typing
from tqdm import tqdm
from fpl_dashboard.data.database_model import *
from fpl_dashboard.data.fpl_api_handler import *

if typing.TYPE_CHECKING:
    from .database_model import *
    from .fpl_api_handler import *
