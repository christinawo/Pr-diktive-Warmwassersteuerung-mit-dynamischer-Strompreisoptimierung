from data.params import PARAMS, BOILER_SIZES

def create_size_params(volume_liters):
    params = PARAMS.copy()
    params.update(BOILER_SIZES[volume_liters])

    return params