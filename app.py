import tornado.ioloop
import tornado.web
import os
import requests
import netCDF4 as nc

data_dir = '/mnt/shear/data/geoserver/data_dir/data/shear'
username = 'admin'
password = 'uR5Qq28iqSXDiMm'
workspace = 'shear'
geoserver = 'http://localhost:8080/geoserver/rest/'
style = 'citycat_output'


def make_app():
    return tornado.web.Application([
        (r'/test', Test),
        (r"/upload/(\d+)", Upload),
        (r"/(.*)", tornado.web.StaticFileHandler, {'path': 'site', 'default_filename': 'index.html'})
    ],
        debug=True)


class Test(tornado.web.RequestHandler):

    def post(self):
        print(self.request.body[:100])

# @tornado.web.stream_request_body
class Upload(tornado.web.RequestHandler):

    def post(self, run_id):

        file_name = 'run_{}.nc'.format(run_id)

        folder = os.path.join(data_dir, 'run{}'.format(run_id))
        if not os.path.exists(folder):
            os.mkdir(folder)

        file_path = os.path.join(folder, file_name)

        with open(file_path, 'wb') as f:
            f.write(self.request.body)

        ds = nc.Dataset(file_path)
        run_name = ds.run_name
        ds.close()

        layer_name = 'run{}'.format(run_id)
        requests.post(
            '{}workspaces/{}/coveragestores'.format(
                geoserver, workspace
            ),
            json={
                "coverageStore":
                    {
                        "name": layer_name,
                        "type": "NetCDF",
                        "enabled": True,
                        "workspace": {
                            "name": workspace
                        },
                        "url": file_path,
                    }
            }
            ,
            auth=(username, password))

        json = {
            "coverage": {
                "name": layer_name,
                "nativeName": layer_name,
                "namespace": {
                    "name": workspace
                },
                "title": run_name,
                "description": "",
                "metadata": {
                    "entry": [
                        {
                            "@key": "COVERAGE_VIEW",
                            "coverageView": {
                                "coverageBands": {
                                    "coverageBand": [
                                        {
                                            "inputCoverageBands": {
                                                "@class": "singleton-list",
                                                "inputCoverageBand": [
                                                    {
                                                        "coverageName": "depth"
                                                    }
                                                ]
                                            },
                                            "definition": "depth",
                                            "index": 0,
                                            "compositionType": "BAND_SELECT"
                                        },
                                        {
                                            "inputCoverageBands": {
                                                "@class": "singleton-list",
                                                "inputCoverageBand": [
                                                    {
                                                        "coverageName": "x_vel"
                                                    }
                                                ]
                                            },
                                            "definition": "x_vel",
                                            "index": 1,
                                            "compositionType": "BAND_SELECT"
                                        },
                                        {
                                            "inputCoverageBands": {
                                                "@class": "singleton-list",
                                                "inputCoverageBand": [
                                                    {
                                                        "coverageName": "y_vel"
                                                    }
                                                ]
                                            },
                                            "definition": "y_vel",
                                            "index": 2,
                                            "compositionType": "BAND_SELECT"
                                        }
                                    ]
                                },
                                "name": layer_name,
                                "envelopeCompositionType": "INTERSECTION",
                                "selectedResolution": "BEST",
                                "selectedResolutionIndex": -1
                            }
                        },
                        {
                            "@key": "time",
                            "dimensionInfo": {
                                "enabled": True,
                                "presentation": "LIST",
                                "units": "ISO8601",
                                "defaultValue": {
                                    "strategy": "MAXIMUM"
                                },
                                "nearestMatchEnabled": True
                            }
                        },
                    ]
                },
                "store": {
                    "@class": "coverageStore",
                    "name": "{}:{}".format(workspace, layer_name),
                },
                "dimensions": {
                    "coverageDimension": [
                        {
                            "name": "Depth",
                            "description": "GridSampleDimension[-Infinity,Infinity]",
                            "range": {
                                "min": "-inf",
                                "max": "inf"
                            },
                            "dimensionType": {
                                "name": "REAL_32BITS"
                            }
                        },
                        {
                            "name": "x_vel",
                            "description": "GridSampleDimension[-Infinity,Infinity]",
                            "range": {
                                "min": "-inf",
                                "max": "inf"
                            },
                            "dimensionType": {
                                "name": "REAL_32BITS"
                            }
                        },
                        {
                            "name": "y_vel",
                            "description": "GridSampleDimension[-Infinity,Infinity]",
                            "range": {
                                "min": "-inf",
                                "max": "inf"
                            },
                            "dimensionType": {
                                "name": "REAL_32BITS"
                            }
                        }
                    ]
                },

                "nativeCoverageName": layer_name
            }
        }


        requests.post("{}workspaces/{}/coveragestores/{}/coverages.json".format(
                    geoserver, workspace, layer_name),
                      json=json,
                      auth=('admin', 'uR5Qq28iqSXDiMm'),
                      headers={
                          'Content-type': 'application/json',
                          'Accept': 'text/plain'
                      })

        requests.put('{}layers/{}:{}'.format(geoserver, workspace, layer_name),
                     json={
                         "layer": {"defaultStyle":
                             {
                                 "name": "{}:{}".format(workspace, style),
                                 "workspace": workspace
                             }
                         }
                     },
                     auth=(username, password),
                     headers={
                         'Content-type': 'application/json',
                         'Accept': 'text/plain'
                     }
                     )



if __name__ == "__main__":
    app = make_app()
    app.listen(8888, max_buffer_size=10000000000, max_body_size=10000000000 )
    tornado.ioloop.IOLoop.current().start()
