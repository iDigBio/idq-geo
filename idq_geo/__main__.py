from idq.harness import create_harness
from idq_geo import GeoWorkflow

def main():
    w = GeoWorkflow()
    app = create_harness(w)
    app.debug = True
    app.run()

if __name__ == '__main__':
    main()