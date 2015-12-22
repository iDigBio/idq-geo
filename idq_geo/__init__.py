from idq.harness import create_harness
from idq.helpers import WorkflowBase, CombinedWorkflow, filled, field_to_flag

from projection import Projection
from convert import Conversion
from reverse_geocode import ReverseGeocode

class GeoWorkflow(CombinedWorkflow):
    def __init__(self):
        super(GeoWorkflow,self).__init__([
            Conversion(),
            Projection(),
            ReverseGeocode()
        ])

    def process(self,d):
        r = super(GeoWorkflow,self).process(d)
        print r
        return r

def main():
    w = GeoWorkflow()
    app = create_harness(w)
    app.debug = True
    app.run()

if __name__ == '__main__':
    main()