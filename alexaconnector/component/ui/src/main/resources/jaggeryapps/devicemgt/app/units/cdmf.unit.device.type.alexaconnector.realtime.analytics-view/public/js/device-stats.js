/*
 * Copyright (c) 2016, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
 *
 * WSO2 Inc. licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

var wsConnection1;
var graphForSensorType1;
var chartDataSensorType1 = [];
var chartDataSensorType2 = [];
var palette = new Rickshaw.Color.Palette();

function getTime() {
    var tNow = new Date().getTime() / 1000;
    return tNow;
}
function drawGraph(wsConnection, placeHolder, yAxis, chat, chartData,chartData2, graph) {
    tNow = getTime();
    for (var i = 0; i < 30; i++) {
        chartData.push({
            x: tNow - (30 - i) * 15,
            y: parseFloat(0)
        });
        chartData2.push({
            x: tNow - (30 - i) * 15,
            y: parseFloat(0)
        });
    }

    graph = new Rickshaw.Graph({
        element: document.getElementById(chat),
        width: $(placeHolder).width() - 50,
        height: 300,
        renderer: "line",
        interpolation: "linear",
        padding: {top: 0.2, left: 0.0, right: 0.0, bottom: 0.2},
        xScale: d3.time.scale(),
        series: [{
            'color': palette.color(),
            'data': chartData,
            'name': "Light"
        },
            {
                'color': palette.color(),
                'data': chartData2,
                'name': "Buzzer"
            }]
    });

    graph.render();

    var xAxis = new Rickshaw.Graph.Axis.Time({
        graph: graph
    });

    xAxis.render();

    new Rickshaw.Graph.Axis.Y({
        graph: graph,
        orientation: 'left',
        height: 300,
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
        element: document.getElementById(yAxis)
    });

    new Rickshaw.Graph.HoverDetail({
        graph: graph,
        formatter: function (series, x, y) {
            var date = '<span class="date">' + moment.unix(x).format('Do MMM YYYY h:mm:ss a') + '</span>';
            var swatch = '<span class="detail_swatch" style="background-color: ' + series.color + '"></span>';
            return swatch + series.name + ": " + parseInt(y) + '<br>' + date;
        }
    });
    var websocketurlStream = $(placeHolder).attr("data-websocketurlStream");
    connect(wsConnection, websocketurlStream, chartData,chartData2, graph);
}

$(window).load(function () {
    drawGraph(wsConnection1, "#div-chart-sensorType1", "yAxisSensorType1", "chartSensorType1", chartDataSensorType1,
        chartDataSensorType2, graphForSensorType1);

});

$(window).unload(function () {
    disconnect(wsConnection1);
});

//websocket connection
function connect(wsConnection, target, chartData,chartData2, graph) {
    if ('WebSocket' in window) {
        wsConnection = new WebSocket(target);
    } else if ('MozWebSocket' in window) {
        wsConnection = new MozWebSocket(target);
    } else {
        console.log('WebSocket is not supported by this browser.');
    }
    if (wsConnection) {
        var value1 = 0.0;
        var value2 = 1.0;
        var blCommand = null;
        var bzCommand;
        wsConnection.onmessage = function (event) {
            var dataPoint = JSON.parse(event.data);
            if (dataPoint[6] == "ON" && dataPoint[5] == "BULB") {

                if (blCommand != dataPoint[6]) {
                    chartData.push({
                        x: parseInt(dataPoint[4]),
                        y: parseFloat(value1)
                    });

                    chartData.shift();
                    graph.update();

                    chartData.push({
                        x: parseInt(dataPoint[4]),
                        y: parseFloat(value2)
                    });

                    chartData.shift();
                    graph.update();

                }
                blCommand = dataPoint[6];

            } else if(dataPoint[6] == "OFF" && dataPoint[5] == "BULB") {
                if (blCommand != dataPoint[6]) {
                    chartData.push({
                        x: parseInt(dataPoint[4]),
                        y: parseFloat(value2)
                    });

                    chartData.shift();
                    graph.update();

                    chartData.push({
                        x: parseInt(dataPoint[4]),
                        y: parseFloat(value1)
                    });

                    chartData.shift();
                    graph.update();

                }
                blCommand = dataPoint[6];
            }

            if (dataPoint[6] == "ON" && dataPoint[5] == "BUZZER") {

                if (bzCommand != dataPoint[6]) {

                    chartData2.push({
                        x: parseInt(dataPoint[4]),
                        y: parseFloat(value1)
                    });

                    chartData2.shift();
                    graph.update();

                    chartData2.push({
                        x: parseInt(dataPoint[4]),
                        y: parseFloat(value2)
                    });

                    chartData2.shift();
                    graph.update();

                }
                bzCommand = dataPoint[6];

            } else if(dataPoint[6] == "OFF" && dataPoint[5] == "BUZZER") {
                if (bzCommand != dataPoint[6]) {

                    chartData2.push({
                        x: parseInt(dataPoint[4]),
                        y: parseFloat(value2)
                    });

                    chartData2.shift();
                    graph.update();

                    chartData2.push({
                        x: parseInt(dataPoint[4]),
                        y: parseFloat(value1)
                    });

                    chartData2.shift();
                    graph.update();

                }
                bzCommand = dataPoint[6];
            }


        };
    }
}

function disconnect(wsConnection) {
    if (wsConnection != null) {
        wsConnection.close();
        wsConnection = null;
    }
}
