
angular.module('app', [])
    .service('MapService', function () {
        var map = L.map('mapid').setView([0.317, 32.580], 13);

        L.tileLayer('https://c.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            id: 'mapbox.streets',
        }).addTo(map);

        var wmsLayer = L.tileLayer.wms('http://shear.ncl.ac.uk:8080/geoserver/shear/wms', {
            layers: 'run657',
            format: 'image/png',
            transparent: true,
            viewparams: JSON.stringify({'run_id':624}),
            opacity: 0.5
        }).addTo(map);

        return {
            getMap: function () {return map},
            getWmsLayer: function () {return wmsLayer}
        }
    })

    .controller('RunController', function(MapService, $scope){

        this.runs = [
            {id: 648, amount: 20, duration: 60, green: false},
            {id: 649, amount: 20, duration: 180, green: false},
            {id: 650, amount: 20, duration: 360, green: false},
            {id: 651, amount: 40, duration: 60, green: false},
            {id: 652, amount: 40, duration: 180, green: false},
            {id: 653, amount: 40, duration: 360, green: false},
            {id: 654, amount: 60, duration: 60, green: false},
            {id: 655, amount: 60, duration: 180, green: false},
            {id: 656, amount: 60, duration: 360, green: false},
            {id: 657, amount: 80, duration: 60, green: false},
            {id: 658, amount: 80, duration: 180, green: false},
            {id: 659, amount: 80, duration: 360, green: false},
            {id: 660, amount: 100, duration: 60, green: false},
            {id: 661, amount: 100, duration: 180, green: false},
            {id: 662, amount: 100, duration: 360, green: false},

            {id: 684, amount: 20, duration: 60, green: true},
            {id: 685, amount: 20, duration: 180, green: true},
            {id: 686, amount: 20, duration: 360, green: true},
            {id: 687, amount: 40, duration: 60, green: true},
            {id: 688, amount: 40, duration: 180, green: true},
            {id: 689, amount: 40, duration: 360, green: true},
            {id: 690, amount: 60, duration: 60, green: true},
            {id: 691, amount: 60, duration: 180, green: true},
            {id: 692, amount: 60, duration: 360, green: true},
            {id: 693, amount: 80, duration: 60, green: true},
            {id: 694, amount: 80, duration: 180, green: true},
            {id: 695, amount: 80, duration: 360, green: true},
            {id: 696, amount: 100, duration: 60, green: true},
            {id: 697, amount: 100, duration: 180, green: true},
            {id: 698, amount: 100, duration: 360, green: true}
            ];

        this.durations = [60, 180, 360];
        this.amounts = [20, 40, 60, 80, 100];
        this.run = this.runs[0];

        this.wmsLayer = MapService.getWmsLayer();

        this.updateRun = function () {
            this.wmsLayer.setParams({layers: 'run' + String(this.run.id)});
            this.duration = this.durations.indexOf(this.run.duration);
            this.amount = this.amounts.indexOf(this.run.amount);

            console.log(this.duration)

        };

        this.findRun = function () {
            let amount = this.amounts[this.amount];
            let duration = this.durations[this.duration];
            for (var i=0; i < this.runs.length; i++) {
                let run = this.runs[i];
                if (run.amount === amount &&
                    run.duration === duration &&
                    run.green === this.green) {

                    console.log(amount);
                    console.log(duration);
                    console.log(run);
                    this.run = run;
                    break
                }
            }
            this.updateRun()
        };

        this.updateTime = function() {
            console.log(this.time)
        }

    });

