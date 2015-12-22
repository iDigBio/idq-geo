from idq.helpers import WorkflowBase, getfield

import decimal


def getExponent(fs):
    try:
        d = decimal.Decimal(fs)
        return -1 * d.as_tuple().exponent
    except:
        return 0


class Conversion(WorkflowBase):

    def __init__(self):
        super(Conversion, self).__init__()
        self.required_fields.extend(
            ["dwc:decimalLatitude", "dwc:decimalLongitude"])
        self.outputs.append("idigbio:geopoint")
        self.flags.extend([
            "idigbio_geopoint_preflip",
            "idigbio_geopoint_bounds",
            "idigbio_geopoint_lowprecision"
        ])

    def process(self, d):
        r = super(Conversion, self).process(d)

        lat_val = getfield("dwc:decimalLatitude", d)
        lon_val = getfield("dwc:decimalLongitude", d)

        if lat_val is not None and lon_val is not None:
            try:
                lat = float(lat_val)
                lon = float(lon_val)

                latexp = getExponent(lat_val)
                lonexp = getExponent(lon_val)

                if (
                    (-180 <= lat < -90 or 90 < lat <= 180) and
                    (-90 <= lon <= 90)
                ):
                    lat, lon = lon, lat
                    r["flags"].append("idigbio_geopoint_preflip")

                if not (-90 <= lat <= 90):
                    r["idigbio:geopoint"] = None
                    r["flags"].append("idigbio_geopoint_bounds")
                    return r

                if not (-180 <= lon <= 180):
                    r["idigbio:geopoint"] = None
                    r["flags"].append("idigbio_geopoint_bounds")
                    return r

                if latexp <= 2 or lonexp <= 2:
                    r["flags"].append("idigbio_geopoint_lowprecision")

                # set the geopoint to a lon,lat tuple
                r["idigbio:geopoint"] = (lon, lat)
            except:
                r["idigbio:geopoint"] = None
        else:
            r["idigbio:geopoint"] = None

        return r
