from idq.helpers import WorkflowBase, filled, getfield
import re
import pyproj

mangler = re.compile("[\W]+")


def mangleString(s):
    return mangler.sub('', s).upper()


class Projection(WorkflowBase):

    def __init__(self):
        super(Projection, self).__init__()
        self.required_fields.extend(["idigbio:geopoint", "dwc:geodeticDatum"])
        self.outputs.append("idigbio:geopoint")
        self.flags.extend([
            "dwc_geodeticDatum_error",
            "dwc_geodeticDatum_missing",
        ])

    def process(self, d):
        r = super(Projection, self).process(d)

        datum_val = getfield("dwc:geodeticDatum", d)

        # if we got this far with actual values
        if filled("idigbio:geopoint", d):
            if datum_val is not None:
                # convert datum to a more canonical representation (no
                # whitespace, all uppercase)
                source_datum = mangleString(datum_val)
                try:
                    # source projection
                    p1 = pyproj.Proj(proj="latlon", datum=source_datum)

                    # destination projection
                    p2 = pyproj.Proj(proj="latlon", datum="WGS84")

                    # do the transform
                    # (lon, lat)
                    r["idigbio:geopoint"] = pyproj.transform(
                        p1, p2, d["idigbio:geopoint"][0], d["idigbio:geopoint"][1])
                except:
                    # traceback.print_exc()
                    # create an error flag on projection creation exception (invalid source datum)
                    # or on transform exception (point out of bounds for source
                    # projection)
                    r["flags"].append("dwc_geodeticDatum_error")
            else:
                # note unprojected points (datum_val is None)
                r["flags"].append("dwc_geodeticDatum_missing")

        return r
