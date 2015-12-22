from idq.helpers import WorkflowBase, getfield, filled

from rg import ReverseGeocoder

rg = ReverseGeocoder()
rg_eez = ReverseGeocoder(shapefile="data/EEZ_land_v2_201410.shp", cc_key="ISO_3digit")

import decimal


def getExponent(fs):
    try:
        d = decimal.Decimal(fs)
        return -1 * d.as_tuple().exponent
    except:
        return 0


class ReverseGeocode(WorkflowBase):

    def __init__(self):
        super(ReverseGeocode, self).__init__()
        self.required_fields.extend(
            ["idigbio:geopoint", "idigbio:isocountrycode"])
        self.outputs.append("idigbio:geopoint")
        self.flags.extend([
            "idigbio_geopoint_eez",
            "idigbio_geopoint_revfailure",
            "idigbio_geopoint_revmismatch",
            "idigbio_geopoint_lonsign",
            "idigbio_geopoint_latsign",
            "idigbio_geopoint_bothsign",
            "idigbio_geopoint_flip",
            "idigbio_geopoint_fliplatsign",
            "idigbio_geopoint_fliplonsign",
            "idigbio_geopoint_flipbothsign",
            "idigbio_geopoint_eezcorrected",
            "idigbio_geopoint_corrected"
        ])

    def process(self, d):
        r = super(ReverseGeocode, self).process(d)

        if filled("idigbio:geopoint", d):
            r["idigbio:geopoint"] = d["idigbio:geopoint"]
            result = rg.get_country(d["idigbio:geopoint"][0], d[
                                    "idigbio:geopoint"][1])
            if result is None:
                result_eez = rg_eez.get_country(
                    d["idigbio:geopoint"][0], d["idigbio:geopoint"][1])
                if result_eez is not None:
                    result = result_eez
                    r["flags"].append("idigbio_geopoint_eez")

            test_flips = False
            if result is None:
                r["flags"].append("idigbio_geopoint_revfailure")
                test_flips = True

            elif filled("idigbio:isocountrycode", d) and result.lower() != d["idigbio:isocountrycode"].lower():
                r["flags"].append("idigbio_geopoint_revmismatch")
                test_flips = True

            if filled("idigbio:isocountrycode", d) and test_flips:
                r["flags"].append("idigbio_geopoint_revmismatch")
                flip_queries = [  # Point, "Distance" from original coords, Flag
                    [(-d["idigbio:geopoint"][0], d["idigbio:geopoint"][1]),
                     1, "idigbio_geopoint_revlonsign"],
                    [(d["idigbio:geopoint"][0], -d["idigbio:geopoint"][1]),
                     1, "idigbio_geopoint_revlatsign"],
                    [(-d["idigbio:geopoint"][0], -d["idigbio:geopoint"][1]),
                     2, "idigbio_geopoint_revbothsign"],
                ]
                if abs(d["idigbio:geopoint"][0]) <= 90.0:
                    flip_queries.extend([
                        [(d["idigbio:geopoint"][1], d["idigbio:geopoint"][0]),
                         2, "idigbio_geopoint_revflip"],
                        [(-d["idigbio:geopoint"][1], d["idigbio:geopoint"][0]),
                         3, "idigbio_geopoint_revfliplatsign"],
                        [(d["idigbio:geopoint"][1], -d["idigbio:geopoint"][0]),
                         3, "idigbio_geopoint_revfliplonsign"],
                        [(-d["idigbio:geopoint"][1], -d["idigbio:geopoint"][0]),
                         4, "idigbio_geopoint_revflipbothsign"]
                    ])
                for i, f in enumerate([rg.get_country(*f[0]) for f in flip_queries] + [rg_eez.get_country(*f[0]) for f in flip_queries]):
                    if f is not None and f.lower() == d["idigbio:isocountrycode"].lower():
                        # Flip back to lon, lat
                        real_i = i % len(flip_queries)
                        r["idigbio:geopoint"] = (
                            flip_queries[real_i][0][0], flip_queries[real_i][0][1])
                        # Set flag
                        r["flags"].append(flip_queries[real_i][2])
                        if real_i != i:
                            r["flags"].append("idigbio_geopoint_reveezcorrected")
                        r["flags"].append("idigbio_geopoint_revcorrected")
                        break

        return r
